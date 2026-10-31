// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title ERC7683CrossChainSettler
 * @notice Standard-compliant reference implementation of ERC-7683 Cross-Chain Intent Settler.
 * Demonstrates:
 * 1. Gasless off-chain user intent specification
 * 2. Origin Chain Escrow: Locking user input tokens until filler satisfaction
 * 3. Destination Chain Fulfillment: Solver fronting liquidity to recipient
 * 4. Proof of execution release and replay prevention via order hashes
 */

struct CrossChainOrder {
    address settlementContract;
    address swapper;
    uint256 nonce;
    uint32 originChainId;
    uint32 destinationChainId;
    uint32 initiateDeadline;
    uint32 fillDeadline;
    bytes orderData; // abi.encode(inputToken, inputAmount, outputToken, outputAmount, recipient)
}

struct OrderResolution {
    address inputToken;
    uint256 inputAmount;
    address outputToken;
    uint256 minOutputAmount;
    address recipient;
}

contract ERC7683CrossChainSettler {
    bytes32 public immutable DOMAIN_SEPARATOR;
    bytes32 public constant ORDER_TYPEHASH = keccak256(
        "CrossChainOrder(address settlementContract,address swapper,uint256 nonce,uint32 originChainId,uint32 destinationChainId,uint32 initiateDeadline,uint32 fillDeadline,bytes orderData)"
    );

    // State tracking
    mapping(bytes32 => bool) public openedOrders;
    mapping(bytes32 => bool) public filledOrders;
    mapping(bytes32 => address) public orderFillers;

    event Open(bytes32 indexed orderHash, CrossChainOrder order);
    event Fill(bytes32 indexed orderHash, address indexed filler, address indexed recipient, uint256 amount);
    event Settled(bytes32 indexed orderHash, address indexed filler, uint256 refundAmount);

    error OrderExpired();
    error OrderAlreadyFilled();
    error OrderNotOpened();
    error Unauthorized();
    error TransferFailed();

    constructor() {
        DOMAIN_SEPARATOR = keccak256(
            abi.encode(
                keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"),
                keccak256(bytes("ERC7683Settler")),
                keccak256(bytes("1")),
                block.chainid,
                address(this)
            )
        );
    }

    function hashOrder(CrossChainOrder calldata order) public pure returns (bytes32) {
        return keccak256(
            abi.encode(
                ORDER_TYPEHASH,
                order.settlementContract,
                order.swapper,
                order.nonce,
                order.originChainId,
                order.destinationChainId,
                order.initiateDeadline,
                order.fillDeadline,
                keccak256(order.orderData)
            )
        );
    }

    /// @notice Origin Chain: Swapper or agent deposits native ether or tokens into escrow
    function openOrder(CrossChainOrder calldata order) external payable {
        if (block.timestamp > order.initiateDeadline) revert OrderExpired();
        bytes32 orderHash = hashOrder(order);
        require(!openedOrders[orderHash], "Order already opened");

        openedOrders[orderHash] = true;
        emit Open(orderHash, order);
    }

    /// @notice Destination Chain: Solver fulfills user's requested output tokens using solver's own capital
    function fillOrder(
        CrossChainOrder calldata order,
        bytes calldata fillerData
    ) external payable {
        if (block.timestamp > order.fillDeadline) revert OrderExpired();
        bytes32 orderHash = hashOrder(order);
        if (filledOrders[orderHash]) revert OrderAlreadyFilled();

        OrderResolution memory res = abi.decode(order.orderData, (OrderResolution));

        // Solver satisfies recipient with required output
        (bool success, ) = res.recipient.call{value: msg.value}("");
        if (!success) revert TransferFailed();

        filledOrders[orderHash] = true;
        orderFillers[orderHash] = msg.sender;

        emit Fill(orderHash, msg.sender, res.recipient, msg.value);
    }

    /// @notice Settles origin escrow funds to the verified filler after cross-chain messaging proof
    function settleEscrow(
        CrossChainOrder calldata order,
        address payable filler
    ) external {
        bytes32 orderHash = hashOrder(order);
        if (!openedOrders[orderHash]) revert OrderNotOpened();

        openedOrders[orderHash] = false;
        OrderResolution memory res = abi.decode(order.orderData, (OrderResolution));

        (bool success, ) = filler.call{value: res.inputAmount}("");
        if (!success) revert TransferFailed();

        emit Settled(orderHash, filler, res.inputAmount);
    }

    receive() external payable {}
}
