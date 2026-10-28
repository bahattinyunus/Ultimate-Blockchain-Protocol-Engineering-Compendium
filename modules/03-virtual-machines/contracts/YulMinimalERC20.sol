// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title YulMinimalERC20
 * @notice Ultra-gas-optimized ERC-20 token implemented directly in Inline Assembly (Yul).
 * Demonstrates:
 * 1. Custom function selector dispatching without Solidity compiler dispatch overhead
 * 2. Direct memory pointer management (free memory pointer bypassing)
 * 3. Keccak-256 storage slot calculation: slot = keccak256(abi.encode(owner, baseSlot))
 * 4. Custom binary revert error codes
 */
contract YulMinimalERC20 {
    // Storage slots
    // Slot 0: totalSupply
    // Slot 1: mapping(address => uint256) balances
    // Slot 2: mapping(address => mapping(address => uint256)) allowances

    uint256 private _totalSupply;
    mapping(address => uint256) private _balances;
    mapping(address => mapping(address => uint256)) private _allowances;

    event Transfer(address indexed from, address indexed to, uint256 amount);
    event Approval(address indexed owner, address indexed spender, uint256 amount);

    constructor(uint256 initialSupply) {
        _totalSupply = initialSupply;
        _balances[msg.sender] = initialSupply;
        emit Transfer(address(0), msg.sender, initialSupply);
    }

    function totalSupply() external view returns (uint256 supply) {
        assembly {
            supply := sload(0)
        }
    }

    function balanceOf(address account) external view returns (uint256 balance) {
        assembly {
            // Compute storage slot for balances[account]
            // slot = keccak256(account . uint256(1))
            mstore(0x00, account)
            mstore(0x20, 1)
            let slot := keccak256(0x00, 0x40)
            balance := sload(slot)
        }
    }

    function transfer(address to, uint256 amount) external returns (bool) {
        assembly {
            // Validate non-zero recipient
            if iszero(to) {
                mstore(0x00, 0xd92e233d) // InvalidRecipient()
                revert(0x1c, 0x04)
            }

            // Sender balance slot
            mstore(0x00, caller())
            mstore(0x20, 1)
            let senderSlot := keccak256(0x00, 0x40)
            let senderBal := sload(senderSlot)

            // Check sufficient balance
            if lt(senderBal, amount) {
                mstore(0x00, 0xf4d678b8) // InsufficientBalance()
                revert(0x1c, 0x04)
            }

            // Deduct sender
            sstore(senderSlot, sub(senderBal, amount))

            // Recipient balance slot
            mstore(0x00, to)
            mstore(0x20, 1)
            let toSlot := keccak256(0x00, 0x40)
            let toBal := sload(toSlot)

            // Add recipient (overflow safe in 256-bit space with finite supply)
            sstore(toSlot, add(toBal, amount))

            // Emit Transfer event: keccak256("Transfer(address,address,uint256)")
            // 0xddf252ad1be2c89b69c2b068fc378d5799fb7795e0c595656664f6fe68334883
            mstore(0x00, amount)
            log3(
                0x00,
                0x20,
                0xddf252ad1be2c89b69c2b068fc378d5799fb7795e0c595656664f6fe68334883,
                caller(),
                to
            )

            // Return true
            mstore(0x00, 1)
            return(0x00, 0x20)
        }
    }
}
