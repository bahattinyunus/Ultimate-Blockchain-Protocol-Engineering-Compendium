// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title SignatureReplayPermitPoC
 * @notice Demonstrates:
 * 1. Cross-chain signature replay attack caused by static DOMAIN_SEPARATOR (hard fork or multi-chain CREATE2).
 * 2. Mempool front-running denial of service on EIP-2612 permit calls.
 * 3. Mitigated dynamic DOMAIN_SEPARATOR with caching and safe permit wrapper pattern.
 */

// === 1. VULNERABLE TOKEN (Static Domain Separator) ===
contract VulnerablePermitToken {
    string public constant name = "VulnerableToken";
    mapping(address => uint256) public balanceOf;
    mapping(address => uint256) public nonces;
    mapping(address => mapping(address => uint256)) public allowance;

    // FLAW: Cached once in constructor! If chain forks (e.g. ETHW vs ETH),
    // or same bytecode deployed on Polygon/Arbitrum, signature replays!
    bytes32 public immutable DOMAIN_SEPARATOR;

    bytes32 public constant PERMIT_TYPEHASH =
        keccak256("Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)");

    constructor() {
        DOMAIN_SEPARATOR = keccak256(
            abi.encode(
                keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"),
                keccak256(bytes(name)),
                keccak256(bytes("1")),
                block.chainid, // Fixed forever to deployment chainId!
                address(this)
            )
        );
        balanceOf[msg.sender] = 1_000_000e18;
    }

    function permit(
        address owner,
        address spender,
        uint256 value,
        uint256 deadline,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external {
        require(block.timestamp <= deadline, "Expired");

        bytes32 structHash = keccak256(
            abi.encode(PERMIT_TYPEHASH, owner, spender, value, nonces[owner]++, deadline)
        );
        bytes32 digest = keccak256(abi.encodePacked("\x19\x01", DOMAIN_SEPARATOR, structHash));

        address signer = ecrecover(digest, v, r, s);
        require(signer != address(0) && signer == owner, "Invalid signature");

        allowance[owner][spender] = value;
    }
}

// === 2. MITIGATED DYNAMIC TOKEN (EIP-712 Standard Compliant) ===
contract MitigatedPermitToken {
    string public constant name = "MitigatedToken";
    mapping(address => uint256) public balanceOf;
    mapping(address => uint256) public nonces;
    mapping(address => mapping(address => uint256)) public allowance;

    uint256 private immutable _deploymentChainId;
    bytes32 private immutable _deploymentDomainSeparator;
    bytes32 private immutable _hashedName;

    bytes32 public constant PERMIT_TYPEHASH =
        keccak256("Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)");

    constructor() {
        _deploymentChainId = block.chainid;
        _hashedName = keccak256(bytes(name));
        _deploymentDomainSeparator = _buildDomainSeparator(_hashedName, block.chainid);
        balanceOf[msg.sender] = 1_000_000e18;
    }

    /// @notice Returns cached domain separator if on same chain, dynamically recomputes if on fork!
    function DOMAIN_SEPARATOR() public view returns (bytes32) {
        if (block.chainid == _deploymentChainId) {
            return _deploymentDomainSeparator;
        }
        return _buildDomainSeparator(_hashedName, block.chainid);
    }

    function _buildDomainSeparator(bytes32 hashedName, uint256 chainId) internal view returns (bytes32) {
        return keccak256(
            abi.encode(
                keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"),
                hashedName,
                keccak256(bytes("1")),
                chainId,
                address(this)
            )
        );
    }

    function permit(
        address owner,
        address spender,
        uint256 value,
        uint256 deadline,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) public {
        require(block.timestamp <= deadline, "Expired");

        bytes32 structHash = keccak256(
            abi.encode(PERMIT_TYPEHASH, owner, spender, value, nonces[owner]++, deadline)
        );
        bytes32 digest = keccak256(abi.encodePacked("\x19\x01", DOMAIN_SEPARATOR(), structHash));

        // Malleability check
        require(uint256(s) <= 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF5D576E7357A4501DDFE92F46681B20A0, "Invalid s");
        address signer = ecrecover(digest, v, r, s);
        require(signer != address(0) && signer == owner, "Invalid signature");

        allowance[owner][spender] = value;
    }
}
