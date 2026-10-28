// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title TransientStorageReentrancyGuard
 * @notice Production-ready Cancun Transient Storage (EIP-1153) Reentrancy Lock.
 * @dev Replaces traditional SSTORE/SLOAD reentrancy guards (2100+ gas) with
 * TSTORE/TLOAD (100 gas), saving ~2000+ gas per guarded call and automatically
 * resetting at transaction boundary with zero post-call cleanup overhead.
 */
abstract contract TransientStorageReentrancyGuard {
    // keccak256("eip1153.reentrancy_guard.slot") - 1
    bytes32 private constant REENTRANCY_GUARD_SLOT =
        0x8e94f87f4e91244e83c27f67899479bfa780d6f9a77ee2d79313db4ec8eef80f;

    error ReentrancyGuardReentrantCall();

    modifier nonReentrant() {
        _nonReentrantBefore();
        _;
        _nonReentrantAfter();
    }

    function _nonReentrantBefore() internal {
        bytes32 slot = REENTRANCY_GUARD_SLOT;
        assembly {
            // Check transient lock value
            if tload(slot) {
                // Store selector for custom error ReentrancyGuardReentrantCall()
                mstore(0x00, 0x324d08e5) // bytes4(keccak256("ReentrancyGuardReentrantCall()"))
                revert(0x1c, 0x04)
            }
            // Acquire lock: value 1
            tstore(slot, 1)
        }
    }

    function _nonReentrantAfter() internal {
        bytes32 slot = REENTRANCY_GUARD_SLOT;
        assembly {
            // Release lock: value 0
            tstore(slot, 0)
        }
    }
}
