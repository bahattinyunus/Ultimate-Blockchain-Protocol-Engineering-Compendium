#!/usr/bin/env python3
"""
secp256k1 Elliptic Curve & ECDSA Implementation from Scratch
Zero external dependencies. Demonstrates:
1. Finite field arithmetic modulo p
2. secp256k1 curve parameters (y^2 = x^3 + 7 mod p)
3. Point addition & doubling (affine coordinates)
4. Double-and-add scalar multiplication
5. ECDSA Keypair Generation, Signing (r, s), and Verification
"""

import hashlib
import hmac
import secrets
from typing import Optional, Tuple

# secp256k1 Domain Parameters
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
A = 0
B = 7
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

Point = Optional[Tuple[int, int]]
G: Point = (Gx, Gy)
INFINITY: Point = None


def inv_mod(a: int, m: int = P) -> int:
    """Computes modular inverse using Extended Euclidean Algorithm."""
    if a < 0:
        a = (a % m + m) % m
    if a == 0:
        raise ZeroDivisionError("Division by zero in finite field")
    return pow(a, -1, m)


def is_on_curve(point: Point) -> bool:
    """Verifies whether a point lies on the secp256k1 curve."""
    if point is None:
        return True
    x, y = point
    return (y * y - (x * x * x + A * x + B)) % P == 0


def point_add(p1: Point, p2: Point) -> Point:
    """Adds two points on secp256k1."""
    if p1 is None:
        return p2
    if p2 is None:
        return p1

    x1, y1 = p1
    x2, y2 = p2

    if x1 == x2 and (y1 != y2 or y1 == 0):
        return INFINITY

    if x1 == x2 and y1 == y2:
        # Point doubling
        lam = (3 * x1 * x1 + A) * inv_mod(2 * y1, P) % P
    else:
        # Point addition
        lam = (y2 - y1) * inv_mod(x2 - x1, P) % P

    x3 = (lam * lam - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return (x3, y3)


def scalar_mult(k: int, point: Point) -> Point:
    """Scalar multiplication using double-and-add algorithm."""
    if point is None or k % N == 0:
        return INFINITY

    k = k % N
    result: Point = INFINITY
    addend = point

    while k > 0:
        if k & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        k >>= 1

    return result


def generate_keypair() -> Tuple[int, Point]:
    """Generates an ECDSA private and public key pair."""
    priv_key = secrets.randbelow(N - 1) + 1
    pub_key = scalar_mult(priv_key, G)
    return priv_key, pub_key


def ecdsa_sign(message: bytes, priv_key: int) -> Tuple[int, int]:
    """
    Signs a message digest using ECDSA.
    Returns signature pair (r, s).
    Enforces low-s normalization (BIP-62 / EIP-2).
    """
    # z = int(hashlib.sha256(message).hexdigest(), 16)
    z = int.from_bytes(hashlib.sha256(message).digest(), byteorder="big")

    while True:
        # Ephemeral secret nonce k
        k = secrets.randbelow(N - 1) + 1
        r_point = scalar_mult(k, G)
        if r_point is None:
            continue
        r = r_point[0] % N
        if r == 0:
            continue

        s = (inv_mod(k, N) * (z + r * priv_key)) % N
        if s == 0:
            continue

        # Enforce canonical low-s (malleability protection)
        if s > N // 2:
            s = N - s

        return (r, s)


def ecdsa_verify(message: bytes, signature: Tuple[int, int], pub_key: Point) -> bool:
    """
    Verifies an ECDSA signature (r, s) against a public key.
    """
    r, s = signature
    if not (1 <= r < N and 1 <= s < N):
        return False
    if pub_key is None or not is_on_curve(pub_key):
        return False

    z = int.from_bytes(hashlib.sha256(message).digest(), byteorder="big")
    w = inv_mod(s, N)
    u1 = (z * w) % N
    u2 = (r * w) % N

    point = point_add(scalar_mult(u1, G), scalar_mult(u2, pub_key))
    if point is None:
        return False

    return (point[0] % N) == r


if __name__ == "__main__":
    print("=== secp256k1 & ECDSA Protocol Simulation ===")
    priv_key, pub_key = generate_keypair()
    print(f"[+] Generated Private Key: 0x{priv_key:064x}")
    print(f"[+] Generated Public Key : (0x{pub_key[0]:064x}, 0x{pub_key[1]:064x})")

    msg = b"Transactions must be cryptographically sound and deterministic."
    print(f"[+] Message to sign: '{msg.decode()}'")

    sig = ecdsa_sign(msg, priv_key)
    print(f"[+] Signature (r, s) produced:")
    print(f"    r: 0x{sig[0]:064x}")
    print(f"    s: 0x{sig[1]:064x}")

    is_valid = ecdsa_verify(msg, sig, pub_key)
    print(f"[+] Verification Result with Authentic Message: {is_valid}")
    assert is_valid, "Authentic signature verification failed!"

    # Tampered message check
    tampered_msg = b"Transactions must be maliciously altered."
    is_tampered_valid = ecdsa_verify(tampered_msg, sig, pub_key)
    print(f"[+] Verification Result with Tampered Message : {is_tampered_valid}")
    assert not is_tampered_valid, "Tampered message passed verification!"

    print("[SUCCESS] secp256k1 and ECDSA engine verified successfully.")
