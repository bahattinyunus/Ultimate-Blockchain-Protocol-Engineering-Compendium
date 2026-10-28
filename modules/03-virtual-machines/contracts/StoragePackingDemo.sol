// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title StoragePackingDemo
 * @notice Demonstrates EVM storage layout packing rules, gas consumption comparisons,
 * and assembly bitwise manipulation.
 *
 * UNPACKED VERSION (Pessimal - 3 SLOADs/SSTOREs):
 * slot 0: uint256 a (32 bytes)
 * slot 1: uint128 b (16 bytes, but isolated)
 * slot 2: uint128 c (16 bytes, but isolated)
 *
 * PACKED VERSION (Optimal - 1 SLOAD/SSTORE):
 * slot 0: [ uint128 b (16 bytes) | uint64 timestamp (8 bytes) | uint32 flags (4 bytes) | address owner (20 bytes)? NO: must fit <= 32 bytes]
 */
contract StoragePackingDemo {
    // === OPTIMIZED PACKED STRUCT (Fits exactly in 32 bytes = 1 Slot) ===
    struct PackedState {
        uint128 balance;    // 16 bytes (offset 0)
        uint64 lastUpdate;  // 8 bytes  (offset 16)
        uint32 txCount;     // 4 bytes  (offset 24)
        uint16 tier;        // 2 bytes  (offset 28)
        bool isActive;      // 1 byte   (offset 30)
        bool isVerified;    // 1 byte   (offset 31)
    }                       // Total: 32 bytes (1 Slot!)

    // Slot 0
    PackedState public state;

    // Slot 1: Bitmap for 256 boolean flags (1 gas-cheap slot replaces 256 boolean slots!)
    uint256 public flagsBitmap;

    event StateUpdated(uint128 balance, uint64 lastUpdate, uint32 txCount);

    function updateState(uint128 balance, uint16 tier) external {
        // Single SLOAD & single SSTORE updates 4 state fields simultaneously!
        state.balance = balance;
        state.lastUpdate = uint64(block.timestamp);
        state.txCount += 1;
        state.tier = tier;
        emit StateUpdated(balance, uint64(block.timestamp), state.txCount);
    }

    /// @notice Set boolean flag at index [0..255] using bitwise OR
    function setFlag(uint8 index) external {
        flagsBitmap |= (1 << index);
    }

    /// @notice Clear boolean flag at index [0..255] using bitwise AND NOT
    function clearFlag(uint8 index) external {
        flagsBitmap &= ~(1 << index);
    }

    /// @notice Read boolean flag at index [0..255] in O(1) gas
    function getFlag(uint8 index) external view returns (bool) {
        return (flagsBitmap & (1 << index)) != 0;
    }
}
