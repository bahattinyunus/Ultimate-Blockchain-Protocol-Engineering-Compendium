// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title Permit2Integration
 * @notice Modern gas-optimized token interaction architecture using Uniswap Permit2.
 * Solves:
 * 1. Infinite token approval security risks
 * 2. Unpredictable front-running of standard ERC20 approve()
 * 3. Batch transfers with a single EIP-712 off-chain signature
 * 4. Automatic deadline expiration
 */

interface IPermit2 {
    struct TokenPermissions {
        address token;
        uint256 amount;
    }

    struct PermitTransferFrom {
        TokenPermissions permitted;
        uint256 nonce;
        uint256 deadline;
    }

    struct SignatureTransferDetails {
        address to;
        uint256 requestedAmount;
    }

    function permitTransferFrom(
        PermitTransferFrom memory permit,
        SignatureTransferDetails calldata transferDetails,
        address owner,
        bytes calldata signature
    ) external;
}

contract Permit2Vault {
    IPermit2 public immutable permit2;
    mapping(address => mapping(address => uint256)) public balances; // token => user => amount

    event DepositedWithPermit2(
        address indexed token,
        address indexed user,
        uint256 amount,
        uint256 nonce
    );

    error ExpiredSignature();
    error InvalidAmount();

    constructor(address _permit2) {
        permit2 = IPermit2(_permit2);
    }

    /// @notice Single-transaction deposit without prior approve() transaction!
    function depositWithPermit2(
        address token,
        uint256 amount,
        uint256 nonce,
        uint256 deadline,
        bytes calldata signature
    ) external {
        if (block.timestamp > deadline) revert ExpiredSignature();
        if (amount == 0) revert InvalidAmount();

        // Construct permit struct
        IPermit2.PermitTransferFrom memory permit = IPermit2.PermitTransferFrom({
            permitted: IPermit2.TokenPermissions({
                token: token,
                amount: amount
            }),
            nonce: nonce,
            deadline: deadline
        });

        IPermit2.SignatureTransferDetails memory transferDetails = IPermit2.SignatureTransferDetails({
            to: address(this),
            requestedAmount: amount
        });

        // Execute permit2 transfer
        permit2.permitTransferFrom(permit, transferDetails, msg.sender, signature);

        // Credit internal state
        balances[token][msg.sender] += amount;
        emit DepositedWithPermit2(token, msg.sender, amount, nonce);
    }
}
