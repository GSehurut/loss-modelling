import numpy as np
import pandas as pd
import pytest

from loss_modelling import Triangle, chain_ladder, mack, taylor_ashe

# Published results for the Taylor and Ashe triangle (Mack, 1993; R ChainLadder "GenIns")
TOTAL_RESERVE = 18_680_856
TOTAL_MACK_SE = 2_447_095


def test_taylor_ashe_total_reserve():
    assert chain_ladder(taylor_ashe()).total_reserve == pytest.approx(TOTAL_RESERVE, rel=1e-6)


def test_taylor_ashe_mack_total_standard_error():
    assert mack(taylor_ashe()).total_std_error == pytest.approx(TOTAL_MACK_SE, rel=1e-4)


def test_oldest_origin_is_fully_developed():
    result = mack(taylor_ashe())
    assert result.reserve[0] == pytest.approx(0.0)
    assert result.std_error[0] == pytest.approx(0.0)


def test_total_se_at_least_root_sum_of_squares():
    # Positive correlation between origins means total SE exceeds independent combination
    result = mack(taylor_ashe())
    assert result.total_std_error >= np.sqrt((result.std_error**2).sum())


def test_from_incremental_cumulates_and_keeps_staircase():
    tri = Triangle.from_incremental([[1, 2, 3], [4, 5], [6]])
    np.testing.assert_allclose(tri.values[0], [1, 3, 6])
    assert np.isnan(tri.values[2, 1])
    np.testing.assert_allclose(tri.latest_diagonal, [6, 9, 6])


def test_from_long_matches_from_incremental():
    movements = pd.DataFrame(
        {
            "uw_year": [2020, 2020, 2020, 2020, 2021, 2021, 2022],
            "dev": [1, 1, 2, 3, 1, 2, 1],
            "amount": [0.5, 0.5, 2, 3, 4, 5, 6],
        }
    )
    tri = Triangle.from_long(movements, "uw_year", "dev", "amount")
    expected = Triangle.from_incremental([[1, 2, 3], [4, 5], [6]])
    np.testing.assert_allclose(tri.values, expected.values)
    assert tri.origins == (2020, 2021, 2022)


def test_from_long_missing_column():
    with pytest.raises(KeyError):
        Triangle.from_long(pd.DataFrame({"a": [1]}), "a", "b", "c")


def test_mack_requires_square():
    with pytest.raises(ValueError):
        mack(Triangle.from_incremental([[1, 2, 3, 4], [1, 2, 3], [1, 2]]))
