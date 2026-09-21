r"""icelab — utilities for the IceCube IceTracks-DR2 data-analysis lab.

Data release: Abbasi et al. (IceCube), "IceCube Second Track Data Release
IceTracks-DR2" (arXiv:2605.19040), Harvard Dataverse doi:10.7910/DVN/MMIIZA.

The expected number of Monte-Carlo (MC) neutrino events follows Eq. (1) of
the paper:

    N_nu = \int dt \int dOmega \int dE  A_eff(E, Omega) * phi_nu(E, Omega)

Note: effective areas are provided for muon NEUTRINOS only. Atmospheric
muons (the dominant background in the southern sky) have no released
effective area/mass: in IceCube point-source analyses their contribution is
estimated directly from the data (right-ascension scrambling), never from
flux x A_eff. See docs/how_mc_events_are_obtained.md.
"""
from __future__ import annotations

import json
import os
import shutil
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

DATAVERSE_DOI = "doi:10.7910/DVN/MMIIZA"
DATAVERSE_API = "https://dataverse.harvard.edu/api"

#: Season livetimes in days — Table 1 of arXiv:2605.19040.
LIVETIME_DAYS = {
    "IC40": 376.4, "IC59": 353.6, "IC79": 312.8,
    "IC86_I": 339.0,   # IC86-2011
    "IC86_II": 327.1,  # IC86-2012
    "IC86_III": 356.2, # IC86-2013
    "IC86_IV": 364.9,  # IC86-2014
    "IC86_V": 365.3,   # IC86-2015
    "IC86_VI": 357.2,  # IC86-2016
    "IC86_VII": 410.9, # IC86-2017
    "IC86_VIII": 368.8,# IC86-2018
    "IC86_IX": 313.3,  # IC86-2019
    "IC86_X": 361.3,   # IC86-2020
    "IC86_XI": 356.6,  # IC86-2021
}

SECONDS_PER_DAY = 86400.0


def aeff_config(season: str) -> str:
    """Which effective-area table applies to a season (all IC86 share one)."""
    return season if season in ("IC40", "IC59", "IC79") else "IC86"


# ---------------------------------------------------------------- data I/O

def get_data_dir(data_dir=None) -> Path:
    """Resolve the data-release folder (contains 'events').

    Order: explicit argument > $ICECUBE_DATA_DIR > walk up from cwd.
    """
    if data_dir:
        return Path(data_dir)
    env = os.environ.get("ICECUBE_DATA_DIR")
    if env:
        return Path(env)
    p = Path.cwd().resolve()
    for cand in (p, *p.parents):
        if (cand / "events").is_dir():
            return cand
    raise FileNotFoundError(
        "Data release not found: no 'events' folder above the current "
        "directory. Pass data_dir= or set ICECUBE_DATA_DIR."
    )


def _read_release_csv(path) -> pd.DataFrame:
    """Release files are whitespace-separated with a '#'-prefixed header."""
    with open(path) as f:
        names = f.readline().lstrip("#").split()
    return pd.read_csv(path, sep=r"\s+", skiprows=1, names=names)


def load_events(data_dir=None, seasons=None) -> pd.DataFrame:
    """Load all (or selected) seasons of experimental events into one frame."""
    data_dir = get_data_dir(data_dir)
    frames = []
    for path in sorted((data_dir / "events").glob("IC*_exp.csv")):
        season = path.stem[: -len("_exp")]
        if seasons is not None and season not in seasons:
            continue
        df = _read_release_csv(path)
        df["season"] = season
        frames.append(df)
    if not frames:
        raise FileNotFoundError(f"No event files found in {data_dir/'events'}")
    return pd.concat(frames, ignore_index=True)


def _open_url(url):
    """urlopen with an explicit User-Agent (Dataverse 403s the urllib default)."""
    return urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": "icelab/1.0"})
    )


def download_irfs(data_dir=None, doi=DATAVERSE_DOI, keyword="eff") -> list:
    """Download instrument-response tables from the Harvard Dataverse release.

    Only files whose name contains `keyword` are fetched, into
    <data_dir>/irfs/. Default keyword fetches the effective areas (small);
    use e.g. keyword="IC86_smearing" for one smearing matrix (~600 MB).
    Needs internet access once.
    """
    data_dir = get_data_dir(data_dir)
    dest = data_dir / "irfs"
    dest.mkdir(exist_ok=True)
    url = f"{DATAVERSE_API}/datasets/:persistentId/?persistentId={doi}"
    with _open_url(url) as r:
        meta = json.load(r)
    fetched = []
    for entry in meta["data"]["latestVersion"]["files"]:
        d = entry["dataFile"]
        # ingested files are renamed *.tab in the record; keep the original name
        name = d.get("originalFileName") or d["filename"]
        folder = entry.get("directoryLabel", "")
        if "irf" not in (folder + name).lower():
            continue
        if keyword.lower() not in name.lower():
            continue
        out = dest / name
        if not out.exists():
            # format=original: Dataverse ingests csv into its own tab format
            tmp = out.with_suffix(out.suffix + ".part")
            with _open_url(
                f"{DATAVERSE_API}/access/datafile/{d['id']}?format=original"
            ) as r, open(tmp, "wb") as f:
                shutil.copyfileobj(r, f)
            tmp.rename(out)
        fetched.append(out)
    if not fetched:
        raise RuntimeError(f"No files matching {keyword!r} in the Dataverse record.")
    return fetched


