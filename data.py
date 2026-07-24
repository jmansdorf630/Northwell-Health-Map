# Bump this when hospital/service data changes (shown under the app title).
DATA_LAST_UPDATED = "2026-07-24"

HOSPITALS = [
    # ── Western Region ───────────────────────────────────────────────────────
    {
        "name": "Lenox Hill Hospital",
        "region": "Western",
        "lat": 40.7704, "lng": -73.9636,
        "services": [
            "TeleICU","TelePICU","TelePeds Cardio","TelePeds Neph","TeleSBIRT",
            "TelePeds ID","TeleStroke","TelePsych","TelePeds Neuro","TelePeds Endo",
            "TelePeds GI","TelePETS","TelePeds Rheum","TeleNICU","TelePeds Pulm",
            "TelePeds Allergy/Immun","TeleCAP"
        ],
    },
    {
        "name": "Greenwich Village Hospital",
        "region": "Western",
        "lat": 40.7328, "lng": -74.0025,
        "services": [
            "TelePsych","TeleStroke","TelePeds Hospitalist","TeleICU","TeleHemOnc",
            "TelePsych CL","TeleHospitalist","TeleGeri-Pall","TelePeds Allergy/Immun",
            "TelePETS","TeleGI","TeleID","TeleEndo","TelePulm","TeleNephro"
        ],
    },
    {
        "name": "Staten Island Hospital",
        "region": "Western",
        "lat": 40.6154, "lng": -74.0776,
        "services": [
            "TeleICU","TeleStroke(S)","TelePeds ICU(N)","TeleStroke","TelePeds Rheum",
            "TelePsych","TeleCardiology(S)","TelePsych C/L","TelePICU","TelePETS",
            "TeleGenetic","TelePeds Allergy/Immun"
        ],
    },
    {
        "name": "Northern Westchester Hospital",
        "region": "Western",
        "lat": 41.1887, "lng": -73.7743,
        "services": [
            "TeleICU","TelePsych","TeleStroke","TelePeds Endo","TeleNICU",
            "TelePeds Cardiology","TeleSBIRT","TelePICU","TelePeds ID","TelePeds GI",
            "TelePeds Neuro","TelePeds Nephro","TelePeds Rheum","TelePeds Pulm",
            "TelePETS","TelePeds Allergy/Immun"
        ],
    },
    {
        "name": "Phelps Memorial Hospital",
        "region": "Western",
        "lat": 41.0887, "lng": -73.8621,
        "services": [
            "TeleICU","TeleStroke","TelePsych","TelePsych C/L","TeleMed History",
            "TelePeds Endo","TelePeds ID","TelePeds GI","TelePeds Cardio","TeleSBIRT",
            "TelePICU","TelePeds Hospitalist","TelePeds Neuro","Virtual Nursing",
            "TelePeds Nephro","TeleNICU","TelePeds Pulm","TelePETS","TelePeds Allergy/Immun"
        ],
    },

    # ── Central Region ───────────────────────────────────────────────────────
    {
        "name": "LIJ Forest Hills",
        "region": "Central",
        "lat": 40.7184, "lng": -73.8468,
        "services": [
            "TeleICU","TeleStroke","TelePsych","TelePeds ID","TelePeds GI",
            "TelePeds Nephro","TeleSBIRT","TeleBurn","TelePeds Endo","TelePeds Neuro",
            "TelePeds NICU","TelePeds Pulm","TelePeds Allergy/Immun"
        ],
    },
    {
        "name": "LIJ Valley Stream",
        "region": "Central",
        "lat": 40.6638, "lng": -73.7077,
        "services": [
            "TeleICU","TeleStroke","TelePsych","TeleBurn","TeleHem Onc",
            "TelePsych C/L","TeleSBIRT","TelePICU","TeleID Adult","TeleNICU"
        ],
    },
    {
        "name": "LIJ Medical Center",
        "region": "Central",
        "lat": 40.7541, "lng": -73.7059,
        "services": ["TeleICU","TeleSBIRT","TeleStroke","TelePsych","TeleNeuro CC"],
    },
    {
        "name": "North Shore University Hospital",
        "region": "Central",
        "lat": 40.7896, "lng": -73.6778,
        "services": [
            "TeleSBIRT","TeleTriage","TeleStroke","TelePeds ID","TelePeds Nephro",
            "TeleICU","TelePsych","TelePeds Endo","TelePeds Neuro","TelePeds GI",
            "TelePeds Pulm","TelePeds Allergy/Immun","TeleNICU"
        ],
    },
    {
        "name": "Cohen Children Medical Center",
        "region": "Central",
        "lat": 40.7543, "lng": -73.7082,
        "services": ["TelePsych","Anesthesia/PST","TelePeds NETS"],
    },

    # ── Eastern Region ───────────────────────────────────────────────────────
    {
        "name": "Glen Cove Hospital",
        "region": "Eastern",
        "lat": 40.8626, "lng": -73.6318,
        "services": ["TeleICU","TeleStroke","TelePsych","TelePsych C/L","TeleSBIRT","TeleNICU"],
    },
    {
        "name": "Huntington Hospital",
        "region": "Eastern",
        "lat": 40.8715, "lng": -73.4254,
        "services": [
            "TeleICU","TeleStroke","TelePsych","TelePeds GI","TelePeds Endo",
            "TelePeds ID","Tele-Heart Failure","TelePeds Nephro","TelePeds Neuro",
            "TeleSBIRT","TelePeds Pulm","TeleNICU","TelePeds Allergy/Immun",
            "TelePICU","TelePeds Rheum"
        ],
    },
    {
        "name": "Mather Hospital",
        "region": "Eastern",
        "lat": 40.9368, "lng": -73.0693,
        "services": ["TeleICU","TeleStroke","TelePsych","TelePsych C/L","TeleSBIRT","TeleNICU"],
    },
    {
        "name": "Peconic Bay Medical Center",
        "region": "Eastern",
        "lat": 40.9176, "lng": -72.6374,
        "services": [
            "TeleICU","TeleStroke","TelePsych","TelePeds GI","TelePeds Endo",
            "TelePeds ID","TelePeds Neuro","TelePeds Nephro","TeleSBIRT",
            "TeleNICU","TelePeds Allergy/Immun","TelePICU"
        ],
    },
    {
        "name": "Syosset Hospital",
        "region": "Eastern",
        "lat": 40.8237, "lng": -73.5021,
        "services": [
            "TeleICU","TeleStroke","TelePsych","TelePsych C/L","TeleSBIRT",
            "TelePICU","TeleNeurology","TeleNICU"
        ],
    },
    {
        "name": "Plainview Hospital",
        "region": "Eastern",
        "lat": 40.7776, "lng": -73.4679,
        "services": ["TeleICU","TeleStroke","TelePsych","TelePsych C/L","TeleSBIRT","TeleNICU"],
    },
    {
        "name": "South Shore Hospital",
        "region": "Eastern",
        "lat": 40.6557, "lng": -73.3293,
        "services": [
            "TeleICU","TeleStroke","TelePsych","TelePeds GI","TelePeds Endo",
            "TelePeds ID","Tele-Heart Failure","TelePeds Neuro","TelePeds Nephro",
            "TeleSBIRT","TelePeds Pulm","TeleNICU","TelePeds Allergy/Immun",
            "TelePICU","TelePeds Rheum"
        ],
    },

    # ── Nuvance Region ───────────────────────────────────────────────────────
    {
        "name": "Northern Dutchess Hospital",
        "region": "Nuvance",
        "lat": 41.9959, "lng": -73.8751,
        "services": ["TBD"],
    },
    {
        "name": "Vassar Brothers Medical Center",
        "region": "Nuvance",
        "lat": 41.6929, "lng": -73.9196,
        "services": ["TBD"],
    },
    {
        "name": "Putnam Hospital",
        "region": "Nuvance",
        "lat": 41.4982, "lng": -73.7393,
        "services": ["TBD"],
    },
    {
        "name": "Sharon Hospital",
        "region": "Nuvance",
        "lat": 41.8784, "lng": -73.4743,
        "services": ["TBD"],
    },
    {
        "name": "New Milford Hospital",
        "region": "Nuvance",
        "lat": 41.5773, "lng": -73.4090,
        "services": ["TBD"],
    },
    {
        "name": "Danbury Hospital",
        "region": "Nuvance",
        "lat": 41.3948, "lng": -73.4540,
        "services": ["TBD"],
    },
    {
        "name": "Norwalk Hospital",
        "region": "Nuvance",
        "lat": 41.1176, "lng": -73.4182,
        "services": ["TBD"],
    },

    # ── External Stakeholders ─────────────────────────────────────────────────
    {
        "name": "Jamaica Medical Center",
        "region": "External",
        "lat": 40.6920, "lng": -73.8054,
        "services": ["TeleICU","TeleNeurology Critical Care"],
    },
    {
        "name": "Flushing Medical Center",
        "region": "External",
        "lat": 40.7335, "lng": -73.8330,
        "services": ["TeleICU","TeleNeurology Critical Care"],
    },
]
