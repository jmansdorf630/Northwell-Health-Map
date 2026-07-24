from __future__ import annotations

import base64
import csv
import io
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from streamlit_folium import st_folium

from data import DATA_LAST_UPDATED, HOSPITALS
from map_utils import (
    BADGE_BG,
    MAP_HEIGHT,
    REGION_COLORS,
    build_map,
    coverage_matrix,
    service_count,
)

st.set_page_config(
    page_title="Northwell Telehealth Footprint",
    page_icon="🏥",
    layout="wide",
)

ASSET_DIR = Path(__file__).resolve().parent / "assets"
LOGO_PATH = ASSET_DIR / "northwell_logo.png"


@st.cache_data
def _logo_data_uri() -> str | None:
    """Embed the sidebar logo as a data URI so Cloud deploys resolve reliably."""
    if not LOGO_PATH.exists():
        return None
    encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


@st.cache_data
def all_regions() -> list[str]:
    return sorted({h["region"] for h in HOSPITALS})


@st.cache_data
def all_services() -> list[str]:
    return sorted({s for h in HOSPITALS for s in h["services"] if s != "TBD"})


@st.cache_data
def hospitals_by_name() -> dict[str, dict]:
    return {h["name"]: h for h in HOSPITALS}


st.markdown(
    """
<style>
    .main .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    .stMultiSelect [data-baseweb="tag"] { background-color: #185FA5; }
    h1 { font-size: 1.6rem; font-weight: 600; }
    .metric-card {
        background: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 0.75rem 1rem;
        text-align: center;
    }
    .metric-card .num { font-size: 1.6rem; font-weight: 700; color: #185FA5; }
    .metric-card .label { font-size: 0.78rem; color: #555; margin-top: 2px; }
    .tag {
        display: inline-block;
        background: #e8f0fb;
        color: #185FA5;
        border-radius: 20px;
        padding: 3px 10px;
        font-size: 0.78rem;
        margin: 2px;
    }
    .tag-tbd {
        background: #f0f0f0;
        color: #888;
    }
    .hospital-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem 1.1rem;
        margin-bottom: 0.6rem;
    }
    .hospital-card.selected {
        border: 2px solid #185FA5;
        box-shadow: 0 0 0 3px rgba(24, 95, 165, 0.15);
    }
    .hospital-card h4 { margin: 0 0 6px 0; font-size: 0.95rem; color: #1a1a1a; }
    .region-badge {
        display: inline-block;
        font-size: 0.7rem;
        padding: 2px 8px;
        border-radius: 20px;
        margin-bottom: 8px;
        font-weight: 600;
    }
    .updated-caption { color: #666; font-size: 0.85rem; margin-top: -0.4rem; }
</style>
""",
    unsafe_allow_html=True,
)


