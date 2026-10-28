#!/usr/bin/env python3
"""
Interactive Fraud Proof Bisection Game Simulator (Arbitrum Nitro / OP Cannon Style)
Demonstrates:
1. Two parties: Honest Asserter vs Dishonest Challenger (or vice-versa)
2. State trace of N VM instructions: S_0, S_1, ..., S_N
3. Multi-round binary search (bisection) reducing N steps to 1 disputed transition
4. One-step on-chain evaluation resolving the dispute and slashing the fraudster
"""

import math
from typing import List, Tuple


class VMState:
    def __init__(self, step: int, register_val: int):
        self.step = step
        self.register_val = register_val

    def __repr__(self):
        return f"State(step={self.step}, val={self.register_val})"


def execute_instruction(prev_state: VMState) -> VMState:
    """Deterministic CPU transition: S_{t+1} = (S_t * 3 + 7) % 1000003"""
    next_val = (prev_state.register_val * 3 + 7) % 1000003
    return VMState(step=prev_state.step + 1, register_val=next_val)


def generate_trace(start_val: int, num_steps: int) -> List[VMState]:
    trace = [VMState(0, start_val)]
    for _ in range(num_steps):
        trace.append(execute_instruction(trace[-1]))
    return trace


def run_bisection_game(
    honest_trace: List[VMState],
    malicious_trace: List[VMState]
) -> Tuple[int, VMState, VMState, str]:
    """
    Executes interactive bisection between two parties having conflicting final states.
    Returns: (disputed_step, honest_prev_state, contested_malicious_next_state, winner)
    """
    assert len(honest_trace) == len(malicious_trace)
    assert honest_trace[0].register_val == malicious_trace[0].register_val, "Initial state must agree"
    assert honest_trace[-1].register_val != malicious_trace[-1].register_val, "Final state must conflict"

    low = 0
    high = len(honest_trace) - 1
    round_counter = 0

    print(f"[+] Starting Bisection Game with {len(honest_trace) - 1} steps (Range: [{low}, {high}])...")

    while high - low > 1:
        round_counter += 1
        mid = (low + high) // 2

        honest_mid = honest_trace[mid]
        malicious_mid = malicious_trace[mid]

        print(f"    Round {round_counter}: Midpoint Step #{mid}")
        print(f"      - Honest State    : {honest_mid}")
        print(f"      - Contested State : {malicious_mid}")

        if honest_mid.register_val == malicious_mid.register_val:
            # Divergence happened in the second half
            print(f"      -> Midpoint agrees. Divergence lies in right half [{mid}, {high}].")
            low = mid
        else:
            # Divergence happened in the first half
            print(f"      -> Midpoint disagrees! Divergence lies in left half [{low}, {mid}].")
            high = mid

    # Now high - low == 1. Step 'low' is agreed, step 'high' is disputed!
    disputed_step = low
    print(f"\n[+] Bisection finished in {round_counter} rounds! Disputed single transition: Step {disputed_step} -> {disputed_step + 1}")

    # L1 One-Step Prover executes instruction on agreed step 'low'
    agreed_prev = honest_trace[disputed_step]
    expected_next = execute_instruction(agreed_prev)
    claimed_next = malicious_trace[disputed_step + 1]

    print(f"[+] L1 One-Step Prover Execution:")
    print(f"    Agreed Input State : {agreed_prev}")
    print(f"    Computed Real State: {expected_next}")
    print(f"    Malicious Claim    : {claimed_next}")

    if expected_next.register_val == claimed_next.register_val:
        winner = "Malicious"
    else:
        winner = "Honest"

    return disputed_step, agreed_prev, claimed_next, winner


if __name__ == "__main__":
    print("=== Optimistic Rollup Interactive Bisection Simulator ===")
    TOTAL_STEPS = 1024  # 1024 execution steps
    initial_val = 42

    # Honest sequence
    honest_trace = generate_trace(initial_val, TOTAL_STEPS)

    # Malicious sequencer alters step 789's state
    malicious_trace = generate_trace(initial_val, TOTAL_STEPS)
    corrupted_step = 789
    for i in range(corrupted_step, len(malicious_trace)):
        malicious_trace[i] = VMState(i, (malicious_trace[i].register_val + 9999) % 1000003)

    print(f"[+] Injected fault by malicious sequencer at Step #{corrupted_step}.")
    step, prev_state, bad_state, winner = run_bisection_game(honest_trace, malicious_trace)

    print(f"\n[+] Decision: {winner} Party Won!")
    print(f"[+] Resulting Action: Fraud confirmed! Malicious sequencer slashed and rollup state rolled back.")
    assert winner == "Honest"
    assert step + 1 == corrupted_step, f"Expected fault pinpointed at {corrupted_step}, got {step + 1}"
    print("[SUCCESS] Interactive Fraud Proof Bisection correctly identified invalid step.")
