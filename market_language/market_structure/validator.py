"""
APEX Quant OS - Engine 11: Structure Validator
The Structural Invariant Firewall. Ensures zero invalid states propagate downstream.
"""

from typing import List, Optional, Tuple
from market_language.market_structure.models import DealingRange, StructuralAnchors, TrendDirection, TrendState


class StructureValidator:
    """
    Asserts core structural invariants before state publication.
    """

    @staticmethod
    def validate_state(
        trend: TrendState,
        anchors: StructuralAnchors,
        dealing_range: Optional[DealingRange]
    ) -> Tuple[bool, List[str]]:
        """
        Validates all structural invariants. Returns (is_valid, error_list).
        """
        errors: List[str] = []

        # Invariant 1: Range High must be greater than Range Low if range exists
        if dealing_range is not None:
            if dealing_range.high_price <= dealing_range.low_price:
                errors.append(f"INVARIANT VIOLATION: Range High ({dealing_range.high_price}) <= Range Low ({dealing_range.low_price})")

            if dealing_range.spread <= 0:
                errors.append(f"INVARIANT VIOLATION: Dealing Range spread must be strictly positive. Got: {dealing_range.spread}")

        # Invariant 2: In Bullish trend, Protected Low must exist if external low exists
        if trend.direction == TrendDirection.BULLISH and anchors.current_external_low:
            if anchors.protected_low is None:
                errors.append("INVARIANT VIOLATION: Active Bullish Trend missing Protected Low anchor.")

        # Invariant 3: In Bearish trend, Protected High must exist if external high exists
        if trend.direction == TrendDirection.BEARISH and anchors.current_external_high:
            if anchors.protected_high is None:
                errors.append("INVARIANT VIOLATION: Active Bearish Trend missing Protected High anchor.")

        is_valid = len(errors) == 0
        return is_valid, errors
