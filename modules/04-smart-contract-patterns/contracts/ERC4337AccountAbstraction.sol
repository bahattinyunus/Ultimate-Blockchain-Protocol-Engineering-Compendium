// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title ERC4337AccountAbstraction
 * @notice Production-grade ERC-4337 (v0.7 standard) Smart Contract Wallet.
 * Demonstrates:
 * 1. EntryPoint validation flow (validateUserOp)
 * 2. Gas pre-funding mechanism (missingAccountFunds)
 * 3. Replay protection using 2D nonces (uint192 key, uint64 sequence)
 * 4. Arbitrary single and batched execution (execute, executeBatch)
 * 5. Signature validation with ECDSA and low-s enforcement
 */

struct PackedUserOperation {
    address sender;
    uint256 nonce;
    bytes initCode;
    bytes callData;
    bytes32 accountGasLimits;
    uint256 preVerificationGas;
    bytes32 gasFees;
    bytes paymasterAndData;
    bytes signature;
}

contract ERC4337AccountAbstraction {
    address public immutable entryPoint;
    address public owner;

    // 2D Nonce tracking: mapping(key => sequence)
    mapping(uint192 => uint64) public nonces;

    event Executed(address indexed target, uint256 value, bytes data);
    event BatchExecuted(uint256 totalOperations);
    event OwnerChanged(address indexed previousOwner, address indexed newOwner);

    error OnlyEntryPoint();
    error OnlyOwnerOrEntryPoint();
    error InvalidSignature();
    error InvalidNonce();
    error ExecutionFailed();

    modifier onlyEntryPoint() {
        if (msg.sender != entryPoint) revert OnlyEntryPoint();
        _;
    }

    modifier onlyOwnerOrEntryPoint() {
        if (msg.sender != owner && msg.sender != entryPoint) revert OnlyOwnerOrEntryPoint();
        _;
    }

    constructor(address _entryPoint, address _owner) {
        entryPoint = _entryPoint;
        owner = _owner;
    }

    /// @notice ERC-4337 Core entrypoint callback to validate UserOperation
    function validateUserOp(
        PackedUserOperation calldata userOp,
        bytes32 userOpHash,
        uint256 missingAccountFunds
    ) external onlyEntryPoint returns (uint256 validationData) {
        // Step 1: Validate Nonce (2D nonce check)
        uint192 key = uint192(userOp.nonce >> 64);
        uint64 seq = uint64(userOp.nonce);
        if (seq != nonces[key]) revert InvalidNonce();
        nonces[key] = seq + 1;

        // Step 2: Validate Signature
        bytes32 ethSignedMessageHash = keccak256(
            abi.encodePacked("\x19Ethereum Signed Message:\n32", userOpHash)
        );
        if (!_isValidSignature(ethSignedMessageHash, userOp.signature)) {
            // Return validationData = 1 (SIG_VALIDATION_FAILED)
            return 1;
        }

        // Step 3: Pay pre-fund to EntryPoint if needed
        if (missingAccountFunds > 0) {
            (bool success, ) = entryPoint.call{value: missingAccountFunds}("");
            require(success, "Pre-fund failed");
        }

        // Return 0: Valid signature, no time-range restrictions
        return 0;
    }

    /// @notice Execute single transaction
    function execute(
        address dest,
        uint256 value,
        bytes calldata func
    ) external onlyOwnerOrEntryPoint {
        (bool success, bytes memory result) = dest.call{value: value}(func);
        if (!success) {
            assembly {
                revert(add(result, 32), mload(result))
            }
        }
        emit Executed(dest, value, func);
    }

    /// @notice Execute batch of transactions atomically
    function executeBatch(
        address[] calldata dests,
        uint256[] calldata values,
        bytes[] calldata funcs
    ) external onlyOwnerOrEntryPoint {
        require(dests.length == values.length && values.length == funcs.length, "Length mismatch");
        for (uint256 i = 0; i < dests.length; ) {
            (bool success, bytes memory result) = dests[i].call{value: values[i]}(funcs[i]);
            if (!success) {
                assembly {
                    revert(add(result, 32), mload(result))
                }
            }
            unchecked {
                ++i;
            }
        }
        emit BatchExecuted(dests.length);
    }

    function _isValidSignature(bytes32 hash, bytes calldata sig) internal view returns (bool) {
        if (sig.length != 65) return false;
        bytes32 r;
        bytes32 s;
        uint8 v;
        assembly {
            r := calldataload(sig.offset)
            s := calldataload(add(sig.offset, 32))
            v := byte(0, calldataload(add(sig.offset, 64)))
        }
        // EIP-2 low-s check
        if (uint256(s) > 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF5D576E7357A4501DDFE92F46681B20A0) {
            return false;
        }
        address recovered = ecrecover(hash, v, r, s);
        return recovered != address(0) && recovered == owner;
    }

    receive() external payable {}
}
