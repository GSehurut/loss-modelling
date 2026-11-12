# loss-modelling

[![CI](https://github.com/GSehurut/loss-modelling/actions/workflows/ci.yml/badge.svg)](https://github.com/GSehurut/loss-modelling/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Claims development triangles, chain ladder projections and reserve uncertainty in plain, readable Python.

The goal is a small library that actuaries, students and data engineers can read end to end: every method is a short function with a reference to the paper or textbook it comes from, and tests check results against published benchmarks.

## Features

- **`Triangle`**: build from incremental arrays or from long format claim movements (for example the output of a SQL query), with link ratios, latest diagonal and incremental views
- **Chain ladder** with volume weighted development factors
- **Mack (1993)** distribution free standard errors for each origin and the total reserve
- **Benchmark data:** the Taylor and Ashe (1983) triangle, with tests that reproduce Mack's published results

## Quick start

```sh
pip install git+https://github.com/GSehurut/loss-modelling.git
```

```python
from loss_modelling import mack, taylor_ashe

result = mack(taylor_ashe())
print(result.summary().round(0))
print(f"Total reserve {result.total_reserve:,.0f} +/- {result.total_std_error:,.0f}")
# Total reserve 18,680,856 +/- 2,447,095
```

### From claim movements

```python
import pandas as pd
from loss_modelling import Triangle, chain_ladder

movements = pd.read_csv("claim_movements.csv")  # uw_year, dev_quarter, incurred_movement
tri = Triangle.from_long(
    movements, origin="uw_year", development="dev_quarter", value="incurred_movement"
)
print(chain_ladder(tri).summary())
```

## Contributing

There is plenty to do, from adding Bornhuetter-Ferguson to plotting helpers. See [CONTRIBUTING.md](CONTRIBUTING.md), the [roadmap](ROADMAP.md) and issues labelled [`good first issue`](https://github.com/GSehurut/loss-modelling/labels/good%20first%20issue).

## References

- Mack, T. (1993). Distribution-free calculation of the standard error of chain ladder reserve estimates. *ASTIN Bulletin*, 23(2), 213 to 225.
- Taylor, G. C. and Ashe, F. R. (1983). Second moments of estimates of outstanding claims. *Journal of Econometrics*, 23(1), 37 to 61.
- Friedland, J. (2010). *Estimating Unpaid Claims Using Basic Techniques*. Casualty Actuarial Society.
- [Data modelling for insurance analytics](https://gsehurut.github.io/blog/2026/10/05/data-modelling-insurance-analytics/), on building triangles from claim movements.

The R [ChainLadder](https://github.com/mages/ChainLadder) package and Python [chainladder](https://github.com/casact/chainladder-python) are mature, feature rich alternatives. This project favours readability and teaching value over breadth.

## Licence

MIT. See [LICENSE](LICENSE).
