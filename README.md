# IceTracks-DR2 data-analysis lab (student materials)

A data-analysis lab course for physics master students based on the IceCube
Second Track Data Release (**IceTracks-DR2**): 14 years of track-like
neutrino candidates, 2008–2022.

- Paper: [arXiv:2605.19040](https://arxiv.org/abs/2605.19040)
- Data: [Harvard Dataverse, doi:10.7910/DVN/MMIIZA](https://doi.org/10.7910/DVN/MMIIZA)

## Layout

```
icetracks-dr2-lab-student/
├── src/icelab.py         # data loading, flux models, MC expectation
├── requirements.txt
└── docs/
    ├── getting_started.md            # start here: setup + first task
    ├── how_mc_events_are_obtained.md # literature notes
    └── assignment_source_search.md   # final assignment (source search)
```

Lab notebooks are not distributed in this repository; your instructor
provides them during the course.

## Getting started

Start with [`docs/getting_started.md`](docs/getting_started.md): it covers
installing the required Python packages, downloading the data, and your
first data-reading task.

## Install

```bash
pip install -r requirements.txt
```

## Data setup

The code expects the data release folder (containing `events/`, and
`irfs/` for later labs) **one level above this repository**, or anywhere
pointed to by the environment variable `ICECUBE_DATA_DIR`:

```
<data folder>/                    # e.g. dataverse_files/
├── events/IC*_exp.csv
├── irfs/                         # effective areas (auto-downloaded if missing)
└── icetracks-dr2-lab-student/    # this repository
```

## Data credit

Data © IceCube Collaboration. Cite Abbasi et al. (2026), arXiv:2605.19040
and the Dataverse DOI when using the data.
