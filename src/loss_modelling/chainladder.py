"""Chain ladder projection and Mack's distribution free standard error.

References
----------
Mack, T. (1993). Distribution-free calculation of the standard error of chain
ladder reserve estimates. ASTIN Bulletin, 23(2), 213-225.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .triangle import Triangle


@dataclass(frozen=True)
class ChainLadderResult:
    factors: np.ndarray  # volume weighted development factors f_j
    projected: np.ndarray  # full square of observed and projected cumulative values
    latest: np.ndarray  # latest observed diagonal
    ultimate: np.ndarray
    reserve: np.ndarray  # ultimate - latest (IBNR + IBNER on an incurred triangle)
    origins: tuple

    @property
    def total_reserve(self) -> float:
        return float(self.reserve.sum())

    def summary(self) -> pd.DataFrame:
        return pd.DataFrame(
            {"latest": self.latest, "ultimate": self.ultimate, "reserve": self.reserve},
            index=list(self.origins),
        )


@dataclass(frozen=True)
class MackResult(ChainLadderResult):
    sigma2: np.ndarray  # variance parameters sigma_j^2
    std_error: np.ndarray  # per origin standard error of the reserve
    total_std_error: float

    def summary(self) -> pd.DataFrame:
        df = super().summary()
        df["std_error"] = self.std_error
        with np.errstate(divide="ignore", invalid="ignore"):
            df["cv"] = np.where(self.reserve > 0, self.std_error / self.reserve, np.nan)
        return df


def chain_ladder(triangle: Triangle) -> ChainLadderResult:
    """Basic chain ladder with volume weighted development factors."""
    c = triangle.values
    n_orig, n_dev = c.shape
    factors = np.ones(n_dev - 1)
    for j in range(n_dev - 1):
        mask = ~np.isnan(c[:, j]) & ~np.isnan(c[:, j + 1])
        denom = c[mask, j].sum()
        if not mask.any() or denom == 0:
            raise ValueError(f"cannot estimate development factor {j} -> {j + 1}")
        factors[j] = c[mask, j + 1].sum() / denom

    projected = c.copy()
    for i in range(n_orig):
        for j in range(n_dev - 1):
            if np.isnan(projected[i, j + 1]):
                projected[i, j + 1] = projected[i, j] * factors[j]

    latest = triangle.latest_diagonal
    ultimate = projected[:, -1]
    return ChainLadderResult(
        factors, projected, latest, ultimate, ultimate - latest, triangle.origins
    )


def mack(triangle: Triangle) -> MackResult:
    """Chain ladder with Mack (1993) standard errors for each origin and the total.

    Requires a square triangle (as many development periods as origins) with
    the usual staircase of observations.
    """
    c = triangle.values
    n = c.shape[0]
    if c.shape != (n, n):
        raise ValueError("Mack's method here requires a square triangle")
    if n < 3:
        raise ValueError("need at least 3 origin periods")

    cl = chain_ladder(triangle)
    f = cl.factors

    # Variance parameters sigma_j^2 (j = 0 .. n-2)
    sigma2 = np.zeros(n - 1)
    for j in range(n - 1):
        rows = n - 1 - j  # origins with both C[i, j] and C[i, j+1]
        if rows > 1:
            cj, cj1 = c[:rows, j], c[:rows, j + 1]
            sigma2[j] = np.sum(cj * (cj1 / cj - f[j]) ** 2) / (rows - 1)
    # Mack's extrapolation for the last factor, which has a single observation
    if n - 1 >= 3:
        a, b = sigma2[n - 3], sigma2[n - 4]
        sigma2[n - 2] = min(a**2 / b if b > 0 else 0.0, min(a, b))
    else:
        sigma2[n - 2] = sigma2[n - 3]

    # Column sums S_j over origins observed at j and j+1
    s = np.array([c[: n - 1 - j, j].sum() for j in range(n - 1)])
    chat = cl.projected
    ult = cl.ultimate

    mse = np.zeros(n)
    for i in range(1, n):
        js = range(n - 1 - i, n - 1)
        mse[i] = ult[i] ** 2 * sum(sigma2[j] / f[j] ** 2 * (1 / chat[i, j] + 1 / s[j]) for j in js)

    total_mse = mse.sum()
    for i in range(1, n):
        younger = ult[i + 1 :].sum()
        js = range(n - 1 - i, n - 1)
        total_mse += 2 * ult[i] * younger * sum(sigma2[j] / f[j] ** 2 / s[j] for j in js)

    return MackResult(
        factors=cl.factors,
        projected=cl.projected,
        latest=cl.latest,
        ultimate=cl.ultimate,
        reserve=cl.reserve,
        origins=cl.origins,
        sigma2=sigma2,
        std_error=np.sqrt(mse),
        total_std_error=float(np.sqrt(total_mse)),
    )
