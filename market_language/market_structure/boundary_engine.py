"""
APEX Quant OS - Engine 7: Boundary Engine
Calculates active Dealing Range boundaries (Range High, Range Low) and Equilibrium (50%).
"""

from typing import Optional
from market_language.market_structure.models import DealingRange, StructuralAnchors


class BoundaryEngine:
    """
    Computes the active operating price range from structural anchors.
    """

    @staticmethod
    def compute_dealing_range(anchors: StructuralAnchors) -> Optional[DealingRange]:
        """
        Calculates Dealing Range metrics using active external high/low anchors.
        """
        if not anchors.current_external_high or not anchors.current_external_low:
            return None

        high_p = anchors.current_external_high.price_point.price
        low_p = anchors.current_external_low.price_point.price

        if high_p <= low_p:
            return None

        spread = high_p - low_p
        eq = (high_p + low_p) / 2.0

        return DealingRange(
            high_price=high_p,
            low_price=low_p,
            equilibrium_price=eq,
            spread=spread
        )
