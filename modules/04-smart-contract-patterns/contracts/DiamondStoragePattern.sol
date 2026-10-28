// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title DiamondStoragePattern (EIP-2535 Reference)
 * @notice Demonstrates diamond storage struct positioning using unique keccak-256 slots
 * to prevent storage pointer collisions across modular facets.
 */
library LibDiamondStorage {
    bytes32 constant LENDING_STORAGE_POSITION =
        keccak256("compendium.protocol.storage.lending.facet");

    struct LendingFacetStorage {
        uint256 totalBorrowed;
        uint256 totalCollateral;
        uint256 interestRateBps;
        mapping(address => uint256) collateralOf;
        mapping(address => uint256) debtOf;
    }

    function lendingStorage() internal pure returns (LendingFacetStorage storage ds) {
        bytes32 position = LENDING_STORAGE_POSITION;
        assembly {
            ds.slot := position
        }
    }
}

contract LendingFacet {
    using LibDiamondStorage for LibDiamondStorage.LendingFacetStorage;

    event CollateralDeposited(address indexed user, uint256 amount);
    event AssetBorrowed(address indexed user, uint256 amount);

    error HealthFactorTooLow();
    error InsufficientCollateral();

    function depositCollateral() external payable {
        LibDiamondStorage.LendingFacetStorage storage ds = LibDiamondStorage.lendingStorage();
        ds.collateralOf[msg.sender] += msg.value;
        ds.totalCollateral += msg.value;
        emit CollateralDeposited(msg.sender, msg.value);
    }

    function borrow(uint256 amount) external {
        LibDiamondStorage.LendingFacetStorage storage ds = LibDiamondStorage.lendingStorage();
        uint256 collateral = ds.collateralOf[msg.sender];

        // 150% collateral ratio requirement
        if (collateral * 100 < (ds.debtOf[msg.sender] + amount) * 150) {
            revert HealthFactorTooLow();
        }

        ds.debtOf[msg.sender] += amount;
        ds.totalBorrowed += amount;

        (bool success, ) = msg.sender.call{value: amount}("");
        if (!success) revert InsufficientCollateral();

        emit AssetBorrowed(msg.sender, amount);
    }

    function getPosition(address user) external view returns (uint256 collateral, uint256 debt) {
        LibDiamondStorage.LendingFacetStorage storage ds = LibDiamondStorage.lendingStorage();
        return (ds.collateralOf[user], ds.debtOf[user]);
    }
}
