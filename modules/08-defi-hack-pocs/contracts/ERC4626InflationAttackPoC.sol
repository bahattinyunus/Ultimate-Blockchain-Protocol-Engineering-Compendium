// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title ERC-4626 Inflation (Donation) Attack PoC
 * @notice Demonstrates:
 * 1. Vulnerable naive vault without virtual shares.
 * 2. Attacker inflating share price via donation (1 wei deposit + large direct transfer).
 * 3. Victim depositor suffering 100% rounding precision loss.
 * 4. Mitigated Vault using OpenZeppelin v5 Virtual Shares & Virtual Assets offset.
 */

// === 1. NAIVE VULNERABLE VAULT ===
contract VulnerableVault {
    uint256 public totalSupply;
    uint256 public totalAssets;
    mapping(address => uint256) public balanceOf;

    function deposit(uint256 assets) external returns (uint256 shares) {
        if (totalSupply == 0) {
            shares = assets;
        } else {
            // Integer division truncation flaw:
            shares = (assets * totalSupply) / totalAssets;
        }

        require(shares > 0, "Zero shares minted");
        balanceOf[msg.sender] += shares;
        totalSupply += shares;
        totalAssets += assets;
    }

    /// @notice External direct balance increase simulates donation attack
    function simulateDonation(uint256 donationAmount) external {
        totalAssets += donationAmount;
    }

    function withdraw(uint256 shares) external returns (uint256 assets) {
        assets = (shares * totalAssets) / totalSupply;
        balanceOf[msg.sender] -= shares;
        totalSupply -= shares;
        totalAssets -= assets;
    }
}

// === 2. MITIGATED VAULT (Virtual Shares / Offset Solution) ===
contract MitigatedVault {
    uint256 public totalSupply;
    uint256 public totalAssets;
    mapping(address => uint256) public balanceOf;

    // Virtual offset: 10^3 = 1000 virtual shares & assets
    // Prevents dividing by tiny supply and makes inflation attack prohibitively expensive!
    uint256 private constant _DECIMAL_OFFSET = 3;
    uint256 private constant _VIRTUAL_OFFSET = 10 ** _DECIMAL_OFFSET;

    function deposit(uint256 assets) external returns (uint256 shares) {
        // Formally: shares = assets * (totalSupply + 10^3) / (totalAssets + 1)
        shares = (assets * (totalSupply + _VIRTUAL_OFFSET)) / (totalAssets + 1);

        require(shares > 0, "Zero shares minted");
        balanceOf[msg.sender] += shares;
        totalSupply += shares;
        totalAssets += assets;
    }

    function withdraw(uint256 shares) external returns (uint256 assets) {
        // Rounding down in favor of vault:
        assets = (shares * (totalAssets + 1)) / (totalSupply + _VIRTUAL_OFFSET);
        balanceOf[msg.sender] -= shares;
        totalSupply -= shares;
        totalAssets -= assets;
    }
}
