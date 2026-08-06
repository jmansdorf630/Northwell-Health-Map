from __future__ import annotations

import base64
import csv
import io
from datetime import datetime
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

st.markdown(
    """
<style>
    .main .block-container { padding-top: 1.25rem; padding-bottom: 1rem; max-width: 1400px; }
    .stMultiSelect [data-baseweb="tag"] { background-color: #185FA5; }
    div[data-testid="stMetricValue"] { font-size: 1.55rem; color: #185FA5; }
    div[data-testid="stMetricLabel"] { font-size: 0.8rem; }
    .hospital-card {
        background: #fff;
        border: 1px solid #e8e8e8;
        border-radius: 8px;
        padding: 0.7rem 0.85rem;
        margin-bottom: 0.35rem;
    }
    .hospital-card.selected {
        border: 2px solid #185FA5;
        box-shadow: 0 0 0 3px rgba(24, 95, 165, 0.12);
    }
    .hospital-card h4 {
        margin: 0 0 2px 0;
        font-size: 0.9rem;
        color: #1a1a1a;
        font-weight: 600;
    }
    .hospital-card .meta {
        font-size: 0.75rem;
        color: #666;
        margin: 0;
    }
    .region-badge {
        display: inline-block;
        font-size: 0.65rem;
        padding: 1px 7px;
        border-radius: 12px;
        margin-bottom: 4px;
        font-weight: 600;
    }
    .updated-caption { color: #777; font-size: 0.82rem; margin: 0.15rem 0 0.75rem 0; }
    section[data-testid="stSidebar"] .block-container { padding-top: 1.25rem; }
    /* Tighten metric row */
    div[data-testid="stMetric"] {
        background: #f8f9fa;
        border: 1px solid #eee;
        border-radius: 8px;
        padding: 0.55rem 0.75rem;
    }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def _logo_data_uri() -> str | None:
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


@st.cache_data
def _cached_coverage(names: tuple[str, ...]):
    by_name = hospitals_by_name()
    return coverage_matrix([by_name[n] for n in names if n in by_name])


@st.cache_data
def _cached_csv(names: tuple[str, ...]) -> str:
    by_name = hospitals_by_name()
    hospitals = [by_name[n] for n in names if n in by_name]
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["name", "region", "lat", "lng", "services", "service_count"])
    for h in hospitals:
        services = "" if h["services"] == ["TBD"] else "; ".join(h["services"])
        writer.writerow(
            [h["name"], h["region"], h["lat"], h["lng"], services, service_count(h)]
        )
    return buf.getvalue()


def _hospital_anchor(name: str) -> str:
    return "hospital-" + "".join(ch if ch.isalnum() else "-" for ch in name).strip("-").lower()


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
    return (
        tuple(sorted(regions)),
        tuple(sorted(services)),
        match_mode,
        search.strip().lower(),
    )


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
            filtered = [h for h in filtered if all(s in h["services"] for s in services)]
        else:
            filtered = [h for h in filtered if any(s in h["services"] for s in services)]
    return filtered


def sort_hospitals(hospitals: list[dict], sort_by: str) -> list[dict]:
    if sort_by == "Name":
        return sorted(hospitals, key=lambda h: h["name"].lower())
    if sort_by == "Region":
        return sorted(hospitals, key=lambda h: (h["region"].lower(), h["name"].lower()))
    if sort_by == "Number of services":
        return sorted(hospitals, key=lambda h: (-service_count(h), h["name"].lower()))
    return sorted(hospitals, key=lambda h: (h["region"].lower(), h["name"].lower()))


def render_hospital_list(hospitals: list[dict], selected_name: str | None) -> None:
    st.caption(f"{len(hospitals)} hospitals")
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
            anchor = _hospital_anchor(h["name"])
            count = service_count(h)
            meta = "Programs TBD" if tbd else f"{count} service{'s' if count != 1 else ''}"

            st.markdown(
                f"""
                <div id="{anchor}" class="{card_class}">
                    <span class="region-badge" style="background:{badge_bg};color:{badge_fg};">{h['region']}</span>
                    <h4>{h['name']}</h4>
                    <p class="meta">{meta}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if not tbd:
                with st.expander("Services", expanded=False):
                    st.write(", ".join(h["services"]))

            if st.button("Show on map", key=f"focus_{h['name']}", width="stretch"):
                st.session_state.selected_hospital = h["name"]
                st.session_state.focus_hospital = h["name"]
                st.rerun()

    if selected_name:
        anchor = _hospital_anchor(selected_name)
        components.html(
            f"""
            <script>
            const el = window.parent.document.getElementById("{anchor}");
            if (el) el.scrollIntoView({{behavior: "smooth", block: "nearest"}});
            </script>
            """,
            height=0,
        )


def render_map_tab(hospitals: list[dict]) -> None:
    selected = st.session_state.selected_hospital
    focus = st.session_state.focus_hospital

    map_col, list_col = st.columns([3, 1.1], gap="medium")
    with map_col:
        m = build_map(hospitals, selected_name=selected, focus_name=focus)
        center = zoom = None
        if focus and focus in hospitals_by_name():
            h = hospitals_by_name()[focus]
            center = [h["lat"], h["lng"]]
            zoom = 12

        # Only return click tooltip — avoids reruns on pan/zoom.
        map_state = st_folium(
            m,
            height=MAP_HEIGHT,
            use_container_width=True,
            center=center,
            zoom=zoom,
            key="telehealth_map",
            returned_objects=["last_object_clicked_tooltip"],
        )

        tooltip = (map_state or {}).get("last_object_clicked_tooltip")
        if tooltip and tooltip != st.session_state.map_click_sig:
            st.session_state.map_click_sig = tooltip
            if tooltip in hospitals_by_name():
                st.session_state.selected_hospital = tooltip
                st.session_state.focus_hospital = None
                st.rerun()

        if focus:
            st.session_state.focus_hospital = None

    with list_col:
        render_hospital_list(hospitals, selected)


def render_coverage_tab(hospitals: list[dict]) -> None:
    st.caption(
        "Hospital × service coverage for the current filters. "
        "Columns ordered by how many hospitals offer each service."
    )
    names = tuple(h["name"] for h in hospitals)
    df = _cached_coverage(names)

    def _style_cells(val):
        if val == "●":
            return (
                "background-color:#e8f0fb;color:#185FA5;"
                "text-align:center;font-weight:700;"
            )
        if val == "" or val is None:
            return "background-color:#fafafa;color:#ccc;text-align:center;"
        return ""

    service_cols = [c for c in df.columns if c not in ("Hospital", "Total")]
    try:
        styler = df.style.map(_style_cells, subset=service_cols).set_properties(
            **{"font-size": "0.8rem"}
        )
        st.dataframe(styler, width="stretch", height=560)
    except Exception:
        # Fallback if Styler/jinja2 isn't available in the runtime.
        st.dataframe(df, width="stretch", height=560)


def main() -> None:
    _init_state()
    _apply_pending_filter_reset()

    with st.sidebar:
        logo_uri = _logo_data_uri()
        if logo_uri:
            st.markdown(
                f'<img src="{logo_uri}" alt="Northwell Health" width="170" />',
                unsafe_allow_html=True,
            )
        elif LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=170)
        else:
            st.markdown("### Northwell Health")

        st.caption("Telehealth footprint filters")

        st.text_input("Search hospitals", key="search", placeholder="Hospital name…")
        st.multiselect("Region", options=all_regions(), key="regions")
        st.multiselect("Service", options=all_services(), key="services")

        if st.session_state.services:
            st.radio(
                "Match",
                options=["all", "any"],
                format_func=lambda m: (
                    "All selected services"
                    if m == "all"
                    else "Any selected service"
                ),
                key="service_match",
            )

        st.selectbox(
            "Sort",
            options=[
                "Region, then name",
                "Name",
                "Region",
                "Number of services",
            ],
            key="sort_by",
        )

        st.caption(
            "Click a map pin to highlight a hospital, or use Show on map in the list."
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

    sig = _filter_fingerprint(regions, services, match_mode, search)
    if st.session_state.filter_sig != sig:
        st.session_state.filter_sig = sig
        selected = st.session_state.selected_hospital
        if selected and selected not in {h["name"] for h in filtered}:
            st.session_state.selected_hospital = None
            st.session_state.focus_hospital = None

    st.markdown("## Northwell Health — Telehealth Footprint")
    try:
        updated = datetime.strptime(DATA_LAST_UPDATED, "%Y-%m-%d").strftime("%b %d, %Y")
    except ValueError:
        updated = DATA_LAST_UPDATED
    st.markdown(
        f'<p class="updated-caption">Data last updated: {updated}</p>',
        unsafe_allow_html=True,
    )

    total_hospitals = len(filtered)
    total_services = len({s for h in filtered for s in h["services"] if s != "TBD"})
    active_regions = len({h["region"] for h in filtered})
    fully_active = len([h for h in filtered if "TBD" not in h["services"]])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Hospitals shown", total_hospitals)
    c2.metric("Unique services", total_services)
    c3.metric("Regions", active_regions)
    c4.metric(
        "Fully active",
        fully_active,
        help="Hospitals whose service list does not include TBD (service programs are defined).",
    )

    st.download_button(
        "Download filtered data (CSV)",
        data=_cached_csv(tuple(h["name"] for h in filtered)),
        file_name="northwell_telehealth_filtered.csv",
        mime="text/csv",
        disabled=not filtered,
    )

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
