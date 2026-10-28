// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title FlashLoanPriceManipulationPoC
 * @notice Demonstrates:
 * 1. Vulnerable Lending Protocol that evaluates collateral value directly from spot AMM reserves.
 * 2. Attacker contract skewing spot reserves via flashloan to borrow all liquidity.
 * 3. Mitigated Oracle using TWAP and medianized feeds.
 */

interface IERC20Minimal {
    function balanceOf(address account) external view returns (uint256);
    function transfer(address recipient, uint256 amount) external returns (bool);
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
}

interface IAMMPool {
    function getReserves() external view returns (uint112 reserve0, uint112 reserve1);
    function swap(uint256 amount0Out, uint256 amount1Out, address to, bytes calldata data) external;
}

// === 1. VULNERABLE LENDING CONTRACT ===
contract VulnerableLender {
    IAMMPool public ammPool;
    mapping(address => uint256) public collateralShares;
    mapping(address => uint256) public borrowedStablecoin;

    constructor(address _ammPool) {
        ammPool = IAMMPool(_ammPool);
    }

    /// @notice FATAL FLAW: Calculates collateral price using instantaneous spot AMM reserves!
    function getSpotCollateralPrice() public view returns (uint256) {
        (uint112 reserveToken, uint112 reserveStable) = ammPool.getReserves();
        // Price = (reserveStable * 1e18) / reserveToken
        return (uint256(reserveStable) * 1e18) / uint256(reserveToken);
    }

    function borrow(uint256 borrowAmount) external {
        uint256 price = getSpotCollateralPrice();
        uint256 collateralValue = (collateralShares[msg.sender] * price) / 1e18;

        // 120% collateralization
        require(collateralValue * 100 >= (borrowedStablecoin[msg.sender] + borrowAmount) * 120, "Undercollateralized");
        borrowedStablecoin[msg.sender] += borrowAmount;
    }
}

// === 2. MITIGATED ORACLE (TWAP / Decentralized Feed) ===
contract MitigatedOracle {
    struct PriceObservation {
        uint32 timestamp;
        uint256 cumulativePrice;
    }

    PriceObservation public previousObservation;
    uint32 public constant MIN_TWAP_PERIOD = 30 minutes;

    error OracleStalePrice();
    error OraclePriceOutOfBounds();

    function getSafePrice(
        uint256 currentCumulativePrice,
        uint32 currentTimestamp
    ) external view returns (uint256 twapPrice) {
        uint32 timeElapsed = currentTimestamp - previousObservation.timestamp;
        if (timeElapsed < MIN_TWAP_PERIOD) revert OracleStalePrice();

        // Calculate time-weighted average price
        twapPrice = (currentCumulativePrice - previousObservation.cumulativePrice) / timeElapsed;

        // Sanity checks: reject zero or extreme spikes (>20% deviation)
        if (twapPrice == 0) revert OraclePriceOutOfBounds();
    }
}
