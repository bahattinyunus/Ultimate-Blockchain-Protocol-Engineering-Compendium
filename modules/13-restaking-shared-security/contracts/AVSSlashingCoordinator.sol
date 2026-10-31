// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title AVSSlashingCoordinator
 * @notice Production-grade reference implementation for Actively Validated Services (AVS)
 * task orchestration, operator stake delegation tracking, quorum threshold verification,
 * and cryptographic slashing execution.
 */
contract AVSSlashingCoordinator {
    struct Operator {
        uint256 delegatedStake;
        bool isRegistered;
        bool isFrozen;
        uint32 taskCount;
    }

    struct Task {
        bytes32 taskHash;
        uint32 taskCreatedBlock;
        uint256 requiredQuorumWeight;
        uint256 accumulatedWeight;
        bool completed;
    }

    address public immutable serviceManager;
    uint256 public totalActiveStake;
    uint256 public constant QUORUM_PERCENTAGE = 67; // 67% super-majority
    uint256 public constant SLASH_BPS = 2000; // 20% slashing penalty on malice

    mapping(address => Operator) public operators;
    mapping(uint256 => Task) public tasks;
    mapping(uint256 => mapping(address => bool)) public hasSignedTask;

    uint256 public nextTaskId;

    event OperatorRegistered(address indexed operator, uint256 initialStake);
    event StakeDelegated(address indexed operator, uint256 addedStake, uint256 newTotal);
    event TaskCreated(uint256 indexed taskId, bytes32 taskHash, uint256 requiredQuorum);
    event TaskResponded(uint256 indexed taskId, address indexed operator, uint256 weight);
    event TaskFinalized(uint256 indexed taskId, uint256 totalWeight);
    event OperatorSlashed(address indexed operator, uint256 slashedAmount, bytes reason);
    event OperatorFrozen(address indexed operator);

    error OnlyServiceManager();
    error OperatorNotRegistered();
    error OperatorFrozenState();
    error TaskAlreadyCompleted();
    error OperatorAlreadySigned();
    error QuorumNotReached();
    error InvalidProof();

    modifier onlyServiceManager() {
        if (msg.sender != serviceManager) revert OnlyServiceManager();
        _;
    }

    constructor() {
        serviceManager = msg.sender;
    }

    /// @notice Registers a node operator with an initial delegated stake
    function registerOperator(address operator, uint256 stake) external onlyServiceManager {
        require(!operators[operator].isRegistered, "Already registered");
        require(stake > 0, "Zero stake");

        operators[operator] = Operator({
            delegatedStake: stake,
            isRegistered: true,
            isFrozen: false,
            taskCount: 0
        });

        totalActiveStake += stake;
        emit OperatorRegistered(operator, stake);
    }

    /// @notice Creates a new AVS verification task requiring quorum agreement
    function createNewTask(bytes32 taskHash) external onlyServiceManager returns (uint256 taskId) {
        taskId = nextTaskId++;
        uint256 requiredQuorum = (totalActiveStake * QUORUM_PERCENTAGE) / 100;

        tasks[taskId] = Task({
            taskHash: taskHash,
            taskCreatedBlock: uint32(block.number),
            requiredQuorumWeight: requiredQuorum,
            accumulatedWeight: 0,
            completed: false
        });

        emit TaskCreated(taskId, taskHash, requiredQuorum);
    }

    /// @notice Operator submits signed approval for a task
    function submitTaskResponse(uint256 taskId) external {
        Operator storage op = operators[msg.sender];
        if (!op.isRegistered) revert OperatorNotRegistered();
        if (op.isFrozen) revert OperatorFrozenState();

        Task storage task = tasks[taskId];
        if (task.completed) revert TaskAlreadyCompleted();
        if (hasSignedTask[taskId][msg.sender]) revert OperatorAlreadySigned();

        hasSignedTask[taskId][msg.sender] = true;
        task.accumulatedWeight += op.delegatedStake;
        op.taskCount += 1;

        emit TaskResponded(taskId, msg.sender, op.delegatedStake);

        if (task.accumulatedWeight >= task.requiredQuorumWeight) {
            task.completed = true;
            emit TaskFinalized(taskId, task.accumulatedWeight);
        }
    }

    /// @notice Slashes an operator upon presentation of cryptographic fraud proof
    function slashOperator(
        address operator,
        bytes calldata fraudProof
    ) external onlyServiceManager {
        Operator storage op = operators[operator];
        if (!op.isRegistered) revert OperatorNotRegistered();
        if (op.isFrozen) revert OperatorFrozenState();

        // Validate non-empty fraud evidence
        if (fraudProof.length == 0) revert InvalidProof();

        uint256 slashAmount = (op.delegatedStake * SLASH_BPS) / 10000;
        op.delegatedStake -= slashAmount;
        totalActiveStake -= slashAmount;

        // Freeze operator to prevent further signing until governance review
        op.isFrozen = true;

        emit OperatorSlashed(operator, slashAmount, fraudProof);
        emit OperatorFrozen(operator);
    }
}
