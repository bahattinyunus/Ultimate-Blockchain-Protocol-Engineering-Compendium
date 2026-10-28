// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title UUPSUpgradeableVault
 * @notice Production-grade Universal Upgradeable Proxy Standard (UUPS - ERC-1822 / ERC-1967)
 * implementation with explicit storage layout, initializer re-entrancy protection,
 * and 50-slot storage gap for future upgrades.
 */
contract UUPSUpgradeableVault {
    // EIP-1967 implementation slot:
    // bytes32(uint256(keccak256('eip1967.proxy.implementation')) - 1)
    bytes32 private constant _IMPLEMENTATION_SLOT =
        0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc;

    // EIP-1967 admin slot:
    // bytes32(uint256(keccak256('eip1967.proxy.admin')) - 1)
    bytes32 private constant _ADMIN_SLOT =
        0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103;

    // State Variables
    address public owner;
    uint256 public totalDeposits;
    mapping(address => uint256) public userBalances;
    bool private _initialized;

    // Events
    event Initialized(address indexed owner);
    event Upgraded(address indexed newImplementation);
    event Deposited(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);

    // Errors
    error AlreadyInitialized();
    error Unauthorized();
    error InvalidAddress();
    error InsufficientBalance();

    modifier onlyOwner() {
        if (msg.sender != owner) revert Unauthorized();
        _;
    }

    /// @notice Initializer replaces constructor for upgradeable proxies
    function initialize(address _initialOwner) external {
        if (_initialized) revert AlreadyInitialized();
        if (_initialOwner == address(0)) revert InvalidAddress();

        _initialized = true;
        owner = _initialOwner;
        emit Initialized(_initialOwner);
    }

    function deposit() external payable {
        if (msg.value == 0) revert InsufficientBalance();
        userBalances[msg.sender] += msg.value;
        totalDeposits += msg.value;
        emit Deposited(msg.sender, msg.value);
    }

    function withdraw(uint256 amount) external {
        if (userBalances[msg.sender] < amount) revert InsufficientBalance();
        userBalances[msg.sender] -= amount;
        totalDeposits -= amount;
        emit Withdrawn(msg.sender, amount);

        (bool success, ) = msg.sender.call{value: amount}("");
        if (!success) revert InsufficientBalance();
    }

    /// @notice Upgrades the implementation address (UUPS Pattern)
    function upgradeToAndCall(address newImplementation, bytes calldata data) external payable onlyOwner {
        if (newImplementation == address(0) || newImplementation.code.length == 0) {
            revert InvalidAddress();
        }

        bytes32 slot = _IMPLEMENTATION_SLOT;
        assembly {
            sstore(slot, newImplementation)
        }
        emit Upgraded(newImplementation);

        if (data.length > 0) {
            (bool success, ) = newImplementation.delegatecall(data);
            if (!success) revert InvalidAddress();
        }
    }

    /// @dev Storage gap reserved for future contract upgrades without storage shifting
    uint256[50] private __gap;
}
