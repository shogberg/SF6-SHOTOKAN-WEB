"""Shared definitions for the publish step: schema version, MR bands, weights, spectra."""
import re

SCHEMA_VERSION = "1.0"          # major.minor: the API refuses an unknown major

# ---- MR bands (docs/analysis-methods.md) -------------------------------------
BANDS = [  # (id, label, lo, hi) on effective MR; Master only
    ("lt1400", "Below 1400", None, 1400),
    ("1400_1600", "1400-1600", 1400, 1600),
    ("1600_1800", "1600-1800", 1600, 1800),
    ("1800_2000", "1800-2000", 1800, 2000),
    ("2000p", "2000+", 2000, None),
]
NON_MASTER = ("diamond_below", "Diamond and below")
UNKNOWN = ("unknown", "MR unknown")
LEAGUES = ("rookie", "iron", "bronze", "silver", "gold", "platinum", "diamond")

# draft weights, pending review (docs/analysis-methods.md)
WEIGHTS = {"diamond_below": 0.5, "lt1600": 0.75, "1600_1800": 1.0, "1800_2000": 2.0, "2000_2100": 3.0, "2100p": 4.0, "unknown": 0.75}

JP_OFFSET = 200   # deferred: no region data yet, so never applied


def effective_mr(mr, region=None):
    if mr is None:
        return None
    return mr - JP_OFFSET if (region or "").upper() == "JP" else mr


def parse_rank(rank):
    """'1692 MR' -> (1692, None); 'Diamond' / 'Platinum 3' -> (None, 'Diamond'); else (None, None)."""
    if not rank:
        return None, None
    m = re.match(r"\s*(\d{3,4})\s*MR", str(rank))
    if m:
        return int(m.group(1)), None
    league = str(rank).split()[0].capitalize()
    return (None, league) if league.lower() in LEAGUES else (None, None)


def band_for(mr, league=None, region=None):
    """Band id and label for one player at one set."""
    if mr is None:
        return NON_MASTER if league else UNKNOWN
    e = effective_mr(mr, region)
    for bid, label, lo, hi in BANDS:
        if (lo is None or e >= lo) and (hi is None or e < hi):
            return bid, label
    return UNKNOWN


def weight_for(mr, league=None, region=None):
    if mr is None:
        return WEIGHTS["diamond_below"] if league else WEIGHTS["unknown"]
    e = effective_mr(mr, region)
    return (WEIGHTS["lt1600"] if e < 1600 else WEIGHTS["1600_1800"] if e < 1800 else WEIGHTS["1800_2000"] if e < 2000
            else WEIGHTS["2000_2100"] if e < 2100 else WEIGHTS["2100p"])


# ---- spectra -----------------------------------------------------------------
ENDS = {"Temperament (defense)": ("Impulsive", "Mindful"), "Temperament (offense)": ("Impulsive", "Mindful"),
        "Adaptability": ("Inelastic", "Elastic"), "Risk tolerance": ("Low", "High"), "Initiative": ("Reactive", "Proactive"),
        "Composure": ("Steady", "Tilts"), "Variety": ("Scripted", "Mixed"), "Resource use": ("Conservative", "Spendthrift")}
AXES = list(ENDS)


def spectrum_label(axis, s):
    l, r = ENDS[axis]
    return {1: f"Very {l.lower()}", 2: f"Leans {l.lower()}", 3: "Middle", 4: f"Leans {r.lower()}", 5: f"Very {r.lower()}"}[s]


def confidence_for(n):
    return "Low" if n < 3 else "Medium" if n < 10 else "High"
