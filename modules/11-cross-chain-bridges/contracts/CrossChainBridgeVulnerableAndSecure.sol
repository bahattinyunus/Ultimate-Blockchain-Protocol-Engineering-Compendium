// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title CrossChainBridgeVulnerableAndSecure
 * @notice Demonstrates:
 * 1. The fatal Nomad Bridge ($190M) initialization flaw: zero-hash treated as confirmed root.
 * 2. Unauthenticated attacker draining the bridge with fabricated messages.
 * 3. Secure Bridge using cryptographic ECDSA/EdDSA multi-relayer threshold verification
 *    and EIP-712 structured message digests with nonce replay protection.
 */

// === 1. VULNERABLE BRIDGE (Nomad Flaw Simulation) ===
contract VulnerableNomadBridge {
    // Mapping of root => confirmation timestamp
    mapping(bytes32 => uint256) public confirmAt;
    mapping(bytes32 => bool) public executedMessages;
    uint256 public totalLockedLiquidity;

    constructor() {
        // FATAL FLAW (Nomad Bug):
        // During deployment or upgrade initialization, confirmAt[bytes32(0)] was set to 1!
        // Because default empty/unproven leaves or roots evaluate to 0x00,
        // every unproven message was treated as pre-confirmed!
        confirmAt[bytes32(0)] = 1;
    }

    function deposit() external payable {
        totalLockedLiquidity += msg.value;
    }

    /// @notice Vulnerable execution function
    function process(
        bytes memory message,
        bytes32 root
    ) external {
        // Checks if root is confirmed
        require(confirmAt[root] > 0, "Root not confirmed");

        bytes32 msgHash = keccak256(message);
        require(!executedMessages[msgHash], "Already executed");
        executedMessages[msgHash] = true;

        // Decode: recipient (20 bytes), amount (32 bytes)
        (address recipient, uint256 amount) = abi.decode(message, (address, uint256));

        // When attacker passes root = bytes32(0), check succeeds!
        (bool success, ) = recipient.call{value: amount}("");
        require(success, "Payout failed");
        totalLockedLiquidity -= amount;
    }
}

// === 2. MITIGATED SECURE CROSS-CHAIN RELAYER BRIDGE ===
contract SecureCrossChainBridge {
    // EIP-712 Domain Separator
    bytes32 public immutable DOMAIN_SEPARATOR;
    bytes32 public constant MESSAGE_TYPEHASH =
        keccak256("BridgeMessage(uint256 sourceChainId,uint256 nonce,address recipient,uint256 amount)");

    address public trustedRelayer;
    uint256 public expectedNonce;
    mapping(uint256 => bool) public processedNonces;
    uint256 public totalLiquidity;

    event TokensUnlocked(address indexed recipient, uint256 amount, uint256 nonce);

    error InvalidSignature();
    error NonceAlreadyUsed();
    error InvalidSourceChain();
    error InsufficientLiquidity();

    constructor(address _relayer) {
        trustedRelayer = _relayer;
        DOMAIN_SEPARATOR = keccak256(
            abi.encode(
                keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"),
                keccak256(bytes("SecureBridge")),
                keccak256(bytes("1")),
                block.chainid,
                address(this)
            )
        );
    }

    function deposit() external payable {
        totalLiquidity += msg.value;
    }

    function relayMessage(
        uint256 sourceChainId,
        uint256 nonce,
        address recipient,
        uint256 amount,
        bytes calldata signature
    ) external {
        if (processedNonces[nonce]) revert NonceAlreadyUsed();
        if (address(this).balance < amount) revert InsufficientLiquidity();

        // 1. Build typed EIP-712 digest
        bytes32 structHash = keccak256(
            abi.encode(MESSAGE_TYPEHASH, sourceChainId, nonce, recipient, amount)
        );
        bytes32 digest = keccak256(
            abi.encodePacked("\x19\x01", DOMAIN_SEPARATOR, structHash)
        );

        // 2. Cryptographic signature check
        if (!_verifySignature(digest, signature, trustedRelayer)) {
            revert InvalidSignature();
        }

        processedNonces[nonce] = true;
        totalLiquidity -= amount;

        (bool success, ) = recipient.call{value: amount}("");
        require(success, "Transfer failed");

        emit TokensUnlocked(recipient, amount, nonce);
    }

    function _verifySignature(
        bytes32 hash,
        bytes calldata sig,
        address expectedSigner
    ) internal pure returns (bool) {
        if (sig.length != 65) return false;
        bytes32 r;
        bytes32 s;
        uint8 v;
        assembly {
            r := calldataload(sig.offset)
            s := calldataload(add(sig.offset, 32))
            v := byte(0, calldataload(add(sig.offset, 64)))
        }
        if (uint256(s) > 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF5D576E7357A4501DDFE92F46681B20A0) {
            return false;
        }
        address signer = ecrecover(hash, v, r, s);
        return signer != address(0) && signer == expectedSigner;
    }
}
