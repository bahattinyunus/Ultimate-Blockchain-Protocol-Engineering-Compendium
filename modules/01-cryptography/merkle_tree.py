#!/usr/bin/env python3
"""
Cryptographic Merkle Tree Implementation
Features:
1. Deterministic leaf hashing with domain separation (0x00 for leaf, 0x01 for branch)
2. OpenZeppelin compatible sorted pair hashing to prevent second preimage attacks
3. O(log N) Merkle Proof generation and verification
4. Interactive verification test suite
"""

import hashlib
from typing import List, Tuple, Optional


def hash_leaf(data: bytes) -> bytes:
    """Computes leaf hash with domain separation prefix 0x00."""
    return hashlib.sha256(b"\x00" + data).digest()


def hash_internal_pair(left: bytes, right: bytes, sorted_pairs: bool = True) -> bytes:
    """
    Computes parent hash with domain separation prefix 0x01.
    If sorted_pairs is True (OpenZeppelin style), guarantees hash(a, b) == hash(b, a).
    """
    if sorted_pairs and left > right:
        left, right = right, left
    return hashlib.sha256(b"\x01" + left + right).digest()


class MerkleTree:
    def __init__(self, raw_leaves: List[bytes], sorted_pairs: bool = True):
        if not raw_leaves:
            raise ValueError("Merkle tree cannot be empty")
        self.sorted_pairs = sorted_pairs
        self.leaves = [hash_leaf(leaf) for leaf in raw_leaves]
        self.layers: List[List[bytes]] = [self.leaves]
        self._build_tree()

    def _build_tree(self):
        current_layer = self.leaves
        while len(current_layer) > 1:
            next_layer: List[bytes] = []
            for i in range(0, len(current_layer), 2):
                left = current_layer[i]
                if i + 1 < len(current_layer):
                    right = current_layer[i + 1]
                else:
                    # Duplicate last node if odd number of elements
                    right = current_layer[i]
                parent = hash_internal_pair(left, right, self.sorted_pairs)
                next_layer.append(parent)
            self.layers.append(next_layer)
            current_layer = next_layer

    @property
    def root(self) -> bytes:
        return self.layers[-1][0]

    def get_proof(self, index: int) -> List[Tuple[bytes, str]]:
        """
        Generates Merkle audit proof for leaf at `index`.
        Returns a list of (sibling_hash, direction) tuples.
        """
        if index < 0 or index >= len(self.leaves):
            raise IndexError("Leaf index out of bounds")

        proof: List[Tuple[bytes, str]] = []
        curr_idx = index

        for layer in self.layers[:-1]:
            is_right_child = (curr_idx % 2 == 1)
            sibling_idx = curr_idx - 1 if is_right_child else curr_idx + 1

            if sibling_idx < len(layer):
                sibling = layer[sibling_idx]
            else:
                sibling = layer[curr_idx]  # Duplicated node

            direction = "left" if is_right_child else "right"
            proof.append((sibling, direction))
            curr_idx //= 2

        return proof


def verify_proof(
    leaf_data: bytes,
    proof: List[Tuple[bytes, str]],
    root: bytes,
    sorted_pairs: bool = True
) -> bool:
    """Verifies a Merkle proof against the known root."""
    current = hash_leaf(leaf_data)

    for sibling, direction in proof:
        if sorted_pairs:
            current = hash_internal_pair(current, sibling, sorted_pairs=True)
        else:
            if direction == "left":
                current = hash_internal_pair(sibling, current, sorted_pairs=False)
            else:
                current = hash_internal_pair(current, sibling, sorted_pairs=False)

    return current == root


if __name__ == "__main__":
    print("=== Cryptographic Merkle Tree Engine ===")
    transactions = [
        b"tx1: Alice -> Bob 5 ETH",
        b"tx2: Bob -> Charlie 2 ETH",
        b"tx3: Dave -> Eve 10 USDT",
        b"tx4: Eve -> Frank 1.5 DAI",
        b"tx5: Frank -> Grace 0.05 BTC",
    ]

    tree = MerkleTree(transactions, sorted_pairs=True)
    root_hex = tree.root.hex()
    print(f"[+] Computed Merkle Root ({len(transactions)} leaves): 0x{root_hex}")

    target_idx = 2
    target_tx = transactions[target_idx]
    proof = tree.get_proof(target_idx)
    print(f"[+] Audit Proof for Leaf #{target_idx} ('{target_tx.decode()}'):")
    for step, (sibling, direction) in enumerate(proof):
        print(f"    Step {step + 1}: sibling=0x{sibling.hex()[:16]}... direction={direction}")

    # Valid proof check
    is_valid = verify_proof(target_tx, proof, tree.root, sorted_pairs=True)
    print(f"[+] Proof Verification for authentic data: {is_valid}")
    assert is_valid, "Valid proof failed verification!"

    # Forged data check
    forged_tx = b"tx3: Dave -> Hacker 1,000,000 USDT"
    is_forged_valid = verify_proof(forged_tx, proof, tree.root, sorted_pairs=True)
    print(f"[+] Proof Verification for forged data   : {is_forged_valid}")
    assert not is_forged_valid, "Forged data unexpectedly passed verification!"

    print("[SUCCESS] Merkle Tree and Proof verification test passed.")
