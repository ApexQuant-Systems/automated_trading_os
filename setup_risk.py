import os

os.makedirs('risk', exist_ok=True)
os.makedirs('tests', exist_ok=True)

risk_code = """\"\"\"
APEX Quant OS - Layer 6: Math-Only Risk Engine
Calculates position size from SL distance and enforces strict 1% risk & min 1:4 RR.
\"\"\"

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
    \"\"\"
    Calculates exact risk sizing and enforces 1% equity & RR rules.
    \"\"\"

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
"""

test_risk_code = """\"\"\"
APEX Quant OS - Unit Test: RiskEngine
Verifies position sizing calculation, 1% account risk, and 1:4 RR enforcement.
\"\"\"

import os
import sys
sys.path.insert(0, os.path.abspath("."))

from risk.risk_engine import RiskEngine


def test_risk_engine_calculation():
    print("Executing tests/test_risk_engine.py...")

    account_equity = 100.0  # $100 Account
    entry_price = 100.0
    stop_loss_price = 98.0  # Risk distance = $2.00
    target_price = 110.0   # Reward distance = $10.00 (RR = 1:5)

    # 1. Test Valid Setup (RR = 1:5 >= 1:4)
    risk_params = RiskEngine.calculate_risk(
        account_equity=account_equity,
        entry_price=entry_price,
        stop_loss_price=stop_loss_price,
        target_price=target_price,
        risk_percentage=0.01,
        min_rr_ratio=4.0
    )

    assert risk_params.is_trade_allowed is True
    assert risk_params.dollar_risk == 1.0  # 1% of $100 = $1.00
    assert risk_params.reward_to_risk_ratio == 5.0
    assert risk_params.position_size == 0.5  # $1.00 / $2.00 distance = 0.5 units

    # 2. Test Rejection Low RR (Target = 105.0 -> RR = 1:2.5 < 1:4)
    low_rr_params = RiskEngine.calculate_risk(
        account_equity=account_equity,
        entry_price=entry_price,
        stop_loss_price=stop_loss_price,
        target_price=105.0,
        risk_percentage=0.01,
        min_rr_ratio=4.0
    )

    assert low_rr_params.is_trade_allowed is False
    assert "below minimum required" in low_rr_params.rejection_reason

    print("\\n--- RISK ENGINE PARAMETERS VERIFIED ---")
    print(f" Account Equity:    ${risk_params.account_equity:.2f}")
    print(f" Dollar Risk (1%):  ${risk_params.dollar_risk:.2f}")
    print(f" Position Size:     {risk_params.position_size:.4f} units")
    print(f" Reward-to-Risk:    1:{risk_params.reward_to_risk_ratio:.1f}")
    print(f" Trade Allowed:     {risk_params.is_trade_allowed}")
    print(f" Rejection Test:    {low_rr_params.rejection_reason}")
    print("--------------------------------------------")
    print("  ✅ PASS: test_risk_engine_calculation Passed!")


if __name__ == "__main__":
    test_risk_engine_calculation()
"""

with open('risk/risk_engine.py', 'w') as f:
    f.write(risk_code)

with open('tests/test_risk_engine.py', 'w') as f:
    f.write(test_risk_code)

print("  ✅ SUCCESS: Risk Engine & Unit Test generated cleanly!")