def _init_state() -> None:
    defaults = {
        "selected_hospital": None,
        "focus_hospital": None,
        "map_click_sig": None,
        "filter_sig": None,
        "regions": all_regions(),
        "services": [],
        "service_match": "all",
        "search": "",
        "sort_by": "Region, then name",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _reset_filters() -> None:
    st.session_state.regions = all_regions()
    st.session_state.services = []
    st.session_state.service_match = "all"
    st.session_state.search = ""
    st.session_state.sort_by = "Region, then name"
    st.session_state.selected_hospital = None
    st.session_state.focus_hospital = None


def _request_filter_reset() -> None:
    """Queue a filter reset for the start of the next run (widget-safe)."""
    st.session_state._pending_filter_reset = True


def _apply_pending_filter_reset() -> None:
    if st.session_state.pop("_pending_filter_reset", False):
        _reset_filters()


def _filter_fingerprint(
    regions: list[str],
    services: list[str],
    match_mode: str,
    search: str,
) -> tuple:
    return (tuple(sorted(regions)), tuple(sorted(services)), match_mode, search.strip().lower())


def filter_hospitals(
    regions: list[str],
    services: list[str],
    match_mode: str,
    search: str,
) -> list[dict]:
    query = search.strip().lower()
    filtered = [h for h in HOSPITALS if h["region"] in regions]
    if query:
        filtered = [h for h in filtered if query in h["name"].lower()]
    if services:
        if match_mode == "all":
            filtered = [
                h for h in filtered if all(s in h["services"] for s in services)
            ]
        else:
            filtered = [
                h for h in filtered if any(s in h["services"] for s in services)
            ]
    return filtered


def sort_hospitals(hospitals: list[dict], sort_by: str) -> list[dict]:
    if sort_by == "Name":
        return sorted(hospitals, key=lambda h: h["name"].lower())
    if sort_by == "Region":
        return sorted(hospitals, key=lambda h: (h["region"].lower(), h["name"].lower()))
    if sort_by == "Number of services":
        return sorted(
            hospitals,
            key=lambda h: (-service_count(h), h["name"].lower()),
        )
    # Default: region then name
    return sorted(hospitals, key=lambda h: (h["region"].lower(), h["name"].lower()))


def filtered_to_csv(hospitals: list[dict]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["name", "region", "lat", "lng", "services", "service_count"])
    for h in hospitals:
        services = "" if h["services"] == ["TBD"] else "; ".join(h["services"])
        writer.writerow(
            [h["name"], h["region"], h["lat"], h["lng"], services, service_count(h)]
        )
    return buf.getvalue()


def render_hospital_list(hospitals: list[dict], selected_name: str | None) -> None:
    st.markdown("**Hospitals**")
    if not hospitals:
        st.info("No hospitals match the current filters.")
        return

    with st.container(height=MAP_HEIGHT):
        for h in hospitals:
            badge_bg = BADGE_BG.get(h["region"], "#eee")
            badge_fg = REGION_COLORS.get(h["region"], "#333")
            tbd = h["services"] == ["TBD"]
            selected = h["name"] == selected_name
            card_class = "hospital-card selected" if selected else "hospital-card"
            anchor = "hospital-" + "".join(ch if ch.isalnum() else "-" for ch in h["name"]).strip("-").lower()

            preview = h["services"][:6]
            tags = "".join(
                f'<span class="tag{"" if not tbd else " tag-tbd"}">{s}</span>'
                for s in preview
            )

            st.markdown(
                f"""
                <div id="{anchor}" class="{card_class}">
                    <span class="region-badge" style="background:{badge_bg};color:{badge_fg};">{h['region']}</span>
                    <h4>{h['name']}</h4>
                    <div>{tags}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Single overflow control: expander with the full service list.
            if not tbd and len(h["services"]) > 6:
                with st.expander(f"All {len(h['services'])} services", expanded=False):
                    st.write(", ".join(h["services"]))
            elif tbd:
                st.caption("Programs TBD")

            if st.button(
                "Show on map",
                key=f"focus_{h['name']}",
                use_container_width=True,
            ):
                st.session_state.selected_hospital = h["name"]
                st.session_state.focus_hospital = h["name"]
                st.rerun()

    if selected_name:
        anchor = "hospital-" + "".join(
            ch if ch.isalnum() else "-" for ch in selected_name
        ).strip("-").lower()
        components.html(
            f"""
            <script>
            const doc = window.parent.document;
            const el = doc.getElementById("{anchor}");
            if (el) {{
                el.scrollIntoView({{behavior: "smooth", block: "nearest"}});
            }}
            </script>
            """,
            height=0,
        )


def render_map_tab(hospitals: list[dict]) -> None:
    selected = st.session_state.selected_hospital
    focus = st.session_state.focus_hospital

    map_col, list_col = st.columns([3, 1.1])
    with map_col:
        m = build_map(hospitals, selected_name=selected, focus_name=focus)
        center = None
        zoom = None
        if focus and focus in hospitals_by_name():
            h = hospitals_by_name()[focus]
            center = [h["lat"], h["lng"]]
            zoom = 12

        map_state = st_folium(
            m,
            height=MAP_HEIGHT,
            use_container_width=True,
            center=center,
            zoom=zoom,
            key="telehealth_map",
            returned_objects=["last_object_clicked", "last_object_clicked_tooltip"],
        )

        tooltip = (map_state or {}).get("last_object_clicked_tooltip")
        clicked = (map_state or {}).get("last_object_clicked")
        click_sig = (tooltip, tuple(sorted((clicked or {}).items())) if clicked else None)
        if tooltip and click_sig != st.session_state.map_click_sig:
            st.session_state.map_click_sig = click_sig
            if tooltip in hospitals_by_name():
                st.session_state.selected_hospital = tooltip
                st.session_state.focus_hospital = None
                st.rerun()

        # Consume one-shot map focus after render so later filter edits
        # don't keep re-centering.
        if focus:
            st.session_state.focus_hospital = None

    with list_col:
        render_hospital_list(hospitals, selected)


def render_coverage_tab(hospitals: list[dict]) -> None:
    st.caption(
        "Hospital × service coverage for the current filters. "
        "Columns are ordered by how many hospitals offer each service."
    )
    df = coverage_matrix(hospitals)

    def _style_cells(val):
        if val == "●":
            return "background-color: #e8f0fb; color: #185FA5; text-align: center; font-weight: 700;"
        if val == "" or val is None:
            return "background-color: #fafafa; color: #ccc; text-align: center;"
        return ""

    service_cols = [c for c in df.columns if c not in ("Hospital", "Total")]
    styler = (
        df.style.map(_style_cells, subset=service_cols)
        .set_properties(**{"font-size": "0.8rem"})
    )
    st.dataframe(styler, width="stretch", height=560)


def main() -> None:
    _init_state()
    _apply_pending_filter_reset()

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        logo_uri = _logo_data_uri()
        if logo_uri:
            st.markdown(
                f'<img src="{logo_uri}" alt="Northwell Health" width="180" />',
                unsafe_allow_html=True,
            )
        elif LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=180)
        else:
            st.markdown("### Northwell Health")

        st.markdown("---")
        st.markdown("### Filters")

        st.text_input(
            "Search hospitals",
            key="search",
            placeholder="Type a hospital name…",
        )

        st.multiselect(
            "Region",
            options=all_regions(),
            key="regions",
        )

        st.multiselect(
            "Filter by service",
            options=all_services(),
            key="services",
        )

        st.radio(
            "Match",
            options=["all", "any"],
            format_func=lambda m: (
                "has all selected services"
                if m == "all"
                else "has any selected service"
            ),
            key="service_match",
            horizontal=False,
        )

        st.selectbox(
            "Sort hospitals",
            options=[
                "Region, then name",
                "Name",
                "Region",
                "Number of services",
            ],
            key="sort_by",
        )

        st.markdown("---")
        st.markdown("### About")
        st.caption(
            "Northwell Health hospital-based telehealth footprint across all regions. "
            "Hover over pins for details."
        )

    regions = st.session_state.regions
    services = st.session_state.services
    match_mode = st.session_state.service_match
    search = st.session_state.search
    sort_by = st.session_state.sort_by

    filtered = sort_hospitals(
        filter_hospitals(regions, services, match_mode, search),
        sort_by,
    )

    # Clear selection when filters hide the selected hospital.
    sig = _filter_fingerprint(regions, services, match_mode, search)
    if st.session_state.filter_sig != sig:
        st.session_state.filter_sig = sig
        selected = st.session_state.selected_hospital
        if selected and selected not in {h["name"] for h in filtered}:
            st.session_state.selected_hospital = None
            st.session_state.focus_hospital = None

    # ── Header + metrics ─────────────────────────────────────────────────────
    st.markdown("## 🏥 Northwell Health — Telehealth Footprint")
    try:
        updated = datetime.strptime(DATA_LAST_UPDATED, "%Y-%m-%d").strftime("%b %d, %Y")
    except ValueError:
        updated = DATA_LAST_UPDATED
    st.markdown(
        f'<p class="updated-caption">Data last updated: {updated}</p>',
        unsafe_allow_html=True,
    )

    total_hospitals = len(filtered)
    total_services = len(
        {s for h in filtered for s in h["services"] if s != "TBD"}
    )
    active_regions = len({h["region"] for h in filtered})
    fully_active = len([h for h in filtered if "TBD" not in h["services"]])

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(
        f"""
        <div class="metric-card">
            <div class="num">{total_hospitals}</div>
            <div class="label">Hospitals shown</div>
        </div>""",
        unsafe_allow_html=True,
    )
    c2.markdown(
        f"""
        <div class="metric-card">
            <div class="num">{total_services}</div>
            <div class="label">Unique services</div>
        </div>""",
        unsafe_allow_html=True,
    )
    c3.markdown(
        f"""
        <div class="metric-card">
            <div class="num">{active_regions}</div>
            <div class="label">Regions</div>
        </div>""",
        unsafe_allow_html=True,
    )
    c4.markdown(
        f"""
        <div class="metric-card" title="Hospitals whose service list does not include TBD (service programs are defined).">
            <div class="num">{fully_active}</div>
            <div class="label">Fully active ⓘ</div>
        </div>""",
        unsafe_allow_html=True,
    )

    st.download_button(
        "Download filtered data (CSV)",
        data=filtered_to_csv(filtered),
        file_name="northwell_telehealth_filtered.csv",
        mime="text/csv",
        disabled=not filtered,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if not filtered:
        st.warning("No hospitals match the current filters.")
        if st.button(
            "Reset filters",
            type="primary",
            on_click=_request_filter_reset,
        ):
            st.rerun()
        return

    map_tab, matrix_tab = st.tabs(["Map", "Coverage Matrix"])
    with map_tab:
        render_map_tab(filtered)
    with matrix_tab:
        render_coverage_tab(filtered)


main()
