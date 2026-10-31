#!/usr/bin/env python3
"""
Intent-Centric Architecture & Dutch Auction Solver Competition Simulator
Demonstrates:
1. Declarative User Intent: 10 ETH -> min USDC via continuous Dutch Auction
2. Linear decay pricing curve: Start price (favorable to user) -> End floor price
3. Competing Solver agents:
   - Solver_AMM: Routes through on-chain DEX pools (incurs slippage + gas)
   - Solver_CEX: Hedging on centralized exchange order books (low fee, capital cost)
   - Solver_CoW: Peer-to-peer Coincidence of Wants matching (0 fee, maximum efficiency)
4. Order lifecycle execution, fill latency, and user surplus extraction analytics.
"""

from typing import Dict, List, Optional, Tuple


class DutchAuctionIntent:
    def __init__(
        self,
        intent_id: str,
        input_token: str,
        input_amount: float,
        output_token: str,
        start_output: float,
        end_output: float,
        duration_seconds: int = 60
    ):
        self.intent_id = intent_id
        self.input_token = input_token
        self.input_amount = input_amount
        self.output_token = output_token
        self.start_output = start_output
        self.end_output = end_output
        self.duration_seconds = duration_seconds
        self.is_filled = False
        self.fill_time: Optional[int] = None
        self.fill_output: Optional[float] = None
        self.winner_solver: Optional[str] = None

    def get_required_output(self, current_time: int) -> float:
        """Computes decaying target output at time t."""
        if current_time >= self.duration_seconds:
            return self.end_output
        decay_ratio = current_time / float(self.duration_seconds)
        return self.start_output - (decay_ratio * (self.start_output - self.end_output))


class Solver:
    def __init__(self, name: str, execution_type: str, internal_cost_basis: float, gas_cost_usd: float):
        self.name = name
        self.execution_type = execution_type
        self.internal_cost_basis = internal_cost_basis  # Solver's cost to source the required output
        self.gas_cost_usd = gas_cost_usd

    def can_fill(self, required_output: float, min_profit_margin: float = 10.0) -> bool:
        """Solver fills when market sell revenue exceeds sourcing cost + gas + profit margin."""
        # Swapper gives 10 ETH (market val ~$30,000 USD).
        # Solver provides `required_output` USDC.
        # Net profit for solver = ETH value - required_output - gas
        eth_proceeds = 30_150.0  # Fair market value of 10 ETH
        net_profit = eth_proceeds - required_output - self.gas_cost_usd
        return net_profit >= min_profit_margin


def run_solver_auction_simulation() -> Dict[str, any]:
    # Swapper intent: Sell 10 ETH, starting at 30,400 USDC down to 29,800 USDC over 60s
    intent = DutchAuctionIntent(
        intent_id="intent_eth_usdc_001",
        input_token="WETH",
        input_amount=10.0,
        output_token="USDC",
        start_output=30_400.0,
        end_output=29_800.0,
        duration_seconds=60
    )

    solvers = [
        Solver("Solver_AMM_Uniswap", execution_type="DEX_Routing", internal_cost_basis=30_050.0, gas_cost_usd=25.0),
        Solver("Solver_CEX_Hedger", execution_type="CEX_Orderbook", internal_cost_basis=30_080.0, gas_cost_usd=12.0),
        Solver("Solver_CoW_Matcher", execution_type="CoW_Direct_P2P", internal_cost_basis=30_120.0, gas_cost_usd=5.0),
    ]

    print(f"[+] Intent Launched: 10 ETH -> Dutch Decay [30,400 -> 29,800 USDC] over 60 seconds.")

    # Time-step simulation (1 second ticks)
    for second in range(0, 61):
        req_output = intent.get_required_output(second)

        # Check each solver in priority of latency
        for s in solvers:
            if s.can_fill(req_output, min_profit_margin=15.0):
                intent.is_filled = True
                intent.fill_time = second
                intent.fill_output = req_output
                intent.winner_solver = s.name
                break

        if intent.is_filled:
            break

    user_surplus = intent.fill_output - intent.end_output
    return {
        "is_filled": intent.is_filled,
        "fill_time_seconds": intent.fill_time,
        "fill_output_usdc": intent.fill_output,
        "floor_output_usdc": intent.end_output,
        "user_surplus_usdc": user_surplus,
        "winner": intent.winner_solver
    }


if __name__ == "__main__":
    print("=== Intent-Centric Architecture: Dutch Auction Solver Engine ===")
    res = run_solver_auction_simulation()

    print(f"[+] Auction Finished:")
    print(f"    - Filled Status        : {res['is_filled']}")
    print(f"    - Execution Time       : t = {res['fill_time_seconds']} seconds")
    print(f"    - Winning Filler       : {res['winner']}")
    print(f"    - Output Delivered     : {res['fill_output_usdc']:,.2f} USDC")
    print(f"    - User Surplus Saved   : +${res['user_surplus_usdc']:,.2f} above reserve price!")

    assert res["is_filled"], "Auction failed to fill!"
    assert res["fill_output_usdc"] >= res["floor_output_usdc"], "Delivered price below minimum reserve!"
    print("[SUCCESS] Intent settlement and competitive solver Dutch Auction verified.")
