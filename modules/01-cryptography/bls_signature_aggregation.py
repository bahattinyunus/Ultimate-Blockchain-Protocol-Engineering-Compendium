#!/usr/bin/env python3
"""
BLS (Boneh-Lynn-Shacham) Signature Aggregation Protocol Simulator
Fundamental cryptographic primitive powering Ethereum Consensus (Beacon Chain).

Demonstrates:
1. Elliptic curve pairing-friendly mapping simulation e: G1 x G2 -> GT
2. Key generation: sk in F_q, PK = sk * G2
3. Signing: sigma = sk * H(m) in G1
4. Aggregation: sigma_agg = sum(sigma_i) [G1], PK_agg = sum(PK_i) [G2]
5. Single-pairing batch verification: e(sigma_agg, G2) == e(H(m), PK_agg)
"""

import hashlib
import secrets
from typing import List, Tuple

# Large prime field for educational demonstration
FIELD_MODULUS = 0x1A0111EA397FE69A4B1BA7B6434BACD764774B84F38512BF6730D2A0F6B0F6241EABFFFEB153FFFFB9FEFFFFFFFFAAAB
SUBGROUP_ORDER = 0x73EDA753299D7D483339D80809A1D80553BDA402FFFE5BFEFFFFFFFF00000001

# Generator placeholders in G1 and G2
G1_GEN = 7
G2_GEN = 11


def hash_to_curve(message: bytes) -> int:
    """Deterministic hash of arbitrary message into G1 subgroup."""
    digest = hashlib.sha256(b"BLS_SIG_ETH2_CURVE_HASH:" + message).digest()
    scalar = int.from_bytes(digest, "big") % SUBGROUP_ORDER
    # Map to group point
    return (scalar * G1_GEN) % SUBGROUP_ORDER


def generate_bls_keypair() -> Tuple[int, int]:
    """Generates private key in [1..r-1] and public key in G2."""
    sk = secrets.randbelow(SUBGROUP_ORDER - 1) + 1
    pk = (sk * G2_GEN) % SUBGROUP_ORDER
    return sk, pk


def bls_sign(sk: int, message: bytes) -> int:
    """Computes BLS signature in G1: sigma = sk * H(m)"""
    hm = hash_to_curve(message)
    return (sk * hm) % SUBGROUP_ORDER


def aggregate_signatures(signatures: List[int]) -> int:
    """Combines N signatures into 1 aggregated signature via point addition: sigma_agg = sum(sigma_i)"""
    agg = 0
    for sig in signatures:
        agg = (agg + sig) % SUBGROUP_ORDER
    return agg


def aggregate_public_keys(public_keys: List[int]) -> int:
    """Combines N public keys into 1 aggregated public key: PK_agg = sum(PK_i)"""
    agg = 0
    for pk in public_keys:
        agg = (agg + pk) % SUBGROUP_ORDER
    return agg


def simulated_pairing(p_g1: int, q_g2: int) -> int:
    """
    Simulates bilinear pairing property e(a*P, b*Q) = e(P, Q)^(a*b).
    In prime scalar ring: (p_g1 * q_g2) mod r
    """
    return (p_g1 * q_g2) % SUBGROUP_ORDER


def verify_aggregate_signature(
    message: bytes,
    agg_signature: int,
    agg_public_key: int
) -> bool:
    """
    Verifies aggregate signature with a single pairing check:
    e(sigma_agg, G2) == e(H(m), PK_agg)
    """
    hm = hash_to_curve(message)
    lhs = simulated_pairing(agg_signature, G2_GEN)
    rhs = simulated_pairing(hm, agg_public_key)
    return lhs == rhs


if __name__ == "__main__":
    print("=== Ethereum Beacon Chain BLS Signature Aggregation Protocol ===")
    NUM_VALIDATORS = 128
    print(f"[+] Simulating consensus committee with {NUM_VALIDATORS} active validators...")

    validators = [generate_bls_keypair() for _ in range(NUM_VALIDATORS)]
    private_keys = [v[0] for v in validators]
    public_keys = [v[1] for v in validators]

    beacon_block_attestation = b"BeaconBlockHeader: Slot=8492021 Epoch=265375 Root=0x4a9b...7f"
    print(f"[+] Committee attesting to payload: '{beacon_block_attestation.decode()[:40]}...'")

    # Step 1: Each validator signs independently
    individual_sigs = [bls_sign(sk, beacon_block_attestation) for sk in private_keys]

    # Step 2: Aggregator combines all signatures into 1 single aggregate signature
    agg_sig = aggregate_signatures(individual_sigs)
    agg_pk = aggregate_public_keys(public_keys)

    print(f"[+] Aggregation completed:")
    print(f"    - Original signatures payload : {NUM_VALIDATORS * 96} bytes uncompressed")
    print(f"    - Aggregated signature size  : 96 bytes (Consensus compression: {NUM_VALIDATORS}x)")
    print(f"    - Aggregated Signature (hex) : 0x{agg_sig:064x}")
    print(f"    - Aggregated Public Key (hex): 0x{agg_pk:064x}")

    # Step 3: Verifier checks entire committee with ONE single pairing check!
    is_valid = verify_aggregate_signature(beacon_block_attestation, agg_sig, agg_pk)
    print(f"\n[+] Single Pairing Verification Result: {is_valid}")
    assert is_valid, "Valid aggregate signature failed verification!"

    # Step 4: Test tampering defense
    tampered_msg = b"CorruptedAttestationSlot=999999"
    assert not verify_aggregate_signature(tampered_msg, agg_sig, agg_pk), "Tampered payload passed verification!"
    print("[SUCCESS] BLS signature aggregation and consensus verification verified.")
