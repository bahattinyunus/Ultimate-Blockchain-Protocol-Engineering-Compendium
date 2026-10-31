#!/usr/bin/env python3
"""
EigenLayer / Shared Security & Cascading Slashing Simulator
Demonstrates:
1. Multi-asset Restaking pool (ETH, stETH, rETH) with price weighting
2. Operator delegation and multi-AVS commitment (EigenDA, Oracle, ZK-Bridge)
3. Quorum threshold evaluation for AVS task finality (67% super-majority)
4. Cascading Slashing Contagion: How a single AVS violation drains operator collateral
   across all shared services and impacts system-wide security thresholds.
"""

from typing import Dict, List, Set, Tuple


class AVS:
    def __init__(self, name: str, min_security_eth: float, quorum_pct: float = 0.67):
        self.name = name
        self.min_security_eth = min_security_eth
        self.quorum_pct = quorum_pct
        self.enrolled_operators: Set[str] = set()
        self.completed_tasks = 0

    def enroll(self, operator_name: str):
        self.enrolled_operators.add(operator_name)


class Operator:
    def __init__(self, name: str, native_eth: float, st_eth: float, r_eth: float):
        self.name = name
        self.native_eth = native_eth
        self.st_eth = st_eth
        self.r_eth = r_eth
        self.is_frozen = False
        self.slashed_history: List[Tuple[str, float]] = []

    def total_weight_eth(self, st_eth_ratio: float = 1.0, r_eth_ratio: float = 1.05) -> float:
        """Computes total restaked security power in ETH units."""
        return self.native_eth + (self.st_eth * st_eth_ratio) + (self.r_eth * r_eth_ratio)

    def apply_slashing(self, slash_fraction: float, avs_name: str):
        """Reduces underlying restaked balances proportionally."""
        slashed_val = self.total_weight_eth() * slash_fraction
        self.native_eth *= (1.0 - slash_fraction)
        self.st_eth *= (1.0 - slash_fraction)
        self.r_eth *= (1.0 - slash_fraction)
        self.slashed_history.append((avs_name, slashed_val))
        self.is_frozen = True


class RestakingEcosystem:
    def __init__(self):
        self.operators: Dict[str, Operator] = {}
        self.services: Dict[str, AVS] = {}

    def add_operator(self, op: Operator):
        self.operators[op.name] = op

    def add_service(self, service: AVS):
        self.services[service.name] = service

    def delegate_to_avs(self, operator_name: str, avs_name: str):
        if operator_name not in self.operators or avs_name not in self.services:
            raise ValueError("Unknown operator or AVS")
        self.services[avs_name].enroll(operator_name)

    def get_avs_total_security(self, avs_name: str) -> float:
        """Returns cumulative active (non-frozen) stake backing the AVS."""
        service = self.services[avs_name]
        total = 0.0
        for op_name in service.enrolled_operators:
            op = self.operators[op_name]
            if not op.is_frozen:
                total += op.total_weight_eth()
        return total

    def execute_avs_task(self, avs_name: str, participating_operators: List[str]) -> bool:
        """Evaluates whether participating operators satisfy 67% quorum."""
        service = self.services[avs_name]
        total_active_backing = self.get_avs_total_security(avs_name)

        if total_active_backing < service.min_security_eth:
            return False  # Under-collateralized service!

        participating_weight = 0.0
        for op_name in participating_operators:
            if op_name in service.enrolled_operators and not self.operators[op_name].is_frozen:
                participating_weight += self.operators[op_name].total_weight_eth()

        quorum_ratio = participating_weight / total_active_backing if total_active_backing > 0 else 0
        if quorum_ratio >= service.quorum_pct:
            service.completed_tasks += 1
            return True
        return False

    def slash_operator(self, operator_name: str, avs_name: str, slash_fraction: float = 0.25):
        """Slashes operator on one AVS and assesses cascading impact."""
        op = self.operators[operator_name]
        weight_before = op.total_weight_eth()
        op.apply_slashing(slash_fraction, avs_name)
        weight_after = op.total_weight_eth()
        return weight_before - weight_after


