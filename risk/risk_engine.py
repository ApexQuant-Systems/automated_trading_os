"""
APEX Quant OS - Layer 6: Math-Only Risk Engine
Calculates position size from SL distance and enforces strict 1% risk & min 1:4 RR.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskParameters:
    is_trade_allowed: bool
    risk_percentage: float
    account_equity: float
    dollar_risk: float
    entry_price: float
    stop_loss_price: float
    target_price: float
    risk_distance: float
    reward_distance: float
    reward_to_risk_ratio: float
    position_size: float
    rejection_reason: str


class RiskEngine:
    """
    Calculates exact risk sizing and enforces 1% equity & RR rules.
    """

    @staticmethod
    def calculate_risk(
        account_equity: float,
        entry_price: float,
        stop_loss_price: float,
        target_price: float,
        risk_percentage: float = 0.01,
        min_rr_ratio: float = 4.0
    ) -> RiskParameters:
        if account_equity <= 0:
            raise ValueError("Account equity must be greater than zero.")

        risk_dist = abs(entry_price - stop_loss_price)
        reward_dist = abs(target_price - entry_price)

        if risk_dist == 0:
            return RiskParameters(
                is_trade_allowed=False,
                risk_percentage=risk_percentage,
                account_equity=account_equity,
                dollar_risk=0.0,
                entry_price=entry_price,
                stop_loss_price=stop_loss_price,
                target_price=target_price,
                risk_distance=0.0,
                reward_distance=reward_dist,
                reward_to_risk_ratio=0.0,
                position_size=0.0,
                rejection_reason="Invalid Stop Loss (Zero Distance)"
            )

        rr_ratio = reward_dist / risk_dist
        dollar_risk = account_equity * risk_percentage
        position_size = dollar_risk / risk_dist

        # Enforce minimum Reward-to-Risk ratio rule (>= 1:4)
        if rr_ratio < min_rr_ratio:
            return RiskParameters(
                is_trade_allowed=False,
                risk_percentage=risk_percentage,
                account_equity=account_equity,
                dollar_risk=dollar_risk,
                entry_price=entry_price,
                stop_loss_price=stop_loss_price,
                target_price=target_price,
                risk_distance=risk_dist,
                reward_distance=reward_dist,
                reward_to_risk_ratio=rr_ratio,
                position_size=position_size,
                rejection_reason=f"RR ratio ({rr_ratio:.2f}) below minimum required (1:{min_rr_ratio:.1f})"
            )

        return RiskParameters(
            is_trade_allowed=True,
            risk_percentage=risk_percentage,
            account_equity=account_equity,
            dollar_risk=dollar_risk,
            entry_price=entry_price,
            stop_loss_price=stop_loss_price,
            target_price=target_price,
            risk_distance=risk_dist,
            reward_distance=reward_dist,
            reward_to_risk_ratio=rr_ratio,
            position_size=position_size,
            rejection_reason="Approved"
        )