def load_effective_area(data_dir=None, config="IC86") -> pd.DataFrame:
    """Load the tabulated effective area for a detector configuration.

    Columns: log10(E_nu/GeV)_min/max, Dec_nu_min/max[deg], A_Eff[cm^2].
    """
    data_dir = get_data_dir(data_dir)
    irfs = data_dir / "irfs"
    cands = [
        p for p in irfs.glob("*.csv")
        if p.name.lower().startswith(config.lower()) and "eff" in p.name.lower()
    ]
    if not cands:
        raise FileNotFoundError(
            f"No effective-area table for {config} in {irfs}. "
            "Run icelab.download_irfs() first."
        )
    # prefer the generic table (shortest name) if several match
    return _read_release_csv(sorted(cands, key=lambda p: len(p.name))[0])


#: Bin-edge columns shared by the effective-area and smearing tables.
_SMEAR_BIN_COLS = [
    "log10(E_nu/GeV)_min", "log10(E_nu/GeV)_max",
    "Dec_nu_min[deg]", "Dec_nu_max[deg]",
    "log10(E/GeV)_min", "log10(E/GeV)_max",
]


def load_energy_smearing(data_dir=None, config="IC86", refresh=False) -> pd.DataFrame:
    """Energy response P(E_reco bin | E_nu bin, dec bin) from the smearing matrix.

    The released smearing matrices are 5D — (E_nu, Dec_nu) -> (E_reco, PSF,
    AngErr) with Fractional_Counts normalized per (E_nu, Dec_nu) bin. This
    reads the ~600 MB table in chunks, sums Fractional_Counts over PSF and
    AngErr, and caches the small energy-only marginal next to the raw file,
    so only the first call is slow.

    Note: the (E_reco, PSF, AngErr) bin edges are chosen independently in
    each (E_nu, Dec_nu) bin — there is no global reco-energy grid (use
    `smear_to_reco` to histogram onto one).
    """
    data_dir = get_data_dir(data_dir)
    raw = data_dir / "irfs" / f"{config}_smearing.csv"
    cache = raw.with_name(f"{config}_smearing_energy.csv")
    if cache.exists() and not refresh:
        return pd.read_csv(cache)
    if not raw.exists():
        raise FileNotFoundError(
            f"{raw} not found. Run icelab.download_irfs(keyword='{config}_smearing') "
            "first (~600 MB, one-time)."
        )
    with open(raw) as f:
        names = f.readline().lstrip("#").split()
    parts = [
        chunk.groupby(_SMEAR_BIN_COLS, as_index=False)["Fractional_Counts"].sum()
        for chunk in pd.read_csv(raw, sep=r"\s+", skiprows=1, names=names,
                                 chunksize=2_000_000)
    ]
    out = pd.concat(parts).groupby(_SMEAR_BIN_COLS, as_index=False)[
        "Fractional_Counts"].sum()
    out.to_csv(cache, index=False)
    return out


def smear_to_reco(mc, smearing, reco_edges) -> np.ndarray:
    """Fold a binned MC expectation into a reconstructed-energy histogram.

    Each (E_nu, dec) bin's n_expected is split over that bin's reco-energy
    bins with Fractional_Counts, then re-histogrammed onto `reco_edges`
    proportionally to the overlap in log10(E_reco).

    Parameters
    ----------
    mc : output of `expected_events` (pre-filter it, e.g. to dec >= -5)
    smearing : output of `load_energy_smearing` (same config as `mc`)
    reco_edges : target histogram edges in log10(E_reco/GeV)

    Returns the expected counts per `reco_edges` bin.

    Despite the readme, the smearing (E_nu, dec) parent bins are *coarser*
    than the effective-area bins (limited MC statistics), so each MC bin is
    assigned to the parent bin containing its center.
    """
    e_mins = np.sort(smearing["log10(E_nu/GeV)_min"].unique())
    e_max = smearing["log10(E_nu/GeV)_max"].max()
    d_mins = np.sort(smearing["Dec_nu_min[deg]"].unique())
    d_max = smearing["Dec_nu_max[deg]"].max()

    # accumulate n_expected of the MC bins falling in each parent bin
    e_c = 0.5 * (mc["log10(E_nu/GeV)_min"] + mc["log10(E_nu/GeV)_max"]).values
    d_c = 0.5 * (mc["Dec_nu_min[deg]"] + mc["Dec_nu_max[deg]"]).values
    ie = np.searchsorted(e_mins, e_c, side="right") - 1
    idd = np.searchsorted(d_mins, d_c, side="right") - 1
    ok = (ie >= 0) & (idd >= 0) & (e_c < e_max) & (d_c < d_max)
    n_parent = np.zeros((len(e_mins), len(d_mins)))
    np.add.at(n_parent, (ie[ok], idd[ok]), mc["n_expected"].values[ok])

    se = np.searchsorted(e_mins, smearing["log10(E_nu/GeV)_min"].values)
    sd = np.searchsorted(d_mins, smearing["Dec_nu_min[deg]"].values)
    w = smearing["Fractional_Counts"].values * n_parent[se, sd]
    lo = smearing["log10(E/GeV)_min"].values
    hi = smearing["log10(E/GeV)_max"].values
    width = np.where(hi > lo, hi - lo, 1.0)
    reco_edges = np.asarray(reco_edges, dtype=float)
    counts = np.empty(len(reco_edges) - 1)
    for k in range(len(counts)):
        overlap = np.clip(
            np.minimum(hi, reco_edges[k + 1]) - np.maximum(lo, reco_edges[k]),
            0.0, None,
        )
        counts[k] = np.sum(w * overlap / width)
    return counts


