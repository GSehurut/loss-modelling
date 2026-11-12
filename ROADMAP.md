# Roadmap

Items marked **good first issue** are well scoped for new contributors. Please open or comment on an issue before starting so work is not duplicated.

## 0.2: more reserving methods

- [ ] **Bornhuetter-Ferguson** with a priori loss ratios and exposure (premium) inputs
- [ ] **Cape Cod** (Stanard-Bühlmann)
- [ ] **Simple average and medial average** development factors as alternatives to volume weighted **(good first issue)**
- [ ] **Tail factors:** user supplied and curve fitted (exponential decay, inverse power)
- [ ] Factor exclusions (drop specific link ratios with a reason recorded)

## 0.3: uncertainty

- [ ] **Bootstrap ODP** (England and Verrall, 2002) giving a full reserve distribution
- [ ] Mack residual diagnostics and plots
- [ ] One year (Merz-Wüthrich) reserve risk

## Data handling

- [ ] Helper to compute development periods from origin and transaction dates (monthly, quarterly, annual) **(good first issue)**
- [ ] Non-square triangles and calendar year views
- [ ] Paid versus incurred side by side, with paid to incurred ratios **(good first issue)**
- [ ] More public benchmark triangles (for example the CAS loss reserving database) **(good first issue)**

## Documentation

- [ ] Plot helpers for triangles and development patterns (optional matplotlib)
- [ ] Example notebook: reserving end to end from synthetic claim movements
- [ ] Documentation site (MkDocs) with worked examples

## Done

- [x] `Triangle` from incremental arrays and long format movements
- [x] Volume weighted chain ladder
- [x] Mack standard errors, validated against Taylor and Ashe published results
