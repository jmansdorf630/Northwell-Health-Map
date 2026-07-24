"""Map and coverage-matrix helpers for the telehealth footprint app."""

from __future__ import annotations

import folium
from folium.plugins import MarkerCluster

REGION_COLORS = {
    "Western": "#185FA5",
    "Central": "#0F6E56",
    "Eastern": "#854F0B",
    "Nuvance": "#6b6b6b",
    "External": "#993C1D",
}

REGION_HEX = {
    "Western": "#185FA5",
    "Central": "#1D9E75",
    "Eastern": "#EF9F27",
    "Nuvance": "#888780",
    "External": "#D85A30",
}

BADGE_BG = {
    "Western": "#e8f0fb",
    "Central": "#e1f5ee",
    "Eastern": "#faeeda",
    "Nuvance": "#f1efe8",
    "External": "#faece7",
}

REGION_GLYPH = {
    "Western": "W",
    "Central": "C",
    "Eastern": "E",
    "Nuvance": "N",
    "External": "X",
}

MAP_HEIGHT = 520
DEFAULT_CENTER = [40.85, -73.6]
DEFAULT_ZOOM = 9


def service_count(hospital: dict) -> int:
    if hospital["services"] == ["TBD"]:
        return 0
    return len([s for s in hospital["services"] if s != "TBD"])


def marker_radius(hospital: dict, *, min_r: int = 8, max_r: int = 18) -> int:
    """Scale marker radius by service count within a readable min/max."""
    count = service_count(hospital)
    if count <= 0:
        return min_r
    # Observed max in data is ~20 services; clamp for readability.
    t = min(count, 20) / 20
    return int(round(min_r + t * (max_r - min_r)))


def _popup_html(hospital: dict) -> str:
    tbd = hospital["services"] == ["TBD"]
    if tbd:
        services_html = '<span style="color:#888;font-size:12px;">Programs TBD</span>'
    else:
        services_html = "".join(
            f'<span style="display:inline-block;background:#e8f0fb;color:#185FA5;'
            f'border-radius:20px;padding:2px 9px;font-size:11px;margin:2px;">{s}</span>'
            for s in hospital["services"]
        )
    return f"""
    <div style="font-family:sans-serif;min-width:220px;max-width:280px;">
        <div style="font-weight:700;font-size:14px;margin-bottom:6px;color:#1a1a1a;">{hospital['name']}</div>
        <div style="font-size:11px;color:#666;margin-bottom:8px;font-weight:600;text-transform:uppercase;
            letter-spacing:0.05em;">{hospital['region']} Region</div>
        <div style="border-top:1px solid #eee;padding-top:8px;">{services_html}</div>
    </div>
    """


def _div_icon(hospital: dict, *, selected: bool = False) -> folium.DivIcon:
    color = REGION_HEX.get(hospital["region"], "#333")
    glyph = REGION_GLYPH.get(hospital["region"], "?")
    tbd = hospital["services"] == ["TBD"]
    radius = marker_radius(hospital)
    size = radius * 2
    opacity = 0.55 if tbd else 0.95
    ring = "#185FA5" if selected else "white"
    ring_w = 3 if selected else 2
    return folium.DivIcon(
        icon_size=(size, size),
        icon_anchor=(radius, radius),
        html=f"""
        <div style="
            width:{size}px;height:{size}px;border-radius:50%;
            background:{color};opacity:{opacity};
            border:{ring_w}px solid {ring};
            display:flex;align-items:center;justify-content:center;
            color:white;font-weight:700;font-size:{max(9, radius - 2)}px;
            font-family:Helvetica,Arial,sans-serif;
            box-shadow:0 1px 3px rgba(0,0,0,0.25);
            line-height:1;
        ">{glyph}</div>
        """,
    )


