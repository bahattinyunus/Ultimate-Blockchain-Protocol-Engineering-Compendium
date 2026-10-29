#!/usr/bin/env python3
"""
Solana Sealevel SVM Parallel Runtime Simulator
Demonstrates:
1. Account-based concurrency model (Read-Only vs Writable locks)
2. Conflict detection: Read-After-Write (RAW), Write-After-Read (WAR), Write-After-Write (WAW)
3. Dynamic greedy batch scheduler across multi-core worker pipelines
4. Benchmarking execution latency: Sequential (EVM-style) vs Parallel (SVM-style)
"""

import time
from typing import Dict, List, Set, Tuple


class Transaction:
    def __init__(
        self,
        tx_id: str,
        read_accounts: List[str],
        write_accounts: List[str],
        duration_ms: float = 5.0
    ):
        self.tx_id = tx_id
        self.read_accounts = set(read_accounts)
        self.write_accounts = set(write_accounts)
        self.duration_ms = duration_ms

    def conflicts_with(self, other: "Transaction") -> bool:
        """
        Two transactions conflict if:
        1. One writes to an account the other reads or writes (WAW, WAR, RAW).
        """
        # WAW conflict
        if self.write_accounts & other.write_accounts:
            return True
        # RAW / WAR conflict
        if self.write_accounts & other.read_accounts:
            return True
        if self.read_accounts & other.write_accounts:
            return True
        # Read-Read does NOT conflict!
        return False

    def __repr__(self):
        return f"Tx({self.tx_id}, R={list(self.read_accounts)}, W={list(self.write_accounts)})"


class SealevelScheduler:
    def __init__(self, num_cores: int = 4):
        self.num_cores = num_cores

    def schedule_batches(self, transactions: List[Transaction]) -> List[List[Transaction]]:
        """
        Partitions transactions into conflict-free batches that can be executed
        in parallel across worker cores.
        """
        remaining = list(transactions)
        batches: List[List[Transaction]] = []

        while remaining:
            current_batch: List[Transaction] = []
            next_remaining: List[Transaction] = []

            for tx in remaining:
                # Check if tx conflicts with anything already scheduled in this batch
                has_conflict = any(tx.conflicts_with(scheduled_tx) for scheduled_tx in current_batch)
                if not has_conflict:
                    current_batch.append(tx)
                else:
                    next_remaining.append(tx)

            batches.append(current_batch)
            remaining = next_remaining

        return batches


def simulate_runtime_benchmark(transactions: List[Transaction], num_cores: int = 4):
    # 1. Sequential Execution (EVM style)
    evm_time_ms = sum(tx.duration_ms for tx in transactions)

    # 2. Parallel Sealevel Execution (SVM style)
    scheduler = SealevelScheduler(num_cores=num_cores)
    batches = scheduler.schedule_batches(transactions)

    svm_time_ms = 0.0
    for batch in batches:
        # In a batch, items are split across `num_cores`
        core_loads = [0.0] * num_cores
        for i, tx in enumerate(batch):
            core_loads[i % num_cores] += tx.duration_ms
        svm_time_ms += max(core_loads)

    speedup = evm_time_ms / svm_time_ms if svm_time_ms > 0 else 1.0
    return evm_time_ms, svm_time_ms, len(batches), speedup


if __name__ == "__main__":
    print("=== Solana Sealevel SVM Parallel Runtime Simulator ===")
    # 8 realistic transactions:
    # Notice: Alice and Bob transfers don't conflict with Charlie and Dave DEX swaps!
    txs = [
        Transaction("tx1_transfer_alice_bob", read_accounts=["SystemProgram"], write_accounts=["Alice", "Bob"]),
        Transaction("tx2_transfer_charlie_dave", read_accounts=["SystemProgram"], write_accounts=["Charlie", "Dave"]),
        Transaction("tx3_dex_swap_pool_a", read_accounts=["Oracle_SOL_USD"], write_accounts=["Pool_A", "User_E"]),
        Transaction("tx4_dex_swap_pool_b", read_accounts=["Oracle_BTC_USD"], write_accounts=["Pool_B", "User_F"]),
        Transaction("tx5_transfer_eve_frank", read_accounts=["SystemProgram"], write_accounts=["Eve", "Frank"]),
        Transaction("tx6_transfer_alice_carol", read_accounts=["SystemProgram"], write_accounts=["Alice", "Carol"]), # Conflicts with tx1 on Alice!
        Transaction("tx7_dex_swap_pool_a_user_g", read_accounts=["Oracle_SOL_USD"], write_accounts=["Pool_A", "User_G"]), # Conflicts with tx3 on Pool_A!
        Transaction("tx8_nft_mint", read_accounts=["MetadataProgram"], write_accounts=["NftCollection", "User_H"]),
    ]

    print(f"[+] Loaded {len(txs)} transactions into mempool block.")

    scheduler = SealevelScheduler(num_cores=4)
    batches = scheduler.schedule_batches(txs)

    print(f"\n[+] Sealevel Conflict Resolution & Parallel Scheduling ({len(batches)} Batches):")
    for b_idx, batch in enumerate(batches):
        print(f"    Batch #{b_idx + 1} ({len(batch)} parallel txs):")
        for tx in batch:
            print(f"      - {tx.tx_id}")

    evm_time, svm_time, num_batches, speedup = simulate_runtime_benchmark(txs, num_cores=4)

    print(f"\n[+] Execution Benchmark (4 Hardware Worker Cores):")
    print(f"    - EVM Sequential Execution Time : {evm_time:.1f} ms")
    print(f"    - SVM Sealevel Parallel Time    : {svm_time:.1f} ms ({num_batches} conflict-free rounds)")
    print(f"    - Parallel Speedup Factor       : {speedup:.2f}x THROUGHPUT MULTIPLIER!")

    assert speedup > 1.5, "Parallel scheduling should significantly outperform sequential execution"
    print("[SUCCESS] Solana Sealevel concurrent execution validated.")
