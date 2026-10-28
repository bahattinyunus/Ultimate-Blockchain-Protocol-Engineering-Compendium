#!/usr/bin/env python3
"""
KZG (Kate-Zaverucha-Goldberg) Polynomial Commitment Educational Simulator
Demonstrates:
1. Trusted Setup (SRS - Structured Reference String / Powers of Tau)
2. Polynomial Commitment generation C = P(s)
3. Polynomial synthetic division to calculate quotient polynomial Q(x) = (P(x) - y) / (x - z)
4. Opening proof generation pi = Q(s)
5. Homomorphic algebraic verification check: C - y == pi * (s - z)
"""

from typing import List, Tuple

# Prime modulus for educational field
MODULUS = 21888242871839275222246405745257275088548364400416034343698204186575808495617  # BN254 scalar field prime


def mod_inv(a: int, m: int = MODULUS) -> int:
    return pow(a, -1, m)


class Polynomial:
    """Represents a polynomial with coefficients in F_p: c0 + c1*x + c2*x^2 + ..."""

    def __init__(self, coeffs: List[int]):
        # Trim high-degree zero coefficients
        self.coeffs = [c % MODULUS for c in coeffs]
        while len(self.coeffs) > 1 and self.coeffs[-1] == 0:
            self.coeffs.pop()

    @property
    def degree(self) -> int:
        return len(self.coeffs) - 1

    def evaluate(self, x: int) -> int:
        """Horner's rule evaluation in F_p."""
        res = 0
        for coeff in reversed(self.coeffs):
            res = (res * x + coeff) % MODULUS
        return res

    def divide_by_linear(self, z: int) -> Tuple["Polynomial", int]:
        """
        Computes Q(x) and remainder r such that P(x) = Q(x)*(x - z) + r
        via synthetic division (Ruffini's rule).
        """
        r = 0
        q_coeffs = [0] * len(self.coeffs)
        for i in reversed(range(len(self.coeffs))):
            val = (self.coeffs[i] + r * z) % MODULUS
            if i > 0:
                q_coeffs[i - 1] = val
            r = val
        if len(q_coeffs) > 1:
            q_coeffs = q_coeffs[:-1]
        else:
            q_coeffs = [0]
        return Polynomial(q_coeffs), r


class KZGScheme:
    """Educational KZG Simulator."""

    def __init__(self, secret_tau: int, max_degree: int = 16):
        self.secret_tau = secret_tau
        # SRS: [tau^0, tau^1, tau^2, ..., tau^max_degree]
        self.srs: List[int] = [pow(secret_tau, i, MODULUS) for i in range(max_degree + 1)]

    def commit(self, poly: Polynomial) -> int:
        """Computes commitment C = sum(c_i * srs[i]) = P(tau)"""
        if poly.degree >= len(self.srs):
            raise ValueError("Polynomial degree exceeds SRS capacity")
        commitment = 0
        for i, c in enumerate(poly.coeffs):
            commitment = (commitment + c * self.srs[i]) % MODULUS
        return commitment

    def create_witness(self, poly: Polynomial, z: int) -> Tuple[int, int]:
        """
        Produces evaluation y = P(z) and evaluation proof pi = Q(tau)
        where Q(x) = (P(x) - y) / (x - z)
        """
        y = poly.evaluate(z)
        poly_shifted = Polynomial([(c - y) % MODULUS if i == 0 else c for i, c in enumerate(poly.coeffs)])
        quotient, rem = poly_shifted.divide_by_linear(z)
        assert rem == 0, "Remainder must be zero after subtracting evaluation"
        proof_pi = self.commit(quotient)
        return y, proof_pi

    def verify(self, commitment: int, z: int, y: int, proof_pi: int) -> bool:
        """
        Simulates pairing check e(pi, tau - z) == e(C - y, 1) in field arithmetic:
        pi * (tau - z) == C - y (mod p)
        """
        lhs = (proof_pi * (self.secret_tau - z)) % MODULUS
        rhs = (commitment - y) % MODULUS
        return lhs == rhs


if __name__ == "__main__":
    print("=== KZG Polynomial Commitment Scheme (EIP-4844 / Verkle Foundation) ===")
    tau_secret = 428751932759  # Ephemeral secret discarded after ceremony
    kzg = KZGScheme(secret_tau=tau_secret, max_degree=8)

    # Polynomial: P(x) = 5 + 3x + 2x^2 + 7x^3
    p = Polynomial([5, 3, 2, 7])
    print(f"[+] Polynomial: 5 + 3x + 2x^2 + 7x^3 (degree: {p.degree})")

    # Step 1: Commit to polynomial
    commitment = kzg.commit(p)
    print(f"[+] KZG Commitment C: 0x{commitment:064x}")

    # Step 2: Open at evaluation point z = 4
    eval_point_z = 4
    y_eval, proof = kzg.create_witness(p, eval_point_z)
    print(f"[+] Evaluation P({eval_point_z}) = {y_eval}")
    print(f"[+] Opening Proof pi: 0x{proof:064x}")

    # Step 3: Verifier checks opening proof
    is_valid = kzg.verify(commitment, eval_point_z, y_eval, proof)
    print(f"[+] Verification with valid claim: {is_valid}")
    assert is_valid, "Valid KZG proof failed verification!"

    # Step 4: Tampered evaluation test
    fraudulent_y = (y_eval + 1) % MODULUS
    is_tampered_valid = kzg.verify(commitment, eval_point_z, fraudulent_y, proof)
    print(f"[+] Verification with fake claim (y + 1): {is_tampered_valid}")
    assert not is_tampered_valid, "Tampered evaluation passed verification!"

    print("[SUCCESS] KZG polynomial commitment engine successfully verified.")
