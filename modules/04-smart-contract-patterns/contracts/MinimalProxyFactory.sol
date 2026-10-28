// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title MinimalProxyFactory (EIP-1167)
 * @notice Factory deploying 45-byte immutable delegator contracts using CREATE and CREATE2.
 * Bytecode structure:
 * 0x363d3d373d3d3d363d73 <20-byte implementation> 5af43d82803e903d91602b57fd5bf3
 */
contract MinimalProxyFactory {
    event CloneCreated(address indexed target, address indexed cloneAddress);

    error DeploymentFailed();
    error ZeroAddress();

    /// @notice Clones `implementation` using standard CREATE
    function clone(address implementation) external returns (address instance) {
        if (implementation == address(0)) revert ZeroAddress();

        assembly {
            // Memory layout:
            // 0x00 - 0x09: 363d3d373d3d3d363d73 (10 bytes)
            // 0x0a - 0x1d: implementation address (20 bytes)
            // 0x1e - 0x2c: 5af43d82803e903d91602b57fd5bf3 (15 bytes)
            // Total bytecode = 45 bytes (0x2d)

            let ptr := mload(0x40)
            mstore(ptr, 0x3d602d80600a3d3981f3363d3d373d3d3d363d73000000000000000000000000)
            mstore(add(ptr, 0x14), shl(0x60, implementation))
            mstore(add(ptr, 0x28), 0x5af43d82803e903d91602b57fd5bf30000000000000000000000000000000000)
            instance := create(0, ptr, 0x37)
        }

        if (instance == address(0)) revert DeploymentFailed();
        emit CloneCreated(implementation, instance);
    }

    /// @notice Predicts deterministic CREATE2 address for a clone
    function predictCloneAddress(
        address implementation,
        bytes32 salt,
        address deployer
    ) external pure returns (address predicted) {
        bytes memory code = abi.encodePacked(
            hex"3d602d80600a3d3981f3363d3d373d3d3d363d73",
            implementation,
            hex"5af43d82803e903d91602b57fd5bf3"
        );
        bytes32 codeHash = keccak256(code);
        predicted = address(
            uint160(
                uint256(
                    keccak256(
                        abi.encodePacked(
                            bytes1(0xff),
                            deployer,
                            salt,
                            codeHash
                        )
                    )
                )
            )
        );
    }
}
