"""
APEX Quant OS - Engine 2: Relationship Engine
Evaluates structural progression by labeling sequential swings as HH, HL, LH, LL, EQH, or EQL.
"""

from typing import List
from market_language.market_structure.models import (
    Swing,
    SwingOrientation,
    SwingRelationshipType,
)
from market_language.market_structure.policy import MarketStructurePolicy


class RelationshipEngine:
    """
    Compares consecutive swings of identical orientation to mark geometric progress.
    """

    @staticmethod
    def evaluate_relationships(
        swings: List[Swing],
        policy: MarketStructurePolicy
    ) -> List[Swing]:
        """
        Mutates/assigns the `relationship` attribute of each swing in-place based on its predecessor.
        """
        last_high: Optional[Swing] = None
        last_low: Optional[Swing] = None

        for swing in swings:
            if swing.orientation == SwingOrientation.HIGH:
                if last_high is not None:
                    prev_p = last_high.price_point.price
                    curr_p = swing.price_point.price
                    diff_pct = abs(curr_p - prev_p) / prev_p

                    if diff_pct <= policy.equal_price_tolerance_pct:
                        swing.relationship = SwingRelationshipType.EQH
                    elif curr_p > prev_p:
                        swing.relationship = SwingRelationshipType.HH
                    else:
                        swing.relationship = SwingRelationshipType.LH
                last_high = swing

            elif swing.orientation == SwingOrientation.LOW:
                if last_low is not None:
                    prev_p = last_low.price_point.price
                    curr_p = swing.price_point.price
                    diff_pct = abs(curr_p - prev_p) / prev_p

                    if diff_pct <= policy.equal_price_tolerance_pct:
                        swing.relationship = SwingRelationshipType.EQL
                    elif curr_p < prev_p:
                        swing.relationship = SwingRelationshipType.LL
                    else:
                        swing.relationship = SwingRelationshipType.HL
                last_low = swing

        return swings