def _legend_html() -> str:
    rows = ""
    for region, color in REGION_HEX.items():
        glyph = REGION_GLYPH[region]
        rows += f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
            <div style="width:18px;height:18px;border-radius:50%;background:{color};
                color:white;font-size:10px;font-weight:700;display:flex;align-items:center;
                justify-content:center;flex-shrink:0;border:2px solid white;
                box-shadow:0 0 0 1px #ccc;">{glyph}</div>
            <span>{region}</span>
        </div>"""
    return f"""
    <div style="position:fixed;bottom:30px;left:30px;z-index:1000;
        background:white;padding:12px 16px;border-radius:10px;
        border:1px solid #ddd;font-family:sans-serif;font-size:12px;">
        <div style="font-weight:700;margin-bottom:8px;">Region</div>
        {rows}
        <div style="margin-top:8px;color:#666;font-size:11px;">Marker size ∝ service count</div>
    </div>
    """


def build_map(
    hospitals: list[dict],
    *,
    selected_name: str | None = None,
    focus_name: str | None = None,
) -> folium.Map:
    """Build a clustered Folium map fitted to the given hospitals."""
    m = folium.Map(
        location=DEFAULT_CENTER,
        zoom_start=DEFAULT_ZOOM,
        tiles="CartoDB positron",
        control_scale=True,
    )

    if not hospitals:
        m.get_root().html.add_child(folium.Element(_legend_html()))
        return m

    cluster = MarkerCluster(name="Hospitals", showCoverageOnHover=False).add_to(m)

    for h in hospitals:
        is_selected = h["name"] == selected_name
        open_popup = h["name"] == focus_name or (focus_name is None and is_selected)
        folium.Marker(
            location=[h["lat"], h["lng"]],
            popup=folium.Popup(_popup_html(h), max_width=300, show=open_popup),
            tooltip=h["name"],
            icon=_div_icon(h, selected=is_selected),
        ).add_to(cluster)

    if len(hospitals) == 1:
        h = hospitals[0]
        m.location = [h["lat"], h["lng"]]
        m.options["zoom"] = 12
    else:
        lats = [h["lat"] for h in hospitals]
        lngs = [h["lng"] for h in hospitals]
        # Small pad so edge markers aren't flush with the frame.
        pad_lat = max(0.05, (max(lats) - min(lats)) * 0.08)
        pad_lng = max(0.05, (max(lngs) - min(lngs)) * 0.08)
        m.fit_bounds(
            [
                [min(lats) - pad_lat, min(lngs) - pad_lng],
                [max(lats) + pad_lat, max(lngs) + pad_lng],
            ]
        )

    m.get_root().html.add_child(folium.Element(_legend_html()))
    return m


def coverage_matrix(hospitals: list[dict]):
    """Return a hospital × service DataFrame with row/column totals.

    Columns (except Hospital / Total) are ordered by how many hospitals
    offer that service (descending), then by name.
    """
    import pandas as pd

    services = sorted(
        {s for h in hospitals for s in h["services"] if s != "TBD"}
    )
    if not hospitals:
        return pd.DataFrame(columns=["Hospital", "Total"])

    rows = []
    for h in hospitals:
        offered = set(h["services"])
        row = {"Hospital": h["name"]}
        for s in services:
            row[s] = "●" if s in offered else ""
        row["Total"] = sum(1 for s in services if s in offered)
        rows.append(row)

    df = pd.DataFrame(rows)
    # Column order: Hospital, services by coverage count desc, Total
    coverage_counts = {
        s: int((df[s] == "●").sum()) if s in df.columns else 0 for s in services
    }
    ordered = sorted(services, key=lambda s: (-coverage_counts[s], s))
    df = df[["Hospital", *ordered, "Total"]]

    # Column totals as a footer row — keep service cells as strings so Arrow
    # serialization stays homogeneous (● / "" / "12").
    totals = {"Hospital": "TOTAL"}
    for s in ordered:
        totals[s] = str(int((df[s] == "●").sum()))
    totals["Total"] = int(df["Total"].sum())
    df = pd.concat([df, pd.DataFrame([totals])], ignore_index=True)
    return df
