#!/usr/bin/env python3
"""
R1CS (Rank-1 Constraint Systems) Arithmetization & Witness Engine
Core mathematical reduction at the heart of zk-SNARKs (Groth16 / Pinocchio).

Demonstrates:
1. Program Flattening: Decomposing y = x^3 + x + 5 into primitive quadratic gates:
   - v1 = x * x
   - v2 = v1 * x
   - out = v2 + x + 5  =>  (v2 + x + 5) * 1 = out
2. Construction of R1CS matrices A, B, C over variable vector:
   s = [1, out, x, v1, v2]
3. Witness computation and exact Hadamard check: (A . s) * (B . s) == (C . s)
4. Fraudulent witness detection and invalid constraint isolation
"""

from typing import List, Tuple


class R1CSEngine:
    def __init__(self):
        # Variable mapping: index 0: '1', 1: 'out', 2: 'x', 3: 'v1', 4: 'v2'
        self.var_names = ["1", "out", "x", "v1", "v2"]
        self.num_vars = len(self.var_names)

        # Gate 1: x * x = v1
        # Gate 2: v1 * x = v2
        # Gate 3: (v2 + x + 5) * 1 = out
        # Matrix A: Left terms, B: Right terms, C: Output terms
        self.A: List[List[int]] = [
            [0, 0, 1, 0, 0],  # x
            [0, 0, 0, 1, 0],  # v1
            [5, 0, 1, 0, 1],  # 5*1 + 1*x + 1*v2
        ]
        self.B: List[List[int]] = [
            [0, 0, 1, 0, 0],  # x
            [0, 0, 1, 0, 0],  # x
            [1, 0, 0, 0, 0],  # 1
        ]
        self.C: List[List[int]] = [
            [0, 0, 0, 1, 0],  # v1
            [0, 0, 0, 0, 1],  # v2
            [0, 1, 0, 0, 0],  # out
        ]

    def compute_witness(self, x: int) -> List[int]:
        """Synthesizes the witness vector s = [1, out, x, v1, v2] from input x."""
        v1 = x * x
        v2 = v1 * x
        out = v2 + x + 5
        return [1, out, x, v1, v2]

    def dot_product(self, row: List[int], vec: List[int]) -> int:
        return sum(a * b for a, b in zip(row, vec))

    def verify_witness(self, witness: List[int]) -> Tuple[bool, List[int]]:
        """
        Checks whether (A . s) * (B . s) == (C . s) holds for every gate.
        Returns (is_valid, violated_gate_indices).
        """
        violated_gates = []
        for i in range(len(self.A)):
            left = self.dot_product(self.A[i], witness)
            right = self.dot_product(self.B[i], witness)
            out = self.dot_product(self.C[i], witness)
            if left * right != out:
                violated_gates.append(i)

        return len(violated_gates) == 0, violated_gates


if __name__ == "__main__":
    print("=== R1CS (Rank-1 Constraint Systems) Arithmetization Engine ===")
    engine = R1CSEngine()

    print("[+] Program: y = x^3 + x + 5")
    print(f"[+] Variable Vector Layout s: {engine.var_names}")
    print(f"[+] R1CS Constraints (Gates): {len(engine.A)} Rank-1 Equations")

    # Honest execution: x = 3 -> y = 3^3 + 3 + 5 = 27 + 3 + 5 = 35
    input_x = 3
    witness = engine.compute_witness(input_x)
    print(f"\n[+] Prover generating witness for secret input x = {input_x}:")
    for name, val in zip(engine.var_names, witness):
        print(f"    - {name:3s} = {val}")

    is_valid, violations = engine.verify_witness(witness)
    print(f"\n[+] Verifying Honest Witness satisfaction (A.s * B.s == C.s): {is_valid}")
    assert is_valid, "Valid witness failed R1CS verification!"

    # Malicious prover attempts to forge output: claim y = 99 for x = 3
    fraudulent_witness = list(witness)
    fraudulent_witness[1] = 99  # Tamper 'out'
    print(f"\n[+] Testing Fraudulent Witness (x = 3, claimed out = 99):")
    is_fraud_valid, fraud_violations = engine.verify_witness(fraudulent_witness)
    print(f"    - Verification Result  : {is_fraud_valid}")
    print(f"    - Violated Gate Index  : Gate #{fraud_violations[0]} (Gate 3: out computation)")
    assert not is_fraud_valid, "Fraudulent witness passed R1CS verification!"

    print("[SUCCESS] R1CS arithmetization and constraint satisfaction verified.")
