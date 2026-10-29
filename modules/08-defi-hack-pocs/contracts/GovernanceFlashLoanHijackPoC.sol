// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title GovernanceFlashLoanHijackPoC
 * @notice Recreates the Beanstalk Farms ($182M) and Build Finance style Governance Flash Loan Hijack.
 * Demonstrates:
 * 1. Vulnerable Governance contract checking live balanceOf(msg.sender) instead of past block checkpoint.
 * 2. Attacker borrowing voting tokens via Flash Loan to create, vote, and execute a proposal in 1 transaction.
 * 3. Mitigated Governance contract using historical block snapshots (getPastVotes / ERC20Votes).
 */

interface IERC20Token {
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
}

// === 1. VULNERABLE GOVERNANCE CONTRACT ===
contract VulnerableDAO {
    IERC20Token public govToken;
    address public treasury;

    struct Proposal {
        address target;
        bytes callData;
        uint256 votesFor;
        bool executed;
    }

    Proposal[] public proposals;
    uint256 public constant QUORUM_VOTES = 1_000_000e18;

    constructor(address _govToken, address _treasury) {
        govToken = IERC20Token(_govToken);
        treasury = _treasury;
    }

    function createProposal(address target, bytes calldata data) external returns (uint256 id) {
        id = proposals.length;
        proposals.push(Proposal({
            target: target,
            callData: data,
            votesFor: 0,
            executed: false
        }));
    }

    /// @notice FATAL FLAW: Checks current balanceOf(msg.sender) instead of past block checkpoint!
    function vote(uint256 proposalId) external {
        Proposal storage p = proposals[proposalId];
        require(!p.executed, "Already executed");

        uint256 votingPower = govToken.balanceOf(msg.sender);
        require(votingPower > 0, "No voting power");

        p.votesFor += votingPower;

        // FATAL FLAW: Allows same-block execution without timelock!
        if (p.votesFor >= QUORUM_VOTES) {
            p.executed = true;
            (bool success, ) = p.target.call(p.callData);
            require(success, "Proposal execution failed");
        }
    }
}

// === 2. MITIGATED GOVERNANCE (Checkpoint Snapshots + Timelock) ===
interface IVotesToken {
    function getPastVotes(address account, uint256 timepoint) external view returns (uint256);
}

contract MitigatedDAO {
    IVotesToken public govToken;
    uint256 public constant VOTING_DELAY_BLOCKS = 100; // 100 blocks delay before voting opens
    uint256 public constant TIMELOCK_DELAY = 2 days;   // 2 days delay before execution

    struct SecureProposal {
        address target;
        bytes callData;
        uint256 snapshotBlock;
        uint256 votesFor;
        uint256 executionEta;
        bool executed;
        mapping(address => bool) hasVoted;
    }

    mapping(uint256 => SecureProposal) public proposals;
    uint256 public proposalCount;

    error VotingNotStarted();
    error TimelockNotMatured();
    error AlreadyVoted();

    constructor(address _govToken) {
        govToken = IVotesToken(_govToken);
    }

    function propose(address target, bytes calldata data) external returns (uint256 id) {
        id = ++proposalCount;
        SecureProposal storage p = proposals[id];
        p.target = target;
        p.callData = data;
        // Snapshot is pinned to past or future block:
        p.snapshotBlock = block.number + VOTING_DELAY_BLOCKS;
    }

    function voteSecure(uint256 proposalId) external {
        SecureProposal storage p = proposals[proposalId];
        if (block.number <= p.snapshotBlock) revert VotingNotStarted();
        if (p.hasVoted[msg.sender]) revert AlreadyVoted();

        // FIX: Queries historical voting power at snapshotBlock!
        // Flashloans in current block have ZERO historical power.
        uint256 pastVotes = govToken.getPastVotes(msg.sender, p.snapshotBlock);
        require(pastVotes > 0, "No historical votes");

        p.hasVoted[msg.sender] = true;
        p.votesFor += pastVotes;
    }
}
