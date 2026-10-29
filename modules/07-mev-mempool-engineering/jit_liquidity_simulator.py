#!/usr/bin/env python3
"""
Uniswap v3 Just-In-Time (JIT) Liquidity MEV Simulator
Demonstrates:
1. Concentrated liquidity mechanics (virtual reserves within active tick)
2. Passive LP fee distribution vs predatory JIT front-running
3. Atomic bundle execution:
   - Tx 1 (Front-run): Searcher mints hyper-concentrated liquidity in target tick
   - Tx 2 (Victim): Large swap transaction executes, paying 0.3% fee to pool
   - Tx 3 (Back-run): Searcher burns liquidity position, harvesting fee share
4. Impact analysis: Passive LP fee dilution and net searcher profitability
"""

from typing import Dict


class ConcentratedPool:
    def __init__(self, passive_liquidity: float, fee_rate: float = 0.003):
        self.passive_liquidity = passive_liquidity
        self.jit_liquidity = 0.0
        self.fee_rate = fee_rate
        self.accumulated_fees = 0.0

    @property
    def total_liquidity(self) -> float:
        return self.passive_liquidity + self.jit_liquidity

    def mint_jit_liquidity(self, amount: float):
        self.jit_liquidity += amount

    def burn_jit_liquidity(self) -> float:
        burned = self.jit_liquidity
        self.jit_liquidity = 0.0
        return burned

    def execute_swap(self, trade_volume_usd: float) -> float:
        fee = trade_volume_usd * self.fee_rate
        self.accumulated_fees += fee
        return fee


def simulate_jit_attack(
    passive_pool_liquidity: float = 500_000.0,
    victim_trade_usd: float = 1_000_000.0,
    jit_capital_multiplier: float = 10.0  # Searcher injects 10x the passive liquidity
) -> Dict[str, float]:
    # Baseline Scenario: Without JIT Searcher (Honest Passive LPs get 100% of fees)
    honest_pool = ConcentratedPool(passive_liquidity=passive_pool_liquidity)
    baseline_fees = honest_pool.execute_swap(victim_trade_usd)
    passive_lp_baseline_fee = baseline_fees

    # JIT Attack Scenario:
    jit_pool = ConcentratedPool(passive_liquidity=passive_pool_liquidity)

    # Step 1: Front-run - Inject massive temporary liquidity
    jit_amount = passive_pool_liquidity * jit_capital_multiplier
    jit_pool.mint_jit_liquidity(jit_amount)

    # Step 2: Victim Swap executes
    total_fee_generated = jit_pool.execute_swap(victim_trade_usd)

    # Step 3: Fee distribution based on proportional liquidity share
    jit_share = jit_pool.jit_liquidity / jit_pool.total_liquidity
    passive_share = jit_pool.passive_liquidity / jit_pool.total_liquidity

    searcher_fee_captured = total_fee_generated * jit_share
    passive_lp_remaining_fee = total_fee_generated * passive_share

    # Step 4: Back-run - Burn JIT liquidity
    jit_pool.burn_jit_liquidity()

    # Estimate gas cost for 2 transactions (mint + burn): ~250,000 gas total at 30 gwei
    gas_cost_usd = (250_000 * 30e-9) * 3000.0  # ETH at $3000 = ~$22.50
    net_profit_usd = searcher_fee_captured - gas_cost_usd

    return {
        "trade_volume_usd": victim_trade_usd,
        "total_fee_generated": total_fee_generated,
        "passive_baseline_fee": passive_lp_baseline_fee,
        "passive_fee_with_jit": passive_lp_remaining_fee,
        "fee_dilution_pct": (1.0 - (passive_lp_remaining_fee / passive_lp_baseline_fee)) * 100.0,
        "searcher_gross_fee": searcher_fee_captured,
        "gas_cost_usd": gas_cost_usd,
        "searcher_net_profit": net_profit_usd,
    }


if __name__ == "__main__":
    print("=== Uniswap v3 Just-In-Time (JIT) Liquidity MEV Simulation ===")
    TRADE_SIZE = 2_000_000.0  # $2 Million victim swap
    PASSIVE_DEPTH = 500_000.0  # $500k existing passive pool depth

    print(f"[+] Active Tick Depth  : ${PASSIVE_DEPTH:,.0f} USD")
    print(f"[+] Incoming Swap Size : ${TRADE_SIZE:,.0f} USD (0.3% fee = ${TRADE_SIZE * 0.003:,.0f})")

    res = simulate_jit_attack(
        passive_pool_liquidity=PASSIVE_DEPTH,
        victim_trade_usd=TRADE_SIZE,
        jit_capital_multiplier=9.0  # Searcher injects $4.5M (90% of final pool)
    )

    print(f"\n[+] Execution & Fee Dilution Metrics:")
    print(f"    - Total Fee Generated         : ${res['total_fee_generated']:,.2f}")
    print(f"    - Passive LP Fee (Normal)     : ${res['passive_baseline_fee']:,.2f}")
    print(f"    - Passive LP Fee (Under JIT)  : ${res['passive_fee_with_jit']:,.2f}")
    print(f"    - Passive LP Revenue Dilution : -{res['fee_dilution_pct']:.1f}% SIPHONED!")
    print(f"\n[+] Searcher Economics:")
    print(f"    - Gross Fee Harvested         : ${res['searcher_gross_fee']:,.2f}")
    print(f"    - Gas Overhead (Mint + Burn)  : ${res['gas_cost_usd']:.2f}")
    print(f"    - Net Searcher Profit         : +${res['searcher_net_profit']:,.2f} in 1 block!")

    assert res["searcher_net_profit"] > 0, "JIT attack should be highly profitable"
    assert res["fee_dilution_pct"] >= 90.0, "Searcher should siphon >=90% of pool fee"
    print("[SUCCESS] JIT liquidity attack and fee extraction mechanics verified.")
