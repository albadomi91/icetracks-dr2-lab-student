# Assignment — Is there a neutrino excess from your favourite source?

*Final assignment of the IceTracks-DR2 data-analysis lab. It uses
everything from Labs 1–3: the event sample, the instrument response, and
the point-source likelihood.*

## The task

Pick **one candidate neutrino source**, and answer quantitatively: *do the
IceCube tracks show an excess of events from its direction?* You must
produce (a) a counting-based answer, (b) a likelihood-based answer with a
properly calibrated p-value, and (c) if you find no significant excess, an
upper limit.

## Choosing a source

Any astrophysical object with a reason to emit neutrinos is fine
(γ-ray blazars, Seyfert galaxies, supernova remnants, the Galactic
Center…). Motivate your choice in one paragraph. Suggestions:

| Source | RA [deg] | Dec [deg] | Why it is interesting |
|---|---|---|---|
| TXS 0506+056 | 77.36 | +5.69 | the famous blazar: 2017 alert event + 2014–15 neutrino flare |
| NGC 1068 | 40.67 | −0.01 | hottest northern spot of the companion paper (Table 3) |
| PKS 1424+240 | 216.75 | +23.80 | soft-spectrum blazar candidate |
| Sagittarius A* | 266.42 | −29.01 | the Galactic Center — but read the warning below! |

**Warning about southern sources** (δ < −5°): there the sample is
dominated by atmospheric muons and the selection cuts hard on energy
(Lab 1, Lab 2). A southern search is possible but much less sensitive —
if you go south, explain how this changes your background estimate and
your interpretation.

## Part 1 — Look at the neighbourhood (warm-up)

1. Select the events within a few degrees of the source. Plot their sky
   positions (with `AngErr` as a size or error indicator), their
   `log10(E/GeV)` distribution, and their MJD times.
2. Compare the energy distribution with an **off-source** region: same
   declination band, different right ascension. Why is same-δ/different-RA
   the right control region for IceCube? (Think about what is uniform in
   RA and why — Lab 1.)

## Part 2 — Counting experiment

3. Count events in an on-source cone of radius $r$. Estimate the expected
   background in the cone from the same-declination band (scaled by solid
   angle), and compute the Poisson significance of the on-source count.
4. Choose $r$ deliberately: the PSF (paper Fig. 1, or the smearing
   matrices) tells you the signal containment vs energy; the background
   grows like $r^2$. Try 1°, 2°, 3° and comment. Optional: an
   energy cut (e.g. keep only events above some `log10(E/GeV)`) can
   raise the signal-to-background — justify your choice *before* looking
   at the on-source data if you want your significance to mean anything
   (this is what "blind analysis" means).

## Part 3 — Likelihood analysis

5. Run the Lab 3 unbinned likelihood at the source position: report
   $\hat n_s$ and TS. You can lift the code directly from
   `03_allsky_search.ipynb` — it is one pixel of that map.
6. **Calibrate the p-value with scrambling**: generate ≥ 1000
   pseudo-experiments by randomizing the events' RA (keep dec, energy,
   AngErr fixed), refit each, and take the fraction of trials with
   TS ≥ TS_observed. Compare with the Wilks approximation
   $p = \frac12 P(\chi^2_1 > \mathrm{TS})$ used in Lab 3. Where does
   Wilks fail, and why?
7. Optional (+): fit the spectral index too — evaluate the likelihood on a
   grid of $\gamma \in [1.5, 4]$ with one signal energy PDF per $\gamma$
   (build them with `icelab.smear_to_reco`, Lab 2). NGC 1068 is the
   instructive case: compare TS at $\gamma = 2$ vs free $\gamma$.

## Part 4 — Interpret

8. If you see no significant excess (likely!): set a 90% C.L. upper limit
   on $n_s$ from your scrambling trials (the $n_s^{90}$ such that 90% of
   background trials injected with… — think about it, or use the simple
   counting limit from Part 2). Optional (+): convert $n_s^{90}$ into a
   flux limit using the effective area and livetime (Lab 2 tells you the
   events expected per unit flux — no new machinery needed).
9. **For TXS 0506+056 only**: the excess claimed in the literature is
   *time-clustered*. The 2014–15 flare window (MJD 56937–57096) is fully
   contained in the IC86-2014 season, which is in your data folder. Split
   your on-source events in time: is the counting significance in that
   window different from the full-sample one? (The 2017 alert event
   IC170922A is in the IC86-2017 season — check whether your data folder
   includes it before drawing conclusions.)

## Deliverable

A short report (≤ 6 pages or a clean notebook): source motivation, the
plots of Part 1, the counting and likelihood results with the scrambled
p-value, the limit or the excess discussion, and an honest list of the
approximations you inherited from the labs (Gaussian PSF, IC86 smearing
for all seasons, seasons available in your data folder — state which!).

**What gets graded**: the correctness of the background estimate, the
calibration of the p-value, and the honesty of the caveats — *not*
whether you find a signal. A solid null result with a defensible limit is
a full-marks answer.
