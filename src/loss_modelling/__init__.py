"""loss-modelling: claims triangles, chain ladder and reserve uncertainty."""

from .chainladder import ChainLadderResult, MackResult, chain_ladder, mack
from .datasets import taylor_ashe
from .triangle import Triangle

__all__ = ["ChainLadderResult", "MackResult", "Triangle", "chain_ladder", "mack", "taylor_ashe"]

__version__ = "0.1.0"
