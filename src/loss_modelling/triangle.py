"""Claims development triangles."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Triangle:
    """A cumulative claims development triangle.

    ``values[i, j]`` is the cumulative amount for origin period ``i`` at
    development period ``j``. Cells not yet observed are ``NaN``. Origins are
    ordered oldest first, so the latest diagonal runs from top right to bottom left.
    """

    values: np.ndarray
    origins: tuple
    developments: tuple

    def __post_init__(self) -> None:
        v = np.asarray(self.values, dtype=float)
        if v.ndim != 2:
            raise ValueError("values must be two-dimensional")
        if v.shape != (len(self.origins), len(self.developments)):
            raise ValueError("values shape must match origins x developments")
        object.__setattr__(self, "values", v)

    # ----- constructors -------------------------------------------------
    @classmethod
    def from_incremental(
        cls,
        incremental: Sequence[Sequence[float]] | np.ndarray,
        origins: Sequence | None = None,
        developments: Sequence | None = None,
    ) -> Triangle:
        """Build from incremental amounts. Ragged rows (lists) are allowed."""
        rows = [np.asarray(r, dtype=float) for r in incremental]
        width = max(len(r) for r in rows)
        grid = np.full((len(rows), width), np.nan)
        for i, r in enumerate(rows):
            grid[i, : len(r)] = r
        cumulative = np.cumsum(np.nan_to_num(grid), axis=1)
        cumulative[np.isnan(grid)] = np.nan
        return cls(
            cumulative,
            tuple(origins if origins is not None else range(len(rows))),
            tuple(developments if developments is not None else range(1, width + 1)),
        )

    @classmethod
    def from_long(
        cls,
        df: pd.DataFrame,
        origin: str,
        development: str,
        value: str,
        cumulative: bool = False,
    ) -> Triangle:
        """Build from long format data, e.g. claim movements aggregated by origin and period.

        Each row has an origin period, a development period and an amount. If
        ``cumulative`` is False, amounts are treated as incremental movements and
        summed within each cell before accumulating.
        """
        missing = {origin, development, value} - set(df.columns)
        if missing:
            raise KeyError(f"columns not found: {sorted(missing)}")
        grid = df.pivot_table(index=origin, columns=development, values=value, aggfunc="sum")
        grid = grid.sort_index().sort_index(axis=1)
        arr = grid.to_numpy(dtype=float)
        if not cumulative:
            observed = ~np.isnan(arr)
            arr = np.cumsum(np.nan_to_num(arr), axis=1)
            # A cell is observed if any later cell in the row has data, or it does itself
            last_obs = np.where(
                observed.any(axis=1),
                observed.shape[1] - 1 - np.argmax(observed[:, ::-1], axis=1),
                -1,
            )
            cols = np.arange(arr.shape[1])
            arr[cols[None, :] > last_obs[:, None]] = np.nan
        return cls(arr, tuple(grid.index), tuple(grid.columns))

    # ----- views --------------------------------------------------------
    @property
    def latest_diagonal(self) -> np.ndarray:
        """Most recent observed cumulative value for each origin."""
        out = np.empty(self.values.shape[0])
        for i, row in enumerate(self.values):
            observed = row[~np.isnan(row)]
            out[i] = observed[-1] if observed.size else np.nan
        return out

    @property
    def incremental(self) -> np.ndarray:
        """Incremental amounts derived from the cumulative triangle."""
        inc = np.diff(self.values, axis=1, prepend=0.0)
        inc[np.isnan(self.values)] = np.nan
        return inc

    def link_ratios(self) -> np.ndarray:
        """Age to age factors ``C[i, j+1] / C[i, j]`` (NaN where not observed)."""
        with np.errstate(divide="ignore", invalid="ignore"):
            return self.values[:, 1:] / self.values[:, :-1]

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame(self.values, index=list(self.origins), columns=list(self.developments))
