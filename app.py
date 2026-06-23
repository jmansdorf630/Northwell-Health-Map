import streamlit as st
import folium
from streamlit_folium import st_folium
from data import HOSPITALS

st.set_page_config(
    page_title="Northwell Telehealth Footprint",
    page_icon="🏥",
    layout="wide"
)

st.markdown("""
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
    .hospital-card h4 { margin: 0 0 6px 0; font-size: 0.95rem; color: #1a1a1a; }
    .region-badge {
        display: inline-block;
        font-size: 0.7rem;
        padding: 2px 8px;
        border-radius: 20px;
        margin-bottom: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

REGION_COLORS = {
    "Western":  "#185FA5",
    "Central":  "#0F6E56",
    "Eastern":  "#854F0B",
    "Nuvance":  "#6b6b6b",
    "External": "#993C1D",
}

REGION_HEX = {
    "Western":  "#185FA5",
    "Central":  "#1D9E75",
    "Eastern":  "#EF9F27",
    "Nuvance":  "#888780",
    "External": "#D85A30",
}

BADGE_BG = {
    "Western":  "#e8f0fb",
    "Central":  "#e1f5ee",
    "Eastern":  "#faeeda",
    "Nuvance":  "#f1efe8",
    "External": "#faece7",
}

# ── Sidebar filters ──────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Northwell_Health_logo.svg/320px-Northwell_Health_logo.svg.png", width=180)
    st.markdown("---")
    st.markdown("### Filters")

    all_regions = sorted(set(h["region"] for h in HOSPITALS))
    selected_regions = st.multiselect("Region", all_regions, default=all_regions)

    all_services = sorted(set(
        s for h in HOSPITALS for s in h["services"] if s != "TBD"
    ))
    selected_services = st.multiselect("Filter by service", all_services)

    st.markdown("---")
    st.markdown("### About")
    st.caption("Northwell Health hospital-based telehealth footprint across all regions. Hover over pins for details.")

# ── Filter logic ─────────────────────────────────────────────────────────────
filtered = [h for h in HOSPITALS if h["region"] in selected_regions]
if selected_services:
    filtered = [h for h in filtered if any(s in h["services"] for s in selected_services)]

# ── Header + metrics ─────────────────────────────────────────────────────────
st.markdown("## 🏥 Northwell Health — Telehealth Footprint")

total_hospitals = len(filtered)
total_services = len(set(s for h in filtered for s in h["services"] if s != "TBD"))
active_regions = len(set(h["region"] for h in filtered))

c1, c2, c3, c4 = st.columns(4)
for col, num, label in [
    (c1, total_hospitals, "Hospitals shown"),
    (c2, total_services, "Unique services"),
    (c3, active_regions, "Regions"),
    (c4, len([h for h in filtered if "TBD" not in h["services"]]), "Fully active"),
]:
    col.markdown(f"""
    <div class="metric-card">
        <div class="num">{num}</div>
        <div class="label">{label}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Map + sidebar layout ─────────────────────────────────────────────────────
map_col, list_col = st.columns([3, 1.1])

with map_col:
    m = folium.Map(
        location=[40.85, -73.6],
        zoom_start=9,
        tiles="CartoDB positron",
        control_scale=True,
    )

    for h in filtered:
        color = REGION_COLORS.get(h["region"], "#333")
        tbd = h["services"] == ["TBD"]

        services_html = "".join(
            f'<span style="display:inline-block;background:#e8f0fb;color:#185FA5;'
            f'border-radius:20px;padding:2px 9px;font-size:11px;margin:2px;">{s}</span>'
            for s in h["services"]
        ) if not tbd else '<span style="color:#888;font-size:12px;">Programs TBD</span>'

        popup_html = f"""
        <div style="font-family:sans-serif;min-width:220px;max-width:280px;">
            <div style="font-weight:700;font-size:14px;margin-bottom:6px;color:#1a1a1a;">{h['name']}</div>
            <div style="font-size:11px;color:#666;margin-bottom:8px;font-weight:600;text-transform:uppercase;
                letter-spacing:0.05em;">{h['region']} Region</div>
            <div style="border-top:1px solid #eee;padding-top:8px;">{services_html}</div>
        </div>
        """

        folium.CircleMarker(
            location=[h["lat"], h["lng"]],
            radius=9 if not tbd else 7,
            color="white",
            weight=2,
            fill=True,
            fill_color=color,
            fill_opacity=0.9 if not tbd else 0.5,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=h["name"],
        ).add_to(m)

    # Legend
    legend_html = """
    <div style="position:fixed;bottom:30px;left:30px;z-index:1000;
        background:white;padding:12px 16px;border-radius:10px;
        border:1px solid #ddd;font-family:sans-serif;font-size:12px;">
        <div style="font-weight:700;margin-bottom:8px;">Region</div>
    """
    for region, color in REGION_HEX.items():
        legend_html += f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
            <div style="width:12px;height:12px;border-radius:50%;background:{color};flex-shrink:0;"></div>
            <span>{region}</span>
        </div>"""
    legend_html += "</div>"
    m.get_root().html.add_child(folium.Element(legend_html))

    st_folium(m, height=520, use_container_width=True)

with list_col:
    st.markdown("**Hospitals**")
    if not filtered:
        st.info("No hospitals match the current filters.")
    for h in filtered:
        badge_bg = BADGE_BG.get(h["region"], "#eee")
        badge_fg = REGION_COLORS.get(h["region"], "#333")
        tbd = h["services"] == ["TBD"]
        tags = "".join(
            f'<span class="tag{"" if not tbd else " tag-tbd"}">{s}</span>'
            for s in h["services"][:6]
        )
        more = f'<span style="font-size:0.75rem;color:#888;"> +{len(h["services"])-6} more</span>' if len(h["services"]) > 6 else ""
        st.markdown(f"""
        <div class="hospital-card">
            <span class="region-badge" style="background:{badge_bg};color:{badge_fg};">{h['region']}</span>
            <h4>{h['name']}</h4>
            <div>{tags}{more}</div>
        </div>""", unsafe_allow_html=True)
