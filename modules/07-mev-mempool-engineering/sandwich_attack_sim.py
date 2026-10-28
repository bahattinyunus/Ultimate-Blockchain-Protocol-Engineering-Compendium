#!/usr/bin/env python3
"""
Uniswap v2 AMM Constant Product Sandwich Attack Simulator
Demonstrates:
1. Exact AMM pricing invariant: (x + dx * 0.997) * (y - dy) = k
2. Victim transaction parameters: input amount dx_victim, slippage tolerance S
3. Searcher optimization: calculating front-run input dx_front that drives
   victim's output to the exact slippage boundary
4. Back-run swap: selling acquired tokens back into the pool to realize risk-free MEV
"""

import math
from typing import Dict, Tuple

FEE = 0.003  # 0.3% Uniswap v2 swap fee
GAMMA = 1.0 - FEE  # 0.997


class UniswapV2Pool:
    def __init__(self, reserve_x: float, reserve_y: float):
        self.rx = reserve_x
        self.ry = reserve_y

    def get_amount_out(self, amount_in: float, in_token: str) -> float:
        """Computes dy given dx with fee deduction: dy = (y * dx * 0.997) / (x + dx * 0.997)"""
        if in_token == "X":
            rin, rout = self.rx, self.ry
        else:
            rin, rout = self.ry, self.rx

        amount_in_with_fee = amount_in * 997.0
        numerator = amount_in_with_fee * rout
        denominator = (rin * 1000.0) + amount_in_with_fee
        return numerator / denominator

    def swap(self, amount_in: float, in_token: str) -> float:
        amount_out = self.get_amount_out(amount_in, in_token)
        if in_token == "X":
            self.rx += amount_in
            self.ry -= amount_out
        else:
            self.ry += amount_in
            self.rx -= amount_out
        return amount_out


def find_optimal_frontrun(
    reserve_x: float,
    reserve_y: float,
    victim_dx: float,
    slippage_tolerance: float
) -> float:
    """Finds the maximum front-run dx such that victim's output >= min_dy using binary search."""
    baseline = UniswapV2Pool(reserve_x, reserve_y)
    min_dy = baseline.get_amount_out(victim_dx, "X") * (1.0 - slippage_tolerance)

    low = 0.0
    high = reserve_x * 0.5  # Upper bound
    best_dx = 0.0

    for _ in range(60):
        mid = (low + high) / 2.0
        test_pool = UniswapV2Pool(reserve_x, reserve_y)
        test_pool.swap(mid, "X")
        actual_dy = test_pool.get_amount_out(victim_dx, "X")

        if actual_dy >= min_dy:
            best_dx = mid
            low = mid
        else:
            high = mid

    # Subtract tiny safety delta so victim doesn't revert due to rounding
    return max(0.0, best_dx - 0.001)


def simulate_sandwich(
    reserve_x: float,
    reserve_y: float,
    victim_dx: float,
    slippage_tolerance: float = 0.02,  # 2% slippage
    frontrun_dx: float = 0.0
) -> Dict[str, float]:
    if frontrun_dx <= 0.0:
        frontrun_dx = find_optimal_frontrun(reserve_x, reserve_y, victim_dx, slippage_tolerance)

    # Baseline: Victim trading alone
    baseline_pool = UniswapV2Pool(reserve_x, reserve_y)
    expected_dy = baseline_pool.get_amount_out(victim_dx, "X")
    min_dy = expected_dy * (1.0 - slippage_tolerance)

    # Sandwich Execution
    attack_pool = UniswapV2Pool(reserve_x, reserve_y)

    # Step 1: Front-run
    attacker_dy = attack_pool.swap(frontrun_dx, "X")

    # Step 2: Victim Swap
    victim_actual_dy = attack_pool.swap(victim_dx, "X")

    # Verify victim transaction does not revert
    victim_reverted = victim_actual_dy < min_dy

    # Step 3: Back-run (Attacker dumps acquired Y tokens)
    attacker_dx_out = attack_pool.swap(attacker_dy, "Y")
    gross_profit_x = attacker_dx_out - frontrun_dx

    return {
        "expected_victim_dy": expected_dy,
        "min_victim_dy": min_dy,
        "victim_actual_dy": victim_actual_dy,
        "victim_reverted": victim_reverted,
        "victim_loss_dy": expected_dy - victim_actual_dy,
        "attacker_frontrun_in": frontrun_dx,
        "attacker_backrun_out": attacker_dx_out,
        "gross_profit_x": gross_profit_x,
    }


if __name__ == "__main__":
    print("=== Uniswap v2 AMM Sandwich Attack Simulator ===")
    INITIAL_RX = 1000.0  # 1000 WETH
    INITIAL_RY = 3000000.0  # 3,000,000 USDC ($3000 / ETH)
    VICTIM_DX = 20.0  # Victim buying USDC with 20 WETH
    SLIPPAGE = 0.01  # 1% slippage tolerance

    print(f"[+] Initial Pool Reserves: {INITIAL_RX} WETH | {INITIAL_RY:,.0f} USDC")
    print(f"[+] Victim swaps {VICTIM_DX} WETH for USDC with {SLIPPAGE*100:.1f}% max slippage...")

    # Attacker calculates optimal frontrun amount dynamically
    res = simulate_sandwich(INITIAL_RX, INITIAL_RY, VICTIM_DX, slippage_tolerance=SLIPPAGE)

    print(f"\n[+] Sandwich Execution Results:")
    print(f"    - Victim Expected Output : {res['expected_victim_dy']:,.2f} USDC")
    print(f"    - Victim Minimum Output  : {res['min_victim_dy']:,.2f} USDC")
    print(f"    - Victim Actual Output   : {res['victim_actual_dy']:,.2f} USDC")
    print(f"    - Transaction Reverted   : {res['victim_reverted']}")
    print(f"    - Victim Value Siphoned  : {res['victim_loss_dy']:,.2f} USDC")
    print(f"\n[+] Searcher Profitability:")
    print(f"    - Optimal Front-run In   : {res['attacker_frontrun_in']:.4f} WETH")
    print(f"    - Back-run Out           : {res['attacker_backrun_out']:.4f} WETH")
    print(f"    - Gross Searcher Profit  : +{res['gross_profit_x']:.4f} WETH (~${res['gross_profit_x']*3000:.2f})")

    assert not res["victim_reverted"], "Front-run was too large, victim transaction reverted!"
    assert res["gross_profit_x"] > 0, "Sandwich must extract positive gross profit"
    print("[SUCCESS] Sandwich attack mechanics verified.")
