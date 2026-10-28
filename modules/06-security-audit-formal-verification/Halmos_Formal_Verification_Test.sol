// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title Halmos Formal Verification & Symbolic Execution Test
 * @notice Demonstrates symbolic execution property tests for Halmos / Foundry SMTChecker.
 */
contract VaultMock {
    uint256 public totalAssets;
    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;

    function deposit(uint256 assets) external {
        require(assets > 0, "Zero assets");
        uint256 shares = assets; // 1:1 simplified
        totalSupply += shares;
        totalAssets += assets;
        balanceOf[msg.sender] += shares;
    }

    function withdraw(uint256 shares) external {
        require(balanceOf[msg.sender] >= shares, "Insufficient shares");
        require(totalSupply >= shares, "Supply underflow");
        require(totalAssets >= shares, "Assets underflow");

        balanceOf[msg.sender] -= shares;
        totalSupply -= shares;
        totalAssets -= shares;
    }
}

contract HalmosFormalVerificationTest {
    VaultMock internal vault;

    function setUp() public {
        vault = new VaultMock();
    }

    /// @notice Symbolic test: Solvency is strictly preserved for any symbolic deposit amount
    function check_solvency_after_deposit(uint256 symbolicAssets) public {
        // Assume symbolic preconditions
        require(symbolicAssets > 0 && symbolicAssets < 1e30);

        uint256 assetsBefore = vault.totalAssets();
        uint256 supplyBefore = vault.totalSupply();

        vault.deposit(symbolicAssets);

        // Prove invariant holds across entire symbolic domain
        assert(vault.totalAssets() == assetsBefore + symbolicAssets);
        assert(vault.totalSupply() == supplyBefore + symbolicAssets);
        assert(vault.totalAssets() >= vault.totalSupply());
    }
}
