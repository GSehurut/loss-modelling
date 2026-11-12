"""Public benchmark triangles for examples and tests."""

from __future__ import annotations

from .triangle import Triangle

# Taylor, G. C. and Ashe, F. R. (1983). Second moments of estimates of outstanding
# claims. Journal of Econometrics, 23(1), 37-61. Incremental paid amounts; the
# standard benchmark used by Mack (1993) and in the R ChainLadder package ("GenIns").
_TAYLOR_ASHE = [
    [357848, 766940, 610542, 482940, 527326, 574398, 146342, 139950, 227229, 67948],
    [352118, 884021, 933894, 1183289, 445745, 320996, 527804, 266172, 425046],
    [290507, 1001799, 926219, 1016654, 750816, 146923, 495992, 280405],
    [310608, 1108250, 776189, 1562400, 272482, 352053, 206286],
    [443160, 693190, 991983, 769488, 504851, 470639],
    [396132, 937085, 847498, 805037, 705960],
    [440832, 847631, 1131398, 1063269],
    [359480, 1061648, 1443370],
    [376686, 986608],
    [344014],
]


def taylor_ashe() -> Triangle:
    """The Taylor and Ashe (1983) triangle as a cumulative :class:`Triangle`."""
    return Triangle.from_incremental(_TAYLOR_ASHE, origins=range(1, 11))
