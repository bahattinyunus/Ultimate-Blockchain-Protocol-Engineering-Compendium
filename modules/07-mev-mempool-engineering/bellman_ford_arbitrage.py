#!/usr/bin/env python3
"""
Graph-based Cross-DEX Triangular & Cyclic Arbitrage Detection
Uses Bellman-Ford algorithm over negative log transformed exchange rates:
weight(A -> B) = -ln(Rate(A -> B) * (1 - fee))
A negative weight cycle in this graph corresponds to a profitable arbitrage loop:
Product(Rate_i * (1 - fee_i)) > 1.0
"""

import math
from typing import Dict, List, Optional, Tuple


class Edge:
    def __init__(self, u: str, v: str, rate: float, fee: float = 0.003):
        self.u = u
        self.v = v
        self.rate = rate
        self.fee = fee
        # Effective conversion multiplier after fee
        self.effective_rate = rate * (1.0 - fee)
        # Weight in additive shortest-path graph
        self.weight = -math.log(self.effective_rate)

    def __repr__(self):
        return f"{self.u}->{self.v} (rate={self.rate}, net={self.effective_rate:.4f})"


class ArbitrageGraph:
    def __init__(self, tokens: List[str]):
        self.tokens = tokens
        self.edges: List[Edge] = []

    def add_pool(self, token_a: str, token_b: str, rate_a_to_b: float, fee: float = 0.003):
        """Adds directional pair rates between tokens."""
        self.edges.append(Edge(token_a, token_b, rate_a_to_b, fee))
        self.edges.append(Edge(token_b, token_a, 1.0 / rate_a_to_b, fee))

    def find_arbitrage_cycle(self, source_token: str) -> Optional[Tuple[List[str], float]]:
        """
        Runs Bellman-Ford algorithm to find negative cycles reachable from source_token.
        Returns: (cycle_tokens_path, profit_multiplier)
        """
        dist: Dict[str, float] = {t: float("inf") for t in self.tokens}
        parent: Dict[str, Optional[str]] = {t: None for t in self.tokens}
        parent_edge: Dict[str, Optional[Edge]] = {t: None for t in self.tokens}
        dist[source_token] = 0.0

        # Relax edges V-1 times
        for _ in range(len(self.tokens) - 1):
            for edge in self.edges:
                if dist[edge.u] + edge.weight < dist[edge.v]:
                    dist[edge.v] = dist[edge.u] + edge.weight
                    parent[edge.v] = edge.u
                    parent_edge[edge.v] = edge

        # Check for negative cycle on V-th iteration
        cycle_node = None
        for edge in self.edges:
            if dist[edge.u] + edge.weight < dist[edge.v]:
                cycle_node = edge.v
                break

        if cycle_node is None:
            return None  # No profitable cycle

        # Trace back to find actual cycle
        visited: Dict[str, bool] = {t: False for t in self.tokens}
        curr = cycle_node
        for _ in range(len(self.tokens)):
            curr = parent[curr]

        cycle: List[str] = []
        cycle_start = curr
        node = cycle_start
        multiplier = 1.0

        while True:
            cycle.append(node)
            p = parent[node]
            edge = parent_edge[node]
            multiplier *= edge.effective_rate
            node = p
            if node == cycle_start and len(cycle) > 1:
                cycle.append(node)
                break

        cycle.reverse()
        return cycle, multiplier


if __name__ == "__main__":
    print("=== Graph-based DEX Cyclic Arbitrage Engine ===")
    tokens = ["WETH", "USDC", "WBTC", "DAI"]
    graph = ArbitrageGraph(tokens)

    # Market prices with an intentional price discrepancy:
    # Uniswap: WETH -> USDC = 3000
    # Sushiswap: USDC -> WBTC = 0.000016666 (WBTC = 60,000 USDC)
    # Curve: WBTC -> WETH = 20.8 (Discrepancy! Fair is 20.0 WETH/WBTC)
    graph.add_pool("WETH", "USDC", rate_a_to_b=3000.0, fee=0.003)
    graph.add_pool("USDC", "WBTC", rate_a_to_b=1.0 / 60000.0, fee=0.003)
    graph.add_pool("WBTC", "WETH", rate_a_to_b=20.8, fee=0.003)
    graph.add_pool("USDC", "DAI", rate_a_to_b=1.0001, fee=0.0005)

    print("[+] Scanning liquidity pools for cyclic arbitrage...")
    res = graph.find_arbitrage_cycle("WETH")

    if res:
        cycle_path, profit_mult = res
        net_profit_pct = (profit_mult - 1.0) * 100.0
        print(f"[+] Arbitrage Opportunity Detected!")
        print(f"    - Execution Cycle : {' -> '.join(cycle_path)}")
        print(f"    - Multiplier      : {profit_mult:.5f}x")
        print(f"    - Net Profit      : +{net_profit_pct:.3f}% (After 0.3% pool fees)")

        # Profit validation
        assert profit_mult > 1.0, "Arbitrage path must yield positive profit"
        print("[SUCCESS] Bellman-Ford cyclic arbitrage detector verified.")
    else:
        print("[-] No arbitrage opportunities found.")
