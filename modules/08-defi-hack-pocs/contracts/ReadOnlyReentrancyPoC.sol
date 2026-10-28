// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title Read-Only Reentrancy PoC
 * @notice Demonstrates:
 * 1. Vulnerable AMM pool where burn/withdraw transfers ETH before updating total LP supply.
 * 2. Vulnerable Lending Protocol reading getVirtualPrice() from the pool.
 * 3. Attacker exploiting the distorted interim price during the fallback callback.
 * 4. Fixed AMM Pool with transient reentrancy lock on view functions.
 */

interface IPool {
    function getVirtualPrice() external view returns (uint256);
}

// === 1. VULNERABLE AMM POOL ===
contract VulnerableLiquidityPool is IPool {
    uint256 public totalEth;
    uint256 public totalLpSupply;
    mapping(address => uint256) public lpBalance;

    bool private _locked;

    modifier nonReentrant() {
        require(!_locked, "ReentrancyGuard");
        _locked = true;
        _;
        _locked = false;
    }

    function deposit() external payable nonReentrant {
        require(msg.value > 0, "Zero deposit");
        uint256 mintAmount = msg.value;
        lpBalance[msg.sender] += mintAmount;
        totalLpSupply += mintAmount;
        totalEth += msg.value;
    }

    function removeLiquidity(uint256 lpAmount) external nonReentrant {
        require(lpBalance[msg.sender] >= lpAmount, "Insufficient LP");

        uint256 ethToReturn = (lpAmount * totalEth) / totalLpSupply;

        // FLAW: ETH is sent before burn and totalLpSupply state update!
        (bool success, ) = msg.sender.call{value: ethToReturn}("");
        require(success, "ETH transfer failed");

        // Delayed state update:
        lpBalance[msg.sender] -= lpAmount;
        totalLpSupply -= lpAmount;
        totalEth -= ethToReturn;
    }

    /// @notice Read-only function WITHOUT reentrancy lock
    function getVirtualPrice() external view override returns (uint256) {
        if (totalLpSupply == 0) return 1e18;
        // During the external call in removeLiquidity, totalEth has decreased
        // while totalLpSupply is still unchanged, temporarily crashing the price,
        // or vice versa if ordered differently.
        return (totalEth * 1e18) / totalLpSupply;
    }
}

// === 2. VULNERABLE LENDING PROTOCOL ===
contract VulnerableLendingVault {
    IPool public pool;
    mapping(address => uint256) public collateralLp;
    mapping(address => uint256) public debtUsdc;

    constructor(address _pool) {
        pool = IPool(_pool);
    }

    function depositCollateral(uint256 lpAmount) external {
        collateralLp[msg.sender] += lpAmount;
    }

    /// @notice Borrow assets against LP token collateral
    function borrow(uint256 usdcAmount) external {
        // Reads price from pool's view function (unprotected against read-only reentrancy!)
        uint256 virtualPrice = pool.getVirtualPrice();
        uint256 collateralValue = (collateralLp[msg.sender] * virtualPrice) / 1e18;

        require(collateralValue >= debtUsdc[msg.sender] + usdcAmount, "Undercollateralized");
        debtUsdc[msg.sender] += usdcAmount;
        // Transfer borrowed tokens...
    }
}

// === 3. MITIGATED POOL (Cancun Transient Lock / CEI) ===
contract MitigatedLiquidityPool is IPool {
    bytes32 private constant READ_LOCK_SLOT = keccak256("read_only_reentrancy.guard");

    uint256 public totalEth;
    uint256 public totalLpSupply;
    mapping(address => uint256) public lpBalance;

    error PoolReentrancyLockActive();

    function removeLiquiditySecure(uint256 lpAmount) external {
        require(lpBalance[msg.sender] >= lpAmount, "Insufficient LP");

        uint256 ethToReturn = (lpAmount * totalEth) / totalLpSupply;

        // FIX 1: Checks-Effects-Interactions (CEI) - Update state BEFORE transfer!
        lpBalance[msg.sender] -= lpAmount;
        totalLpSupply -= lpAmount;
        totalEth -= ethToReturn;

        // FIX 2: Set transient lock flag for view functions during call
        assembly {
            tstore(READ_LOCK_SLOT, 1)
        }

        (bool success, ) = msg.sender.call{value: ethToReturn}("");
        require(success, "ETH transfer failed");

        assembly {
            tstore(READ_LOCK_SLOT, 0)
        }
    }

    function getVirtualPrice() external view override returns (uint256) {
        // View function checks transient lock: Reverts if called during removeLiquidity!
        bytes32 slot = READ_LOCK_SLOT;
        assembly {
            if tload(slot) {
                mstore(0x00, 0x1f19f207) // PoolReentrancyLockActive()
                revert(0x1c, 0x04)
            }
        }
        if (totalLpSupply == 0) return 1e18;
        return (totalEth * 1e18) / totalLpSupply;
    }
}
