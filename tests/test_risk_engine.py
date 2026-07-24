"""
APEX Quant OS - Unit Test: RiskEngine
Verifies position sizing calculation, 1% account risk, and 1:4 RR enforcement.
"""

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

    print("\n--- RISK ENGINE PARAMETERS VERIFIED ---")
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
