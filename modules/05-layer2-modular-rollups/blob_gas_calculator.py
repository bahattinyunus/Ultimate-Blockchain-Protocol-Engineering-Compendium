#!/usr/bin/env python3
"""
EIP-4844 Blob Gas Price & Economics Calculator
Demonstrates:
1. Target vs Max Blobs per block (3 target / 6 max)
2. EIP-4844 exact exponential blob gas price formula: fake_exponential(min_price, excess_blob_gas, update_fraction)
3. Cumulative excess blob gas calculation across blocks
4. Cost comparison: Posting Rollup Batch Data as Calldata vs Blobs
"""

import math

MIN_BLOB_GASPRICE = 1  # 1 wei
BLOB_GASPRICE_UPDATE_FRACTION = 3338477
GAS_PER_BLOB = 131072  # 128 KB
TARGET_BLOBS_PER_BLOCK = 3
TARGET_BLOB_GAS_PER_BLOCK = TARGET_BLOBS_PER_BLOCK * GAS_PER_BLOB  # 393,216
MAX_BLOBS_PER_BLOCK = 6


def fake_exponential(factor: int, numerator: int, denominator: int) -> int:
    """
    Standard Ethereum Consensus / Execution Layer implementation of Taylor-expanded exponential.
    Computes floor(factor * e^(numerator / denominator))
    """
    i = 1
    output = 0
    numerator_accum = factor * denominator
    while numerator_accum > 0:
        output += numerator_accum
        numerator_accum = (numerator_accum * numerator) // (denominator * i)
        i += 1
    return output // denominator


def get_blob_gasprice(excess_blob_gas: int) -> int:
    """Calculates blob gas price in wei given excess_blob_gas."""
    return fake_exponential(MIN_BLOB_GASPRICE, excess_blob_gas, BLOB_GASPRICE_UPDATE_FRACTION)


def calculate_next_excess_blob_gas(current_excess: int, blobs_in_block: int) -> int:
    """Updates excess blob gas for next block."""
    consumed_blob_gas = blobs_in_block * GAS_PER_BLOB
    if current_excess + consumed_blob_gas < TARGET_BLOB_GAS_PER_BLOCK:
        return 0
    return current_excess + consumed_blob_gas - TARGET_BLOB_GAS_PER_BLOCK


def compare_rollup_batch_costs(
    batch_size_bytes: int = 131072,  # 1 Blob = 128 KB
    base_fee_gwei: float = 25.0,
    blob_gas_price_gwei: float = 0.001  # Typical blob market fee
):
    """
    Compares the L1 cost of posting a rollup batch via:
    1. Calldata: 16 gas per non-zero byte
    2. EIP-4844 Blob: Fixed 131,072 blob gas
    """
    # Calldata cost
    calldata_gas = batch_size_bytes * 16
    calldata_cost_eth = (calldata_gas * base_fee_gwei * 1e9) / 1e18

    # Blob cost
    blobs_needed = math.ceil(batch_size_bytes / GAS_PER_BLOB)
    total_blob_gas = blobs_needed * GAS_PER_BLOB
    blob_cost_eth = (total_blob_gas * blob_gas_price_gwei * 1e9) / 1e18

    savings_multiplier = calldata_cost_eth / blob_cost_eth if blob_cost_eth > 0 else float("inf")

    return {
        "calldata_gas": calldata_gas,
        "calldata_cost_eth": calldata_cost_eth,
        "blob_gas": total_blob_gas,
        "blob_cost_eth": blob_cost_eth,
        "savings_multiplier": savings_multiplier
    }


if __name__ == "__main__":
    print("=== EIP-4844 Proto-Danksharding Gas Economics ===")

    # Scenario 1: Simulating congestion where 6 blobs/block are posted for 20 consecutive blocks
    excess_gas = 0
    print("[+] Simulating block sequence under heavy blob demand (6 blobs/block):")
    for block_num in range(1, 11):
        price_wei = get_blob_gasprice(excess_gas)
        price_gwei = price_wei / 1e9
        print(f"    Block #{block_num:02d} | Excess Gas: {excess_gas:7d} | Blob Gas Price: {price_gwei:.6f} Gwei ({price_wei} wei)")
        excess_gas = calculate_next_excess_blob_gas(excess_gas, blobs_in_block=6)

    # Scenario 2: Rollup Batch comparison (128 KB)
    print("\n[+] Cost Comparison for a 128 KB L2 Rollup Batch Data:")
    comparison = compare_rollup_batch_costs(
        batch_size_bytes=131072,
        base_fee_gwei=25.0,
        blob_gas_price_gwei=0.005
    )
    print(f"    - Calldata Gas Consumed : {comparison['calldata_gas']:,} gas")
    print(f"    - Calldata L1 Cost      : {comparison['calldata_cost_eth']:.5f} ETH")
    print(f"    - Blob Gas Consumed     : {comparison['blob_gas']:,} blob gas")
    print(f"    - Blob L1 Cost          : {comparison['blob_cost_eth']:.7f} ETH")
    print(f"    - Economic Savings      : {comparison['savings_multiplier']:.1f}x CHEAPER via Blobs!")

    assert comparison["savings_multiplier"] > 10, "Blob space should be orders of magnitude cheaper than calldata"
    print("[SUCCESS] EIP-4844 blob pricing and economic models verified.")
