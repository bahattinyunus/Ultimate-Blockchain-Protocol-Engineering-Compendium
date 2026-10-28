#!/usr/bin/env python3
"""
Ethereum Gasper Consensus Simulator:
1. LMD-GHOST (Latest Message Driven Greediest Heaviest Observed SubTree)
2. Casper FFG (Friendly Finality Gadget) Checkpoint Justification & Finalization
"""

from typing import Dict, List, Optional, Set


class Block:
    def __init__(self, block_id: str, parent_id: Optional[str], slot: int, epoch: int):
        self.block_id = block_id
        self.parent_id = parent_id
        self.slot = slot
        self.epoch = epoch
        self.children: List[str] = []

    def __repr__(self):
        return f"Block({self.block_id}, slot={self.slot}, epoch={self.epoch})"


class GasperConsensusSimulator:
    def __init__(self, validators: Dict[str, float]):
        """
        validators: map of validator_name -> stake_weight
        """
        self.validators = validators
        self.total_stake = sum(validators.values())
        self.supermajority_threshold = (2.0 / 3.0) * self.total_stake

        # Block store
        self.blocks: Dict[str, Block] = {}
        # Genesis block
        genesis = Block(block_id="genesis", parent_id=None, slot=0, epoch=0)
        self.blocks["genesis"] = genesis

        # LMD votes: validator -> latest voted block_id
        self.latest_messages: Dict[str, str] = {}

        # Casper FFG state
        self.checkpoints: Dict[int, str] = {0: "genesis"}  # epoch -> checkpoint block_id
        self.justified_epochs: Set[int] = {0}
        self.finalized_epochs: Set[int] = {0}
        self.checkpoint_votes: Dict[int, float] = {0: self.total_stake}

    def add_block(self, block_id: str, parent_id: str, slot: int, epoch: int):
        if parent_id not in self.blocks:
            raise ValueError(f"Parent {parent_id} does not exist")
        block = Block(block_id, parent_id, slot, epoch)
        self.blocks[block_id] = block
        self.blocks[parent_id].children.append(block_id)
        if slot % 32 == 0:  # Checkpoint slot
            self.checkpoints[epoch] = block_id

    def vote(self, validator: str, block_id: str):
        """Records an LMD-GHOST attestation vote."""
        if block_id not in self.blocks:
            raise ValueError("Unknown block")
        self.latest_messages[validator] = block_id

    def _get_subtree_weight(self, root_id: str) -> float:
        """Calculates cumulative stake weight voting for root_id or its descendants."""
        descendants: Set[str] = set()
        stack = [root_id]
        while stack:
            curr = stack.pop()
            descendants.add(curr)
            stack.extend(self.blocks[curr].children)

        weight = 0.0
        for val, voted_block in self.latest_messages.items():
            if voted_block in descendants:
                weight += self.validators[val]
        return weight

    def get_head(self) -> str:
        """
        Executes LMD-GHOST rule:
        Starts from the latest justified checkpoint and iteratively selects
        the child with the highest subtree weight until a leaf is reached.
        """
        # Start at latest justified checkpoint
        latest_justified_epoch = max(self.justified_epochs)
        current = self.checkpoints[latest_justified_epoch]

        while self.blocks[current].children:
            best_child = None
            best_weight = -1.0
            for child_id in self.blocks[current].children:
                w = self._get_subtree_weight(child_id)
                if w > best_weight:
                    best_weight = w
                    best_child = child_id
            current = best_child

        return current

    def cast_checkpoint_attestations(self, target_epoch: int, voter_stakes: List[float]):
        """Simulates FFG attestations for target epoch checkpoint."""
        total_voted = sum(voter_stakes)
        self.checkpoint_votes[target_epoch] = total_voted

        if total_voted >= self.supermajority_threshold:
            self.justified_epochs.add(target_epoch)
            # Casper FFG Finalization rule: If epoch E is justified and E-1 was already justified, E-1 is finalized
            prev_epoch = target_epoch - 1
            if prev_epoch in self.justified_epochs:
                self.finalized_epochs.add(prev_epoch)


if __name__ == "__main__":
    print("=== Ethereum Gasper Consensus Engine Simulation ===")
    validators = {
        "val_1": 32.0,
        "val_2": 32.0,
        "val_3": 32.0,
        "val_4": 32.0,
        "val_5": 32.0,
    }
    sim = GasperConsensusSimulator(validators)
    print(f"[+] Total Active Stake: {sim.total_stake} ETH | 2/3 Threshold: {sim.supermajority_threshold:.2f} ETH")

    # Slot 1 to 3: Fork scenario
    # Genesis -> Block A -> Block A1
    #         -> Block B
    sim.add_block("block_A", "genesis", slot=1, epoch=0)
    sim.add_block("block_B", "genesis", slot=1, epoch=0)
    sim.add_block("block_A1", "block_A", slot=2, epoch=0)

    # 4 out of 5 validators vote for Block A branch, 1 votes for Block B
    sim.vote("val_1", "block_A1")
    sim.vote("val_2", "block_A1")
    sim.vote("val_3", "block_A1")
    sim.vote("val_4", "block_A1")
    sim.vote("val_5", "block_B")

    head = sim.get_head()
    print(f"[+] LMD-GHOST Fork-Choice Head: '{head}'")
    assert head == "block_A1", f"Expected block_A1, got {head}"

    # Epoch 1 transition (Slot 32)
    sim.add_block("checkpoint_ep1", "block_A1", slot=32, epoch=1)
    sim.cast_checkpoint_attestations(target_epoch=1, voter_stakes=[32.0, 32.0, 32.0, 32.0])  # 128 ETH >= 106.67 ETH
    print(f"[+] Epoch 1 Checkpoint Justified: {1 in sim.justified_epochs}")
    assert 1 in sim.justified_epochs

    # Epoch 2 transition (Slot 64)
    sim.add_block("checkpoint_ep2", "checkpoint_ep1", slot=64, epoch=2)
    sim.cast_checkpoint_attestations(target_epoch=2, voter_stakes=[32.0, 32.0, 32.0, 32.0])
    print(f"[+] Epoch 2 Checkpoint Justified: {2 in sim.justified_epochs}")
    print(f"[+] Epoch 1 Checkpoint Finalized: {1 in sim.finalized_epochs}")
    assert 1 in sim.finalized_epochs, "Epoch 1 failed to reach FFG finalization!"

    print("[SUCCESS] LMD-GHOST head selection and Casper FFG finalization verified.")