# ------------------------------------------------------------- flux models

def cos_theta_star(cos_theta):
    """Effective zenith cosine accounting for Earth curvature.

    Parametrization by D. Chirkin, hep-ph/0407078.
    """
    p1, p2, p3, p4, p5 = 0.102573, -0.068287, 0.958633, 0.0407253, 0.817285
    x = np.abs(np.asarray(cos_theta, dtype=float))
    num = x**2 + p1**2 + p2 * x**p3 + p4 * x**p5
    den = 1.0 + p1**2 + p2 + p4
    return np.sqrt(num / den)


def atm_flux(E, cos_theta):
    """Conventional atmospheric nu_mu + anti-nu_mu flux [GeV^-1 cm^-2 s^-1 sr^-1].

    Analytic pion/kaon approximation (Gaisser, 'Cosmic Rays and Particle
    Physics', 2nd ed., eq. 6.7), valid for E >~ 100 GeV where the primary
    spectrum is ~E^-2.7. The two terms are the pion and kaon contributions
    with critical energies eps_pi = 115 GeV and eps_K = 850 GeV.
    """
    E = np.asarray(E, dtype=float)
    ct = cos_theta_star(cos_theta)
    return 0.0096 * E**-2.7 * (
        1.0 / (1.0 + 3.7 * E * ct / 115.0)
        + 0.38 / (1.0 + 1.7 * E * ct / 850.0)
    )


def astro_flux(E, phi0=1.44e-18, gamma=2.37, E0=1e5):
    """Diffuse astrophysical nu_mu + anti-nu_mu flux [GeV^-1 cm^-2 s^-1 sr^-1].

    Single power law, best fit of the 9.5-yr diffuse tracks analysis
    (Abbasi et al. 2022, ApJ 928 50): phi0 at E0 = 100 TeV, index 2.37.
    """
    E = np.asarray(E, dtype=float)
    return phi0 * (E / E0) ** -gamma


def dec_to_cos_zenith(dec_deg):
    """At the South Pole cos(zenith) = -sin(declination) (zenith = dec + 90 deg)."""
    return -np.sin(np.radians(np.asarray(dec_deg, dtype=float)))


# --------------------------------------------------------- MC expectation

def expected_events(aeff: pd.DataFrame, flux, livetime_s: float) -> pd.DataFrame:
    """MCevt = flux x A_eff, integrated over each (E, dec) bin and livetime.

    Per bin:  N = phi(E_c, dec_c) * A_eff * dE * dOmega * T
    where dOmega = 2*pi*(sin(dec_max) - sin(dec_min)).

    Parameters
    ----------
    aeff : effective-area table from `load_effective_area`
    flux : callable phi(E_GeV, dec_deg) -> GeV^-1 cm^-2 s^-1 sr^-1
    livetime_s : detector livetime in seconds

    Returns a copy of `aeff` with E_center, dec_center and n_expected columns.
    """
    df = aeff.copy()
    e_lo = 10.0 ** df["log10(E_nu/GeV)_min"].values
    e_hi = 10.0 ** df["log10(E_nu/GeV)_max"].values
    e_c = np.sqrt(e_lo * e_hi)  # log-centered bin energy
    dec_lo = df["Dec_nu_min[deg]"].values
    dec_hi = df["Dec_nu_max[deg]"].values
    d_omega = 2.0 * np.pi * (np.sin(np.radians(dec_hi)) - np.sin(np.radians(dec_lo)))
    df["E_center"] = e_c
    df["dec_center"] = 0.5 * (dec_lo + dec_hi)
    df["n_expected"] = (
        flux(e_c, df["dec_center"].values)
        * df["A_Eff[cm^2]"].values
        * (e_hi - e_lo)
        * d_omega
        * livetime_s
    )
    return df


def total_livetime_s(seasons) -> float:
    """Summed livetime [s] of the given seasons."""
    return sum(LIVETIME_DAYS[s] for s in seasons) * SECONDS_PER_DAY
