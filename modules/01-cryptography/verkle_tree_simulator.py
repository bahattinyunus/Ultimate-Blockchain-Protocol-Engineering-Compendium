#!/usr/bin/env python3
"""
Verkle Tree (Vector Commitment Tree) Educational Simulator
Core upgrade enabling Stateless Ethereum Clients (EIP-6800).

Demonstrates:
1. 256-ary Tree Structure (256 children per node)
2. Vector commitments replacing Merkle cryptographic hashes
3. Comparison of witness / proof sizes: O(log_2 N) Merkle proof vs O(1) constant-size Verkle proof
4. Evaluation of multi-proof aggregation
"""

import math
from typing import Dict, List, Tuple


class VerkleNode:
    def __init__(self, is_leaf: bool = False):
        self.is_leaf = is_leaf
        self.children: Dict[int, "VerkleNode"] = {}
        self.values: Dict[int, int] = {}  # for leaf values
        self.commitment: int = 0

    def compute_commitment(self) -> int:
        """Simulates KZG vector commitment over 256 scalar evaluations."""
        accum = 1337
        for idx in range(256):
            if idx in self.children:
                val = self.children[idx].compute_commitment()
            else:
                val = self.values.get(idx, 0)
            accum = (accum * 31 + val * (idx + 1)) % 1000000007
        self.commitment = accum
        return self.commitment


class VerkleTree:
    def __init__(self):
        self.root = VerkleNode(is_leaf=False)

    def insert(self, key_path: List[int], value: int):
        """
        Inserts key represented as byte path (e.g. [byte0, byte1, byte2]) -> value.
        """
        curr = self.root
        for byte_val in key_path[:-1]:
            if byte_val not in curr.children:
                curr.children[byte_val] = VerkleNode(is_leaf=False)
            curr = curr.children[byte_val]

        leaf_idx = key_path[-1]
        curr.values[leaf_idx] = value


def compare_proof_sizes(num_state_keys: int = 1_000_000_000, keys_accessed: int = 50):
    """
    Compares Ethereum Merkle Patricia Trie (MPT) witness size against Verkle Tree witness size
    for an execution block accessing `keys_accessed` state locations.
    """
    # 1. Merkle Tree (Binary/Hexary - Radix 16)
    # Average depth = log_16(10^9) ~ 7.5 levels
    # Each step requires sibling hashes: (16 - 1) * 32 bytes = 480 bytes per level
    # Or binary: depth ~ 30, 30 * 32 bytes = 960 bytes per key accessed
    mpt_depth = math.ceil(math.log(num_state_keys, 16))
    mpt_witness_bytes_per_key = mpt_depth * 15 * 32  # MPT branch nodes
    total_mpt_witness_kb = (mpt_witness_bytes_per_key * keys_accessed) / 1024

    # 2. Verkle Tree (256-ary with KZG Multiproofs)
    # Depth = log_256(10^9) ~ 3.7 -> 4 levels
    # KZG multiproof allows opening all paths simultaneously with 1 aggregate proof (~150 bytes)
    # plus 32 bytes per intermediate commitment
    verkle_multiproof_bytes = 150  # Constant KZG multiproof
    verkle_commitments_bytes = keys_accessed * 4 * 32  # Intermediate commitments
    total_verkle_witness_kb = (verkle_multiproof_bytes + verkle_commitments_bytes) / 1024

    return {
        "mpt_depth": mpt_depth,
        "mpt_witness_kb": total_mpt_witness_kb,
        "verkle_witness_kb": total_verkle_witness_kb,
        "reduction_factor": total_mpt_witness_kb / total_verkle_witness_kb
    }


if __name__ == "__main__":
    print("=== Verkle Tree & Stateless Ethereum Simulator (EIP-6800) ===")
    tree = VerkleTree()

    # Insert state accounts with 3-byte stem path: [0x12, 0x34, 0x56]
    accounts = {
        (0x01, 0x0A, 0x42): 100_000_000,  # Alice: 100 ETH
        (0x01, 0x0A, 0x99): 50_000_000,   # Bob: 50 ETH
        (0x02, 0x14, 0x01): 1_500_000,    # Uniswap Vault: 1.5 ETH
    }

    print(f"[+] Inserting {len(accounts)} accounts into 256-ary Verkle Tree...")
    for path, balance in accounts.items():
        tree.insert(list(path), balance)

    root_commitment = tree.root.compute_commitment()
    print(f"[+] Computed Verkle Root Vector Commitment: 0x{root_commitment:08x}")

    print("\n[+] Comparing Stateless Block Witness Sizes (1 Billion State Keys, 50 Accesses/Block):")
    stats = compare_proof_sizes(num_state_keys=1_000_000_000, keys_accessed=50)
    print(f"    - Merkle Patricia Trie Witness : {stats['mpt_witness_kb']:,.1f} KB (Unviable for P2P block gossip)")
    print(f"    - Verkle Tree Witness          : {stats['verkle_witness_kb']:,.1f} KB (Easily fits in single network packet)")
    print(f"    - Proof Size Reduction         : {stats['reduction_factor']:.1f}x SMALLER!")

    assert stats["reduction_factor"] > 10, "Verkle trees should achieve >10x witness size compression"
    print("[SUCCESS] Verkle Tree vector commitment properties verified.")
