# How MC events are obtained from the data release — literature notes

## The question

The IceTracks-DR2 release contains experimental events (which include
atmospheric muons in the southern sky) but ships effective areas only for
muon neutrinos, and no effective area/effective mass for atmospheric muons.
How are MC events actually obtained?

## Answer from the literature

**1. MC neutrino events = flux × effective area × livetime.**
Both release papers (Abbasi et al. 2026, arXiv:2605.19040, Sec. 3; Abbasi et
al. 2021, arXiv:2101.09836, Sec. IV, Eq. 1) define

N_ν = ∫dt ∫dΩ ∫dE_ν A_eff(E_ν, Ω) φ_ν(E_ν, Ω, t)

On the binned tables: per (E_ν, δ) bin,
N = T · φ(E_c, δ_c) · A_eff · ΔE · ΔΩ, with ΔΩ = 2π(sin δ_max − sin δ_min).
To also predict *reconstructed* quantities (energy proxy, PSF, angular
error), the per-bin counts are distributed using the released 5D smearing
matrices ("IRFs"). This is exactly what the open-source SkyLLH framework
does with these files.

**2. The flux φ is an external model, not part of the release.**
Standard choices: conventional atmospheric ν_μ from Honda et al. (HKKM) or
MCEq (GaisserH3a primaries + SIBYLL-2.3c; Fedynitch et al. 2015), or the
analytic pion/kaon approximation (Gaisser, *Cosmic Rays and Particle
Physics*, 2nd ed., Eq. 6.7) used in this lab; astrophysical: diffuse power
law, e.g. φ₀(E/100 TeV)^−2.37 with φ₀ = 1.44×10⁻¹⁸ GeV⁻¹cm⁻²s⁻¹sr⁻¹
(Abbasi et al. 2022, ApJ 928 50).

**3. Atmospheric muons deliberately have no released response.**
The effective areas are computed from muon-*neutrino* signal simulation
(ν_μ CC). The southern-sky atmospheric muons are a background whose
CORSIKA-based simulation is not distributed. Crucially, IceCube's
point-source analyses never need it: the background PDF is estimated
**data-driven**, by scrambling the observed events uniformly in right
ascension within declination bands (arXiv:2605.19040 Sec. 4.1;
arXiv:2101.09836 Sec. 4; method from Braun et al., Astropart. Phys. 29
(2008) 299). Since IceCube's effective area is uniform in RA on timescales
≥ 1 day, scrambled data is an excellent background model that includes
atmospheric muons, atmospheric neutrinos and detector effects for free.

**Consequence for this lab:** flux × A_eff reproduces the northern-sky
(neutrino-dominated) event counts; the southern-sky muon population can only
be described from the data itself.

## References

- Abbasi et al. (IceCube), *IceCube Second Track Data Release
  IceTracks-DR2*, arXiv:2605.19040 (2026). Data: doi:10.7910/DVN/MMIIZA.
- Abbasi et al. (IceCube), *IceCube Data for Neutrino Point-Source
  Searches: Years 2008–2018*, arXiv:2101.09836 (2021).
- Braun et al., *Methods for point source analysis in high energy neutrino
  telescopes*, Astropart. Phys. 29 (2008) 299.
- Gaisser, Engel & Resconi, *Cosmic Rays and Particle Physics*, 2nd ed.,
  Cambridge UP (2016) — analytic atmospheric flux, Eq. 6.7.
- Chirkin, hep-ph/0407078 — Earth-curvature correction cos θ*.
- Fedynitch et al., *MCEq*, EPJ Web Conf. 99 (2015) 08001.
- Abbasi et al. (IceCube), ApJ 928 (2022) 50 — diffuse astrophysical ν_μ flux.
- SkyLLH: https://github.com/icecube/skyllh
