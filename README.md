# Northwell Health — Telehealth Footprint Map

Interactive Streamlit app showing hospital-based telehealth services across all Northwell regions.

## Features
- Real map with accurate hospital coordinates (Folium + CartoDB basemap)
- Click any pin for a popup listing all telehealth services
- Sidebar filters by region and by specific service
- Hospital list panel with quick-scan service tags
- Summary metrics at the top

## Local setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud (free, shareable URL)

1. Push this folder to a **public GitHub repo**
2. Go to https://share.streamlit.io
3. Sign in with GitHub → click **New app**
4. Select your repo, branch (`main`), and set **Main file path** to `app.py`
5. Click **Deploy** — you'll get a URL like `https://yourname-northwell-telehealth.streamlit.app`

Share that URL with anyone at Northwell — no login required.

## Updating hospital data

All hospital info lives in `data.py`. To add a hospital:

```python
{
    "name": "New Hospital Name",
    "region": "Western",       # Western | Central | Eastern | Nuvance | External
    "lat": 40.000,
    "lng": -73.000,
    "services": ["TeleICU", "TeleStroke", ...],
},
```

Push to GitHub and the live app updates automatically.