if __name__ == "__main__":
    print("=== EigenLayer Shared Security & Slashing Contagion Simulator ===")
    eco = RestakingEcosystem()

    # Create 3 major Node Operators
    op_alpha = Operator("Alpha_Node", native_eth=20_000, st_eth=10_000, r_eth=5_000)   # ~35,250 ETH
    op_beta = Operator("Beta_Staker", native_eth=15_000, st_eth=15_000, r_eth=10_000)  # ~40,500 ETH
    op_gamma = Operator("Gamma_Infra", native_eth=10_000, st_eth=5_000, r_eth=5_000)    # ~20,250 ETH

    eco.add_operator(op_alpha)
    eco.add_operator(op_beta)
    eco.add_operator(op_gamma)

    # Create 3 AVS networks
    eigen_da = AVS("EigenDA", min_security_eth=50_000, quorum_pct=0.67)
    zk_bridge = AVS("HyperBridge", min_security_eth=40_000, quorum_pct=0.67)
    oracle_net = AVS("FastOracle", min_security_eth=30_000, quorum_pct=0.67)

    eco.add_service(eigen_da)
    eco.add_service(zk_bridge)
    eco.add_service(oracle_net)

    # Restaking: Operators secure multiple services simultaneously!
    for op in ["Alpha_Node", "Beta_Staker", "Gamma_Infra"]:
        eco.delegate_to_avs(op, "EigenDA")
        eco.delegate_to_avs(op, "HyperBridge")
        eco.delegate_to_avs(op, "FastOracle")

    print(f"[+] Total System Operators Restaked: {len(eco.operators)}")
    print(f"[+] EigenDA Initial Security Pool : {eco.get_avs_total_security('EigenDA'):,.1f} ETH")
    print(f"[+] HyperBridge Initial Security  : {eco.get_avs_total_security('HyperBridge'):,.1f} ETH")

    # Step 1: Normal AVS Task Execution
    task_success = eco.execute_avs_task("EigenDA", participating_operators=["Alpha_Node", "Beta_Staker"])
    print(f"\n[+] EigenDA Task Execution with Alpha + Beta: {task_success} (Quorum reached)")
    assert task_success, "Task should achieve quorum"

    # Step 2: Slashing Incident on HyperBridge (Operator Alpha double-signs)
    print("\n[!] Malicious double-signing detected on HyperBridge by 'Alpha_Node'!")
    slashed_amount = eco.slash_operator("Alpha_Node", "HyperBridge", slash_fraction=0.30)
    print(f"[!] Slashed 30% of Alpha_Node's stake: -{slashed_amount:,.1f} ETH burned.")
    print(f"[!] Alpha_Node has been FROZEN.")

    # Step 3: Cascading Security Contagion Assessment
    print("\n[+] Assessing Cascading Contagion across other AVS protocols:")
    for avs_name, srv in eco.services.items():
        active_sec = eco.get_avs_total_security(avs_name)
        health = "HEALTHY" if active_sec >= srv.min_security_eth else "CRITICAL DEFICIT"
        print(f"    - {avs_name:12s} Active Security: {active_sec:,.1f} ETH (Min: {srv.min_security_eth:,.1f}) -> Status: {health}")

    # Now attempt task on EigenDA without Alpha (Beta + Gamma only)
    task_after = eco.execute_avs_task("EigenDA", participating_operators=["Beta_Staker", "Gamma_Infra"])
    print(f"\n[+] EigenDA Task Execution with Beta + Gamma: {task_after} (100% of remaining active stake)")
    assert task_after, "Remaining active operators should successfully continue service"

    print("[SUCCESS] EigenLayer restaking, quorum verification, and cascading slashing model verified.")
