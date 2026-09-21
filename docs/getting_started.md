# Getting started — read the data and take a first look

*First task of the IceTracks-DR2 data-analysis lab. The goal is to get
comfortable with the raw data yourself, writing your own code — not to rely
on a helper library from the start.*

## Background

You will be working with the IceCube **IceTracks-DR2** data release: 14
years (2008–2022) of track-like neutrino candidates, 1,643,355 events in
total. Each event is a single reconstructed muon track through the IceCube
detector at the South Pole, with an estimated energy, direction, and angular
uncertainty.

- Paper: [arXiv:2605.19040](https://arxiv.org/abs/2605.19040)
- Data: [Harvard Dataverse, doi:10.7910/DVN/MMIIZA](https://doi.org/10.7910/DVN/MMIIZA)

## Setup

### 1. Python libraries

You need:

- `numpy`
- `pandas`
- `matplotlib`
- `jupyter`
- `scipy`

If you are using the course repository, these are all listed in
`requirements.txt`; install them with:

```bash
pip install -r requirements.txt
```

(Two more packages, `MCEq` and `crflux`, are needed later for an optional
part of Lab 2 — you do not need them for this task.)

### 2. Download the data

Go to the Dataverse record at
[doi:10.7910/DVN/MMIIZA](https://doi.org/10.7910/DVN/MMIIZA) and download the
**event files**: a folder called `events/` containing one CSV per detector
season (`IC40_exp.csv`, `IC59_exp.csv`, `IC79_exp.csv`,
`IC86_I_exp.csv` … `IC86_XI_exp.csv`). This is about 85 MB in total. You do
**not** need the `irfs/` folder (effective areas, smearing matrices) for this
task — that is only needed starting from Lab 2, and can be downloaded
automatically later with `icelab.download_irfs()`.

Place the `events/` folder so it sits **next to** this repository, not
inside it:

```
<data folder>/            # e.g. dataverse_files/
├── events/IC*_exp.csv
└── <this repository>/
```

If you keep the data somewhere else, set the environment variable
`ICECUBE_DATA_DIR` to point to `<data folder>` instead.

### 3. Where to work

Write your own Jupyter notebook (`jupyter lab`) or a plain Python script —
your choice, and you decide where in the repository to put it. If you want
to reuse the course's helper module (`src/icelab.py`, optional — see Step 1
below), add its folder to the Python path first, adjusting the relative path
to wherever you placed your file:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path("src").resolve()))  # e.g. "../src" if you work one level down
import icelab
```

## Task: read and investigate the data

### Step 1 — Look at the raw format before trusting any tool

Open **one** season file directly (a text editor, or `head IC86_XI_exp.csv`
in a terminal) before loading anything into pandas. Note that:

- The file is **whitespace-separated**, not comma-separated.
- The first line is a header starting with `#`, listing the columns:
  `run`, `event`, `subevent`, `MJD[days]`, `log10(E/GeV)`, `AngErr[deg]`,
  `RA[deg]`, `Dec[deg]`, `Azimuth[deg]`, `Zenith[deg]`.

Now write the code to load this one file into a pandas `DataFrame` yourself
(`pd.read_csv` with the right separator and header handling), and check that
the columns and a few rows look sensible. Then extend your code to load
**all** season files and concatenate them into a single `DataFrame`, adding a
column that records which season each event came from (you will need it
later).

If you are using the course repository, `icelab.load_events()` does exactly
this for you — but only use it *after* you've loaded one file by hand and
understood the format.

### Step 2 — Sanity-check the sample

Using your combined `DataFrame`, answer:

- How many events are there in total, and how many seasons?
- What is the total livetime (sum of the per-season exposure times), and what
  is the resulting all-sky event rate in mHz? The paper quotes a value around
  4 mHz — check whether your number is in that ballpark. (Per-season
  livetimes in days are listed in Table 1 of the paper; if you are using
  `icelab`, they are also available as `icelab.LIVETIME_DAYS`.)
- What is the time range (`MJD[days]`) covered by the whole sample, and by
  each season individually? Do the seasons overlap, or are they contiguous?

### Step 3 — First investigation

Produce and discuss the following, in your own words:

1. **Energy distribution.** Plot a histogram of `log10(E/GeV)` for the whole
   sample. What is the approximate energy range covered? Is the distribution
   a simple power law, or does its shape change somewhere?
2. **Hemispheres.** IceCube's northern sky is defined as declination
   `Dec[deg] >= -5`, southern sky as `Dec[deg] < -5`. Split the sample into
   the two hemispheres and overlay their energy distributions. You should see
   a clear difference in shape and typical energy. One hemisphere is
   dominated by atmospheric **neutrinos**, the other by atmospheric
   **muons** with a hard energy selection cut — which is which, and why does
   the detector's location (the South Pole) make this distinction possible?
   (See `docs/how_mc_events_are_obtained.md` if you want the full physics
   explanation, but try to reason about it yourself first from the plot.)
3. **Angular uncertainty.** Plot `AngErr[deg]` against `log10(E/GeV)` (a 2D
   histogram, log scale on both is a good idea). What is the relationship
   between energy and angular resolution, and what is the smallest `AngErr`
   value you find in the data?
4. **Sky map.** Make a 2D histogram of event positions in equatorial
   coordinates (`RA[deg]` vs `Dec[deg]`). Is the distribution uniform in
   right ascension? Should it be, given how a ground-based detector at the
   South Pole observes the sky as the Earth rotates? Is it uniform in
   declination, and if not, why might that be?

### Deliverable

A short notebook or write-up containing: the four plots above, one or two
sentences of comment per plot answering the questions asked, and the summary
numbers from Step 2 (event count, livetime, rate). No formal report needed —
this is a warm-up, not the final assignment.

## Where this fits in the course

Once you're done, your instructor will walk through a worked version of this
same exploration, going a bit further (per-season rates, more plots). The
physics behind the hemisphere split is explained in detail in
`docs/how_mc_events_are_obtained.md`. Later labs build on the skills from
this task: Lab 2 compares the data to a Monte-Carlo expectation, Lab 3 runs a
point-source search across the whole sky, and the final assignment
(`docs/assignment_source_search.md`) asks you to apply all of it to a source
of your choice.

## Data credit

Data © IceCube Collaboration. Cite Abbasi et al. (2026), arXiv:2605.19040
and the Dataverse DOI when using the data.
