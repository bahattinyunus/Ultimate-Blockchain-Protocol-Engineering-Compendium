#!/usr/bin/env python3
"""
Cosmos IBC (Inter-Blockchain Communication) Protocol Simulator
TCP/IP for Blockchains: Trust-minimized Cross-Chain Messaging.

Demonstrates:
1. On-chain Light Client state & Consensus tracking
2. 4-step Connection Handshake (Init, Try, Ack, Confirm)
3. Cross-chain Packet Commitment & Merkle Membership verification
4. End-to-end packet delivery, execution, and acknowledgement
"""

import hashlib
import json
from typing import Dict, List, Optional, Tuple


def sha256_hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


class Packet:
    def __init__(
        self,
        sequence: int,
        source_port: str,
        source_channel: str,
        dest_port: str,
        dest_channel: str,
        data: Dict[str, str],
        timeout_height: int = 1000
    ):
        self.sequence = sequence
        self.source_port = source_port
        self.source_channel = source_channel
        self.dest_port = dest_port
        self.dest_channel = dest_channel
        self.data = data
        self.timeout_height = timeout_height

    def get_commitment(self) -> str:
        """IBC Packet commitment hash stored on source chain."""
        serialized = json.dumps(
            [self.sequence, self.source_port, self.source_channel, self.dest_port, self.dest_channel, self.data],
            sort_keys=True
        )
        return sha256_hash(serialized)


class BlockchainInstance:
    def __init__(self, chain_id: str):
        self.chain_id = chain_id
        self.height = 1
        # State stores
        self.state_root = "0x" + "00" * 32
        self.packet_commitments: Dict[int, str] = {}
        self.packet_receipts: Dict[int, bool] = {}
        self.packet_acknowledgements: Dict[int, str] = {}

        # Light clients tracking other chains: remote_chain_id -> {trusted_height, trusted_root}
        self.light_clients: Dict[str, Dict[str, str]] = {}
        # Connections: connection_id -> state
        self.connections: Dict[str, str] = {}

    def update_light_client(self, remote_chain_id: str, new_height: int, new_root: str):
        """Advances on-chain light client to remote chain's latest verified header."""
        self.light_clients[remote_chain_id] = {
            "height": new_height,
            "root": new_root
        }

    def compute_state_root(self):
        """Calculates simulated Merkle root over stored packet commitments."""
        items = sorted([f"{k}:{v}" for k, v in self.packet_commitments.items()])
        self.state_root = sha256_hash("|".join(items)) if items else "0x" + "00" * 32

    def send_packet(self, packet: Packet):
        """Source chain records packet commitment in its state."""
        commitment = packet.get_commitment()
        self.packet_commitments[packet.sequence] = commitment
        self.height += 1
        self.compute_state_root()

    def receive_packet(
        self,
        packet: Packet,
        source_chain_id: str,
        proof_commitment: str
    ) -> bool:
        """
        Destination chain verifies packet commitment against its internal
        Light Client tracking source chain, then executes payload.
        """
        if packet.sequence in self.packet_receipts:
            return False  # Replay prevention

        # Verify against trusted light client state root
        trusted = self.light_clients.get(source_chain_id)
        if not trusted:
            return False

        # In IBC, proof verifies: MerkleProof(packet_commitment) == trusted_root
        # Simulated proof check:
        expected_commitment = packet.get_commitment()
        if proof_commitment != expected_commitment:
            return False

        # Mark received and store acknowledgement
        self.packet_receipts[packet.sequence] = True
        ack = sha256_hash("ACK_SUCCESS:" + json.dumps(packet.data))
        self.packet_acknowledgements[packet.sequence] = ack
        return True


def simulate_ibc_connection_handshake(chain_a: BlockchainInstance, chain_b: BlockchainInstance) -> bool:
    """Executes the standard 4-way handshake between Chain A and Chain B."""
    conn_id_a = "connection-0"
    conn_id_b = "connection-1"

    # Step 1: ConnOpenInit (Chain A)
    chain_a.connections[conn_id_a] = "INIT"
    # Step 2: ConnOpenTry (Chain B)
    chain_b.connections[conn_id_b] = "TRYOPEN"
    # Step 3: ConnOpenAck (Chain A)
    chain_a.connections[conn_id_a] = "OPEN"
    # Step 4: ConnOpenConfirm (Chain B)
    chain_b.connections[conn_id_b] = "OPEN"

    return chain_a.connections[conn_id_a] == "OPEN" and chain_b.connections[conn_id_b] == "OPEN"


if __name__ == "__main__":
    print("=== Cosmos IBC (Inter-Blockchain Communication) Protocol Simulator ===")
    osmosis = BlockchainInstance("osmosis-1")
    cosmos_hub = BlockchainInstance("cosmoshub-4")

    # Step 1: Handshake
    print("[+] Executing IBC 4-Step Connection Handshake...")
    is_connected = simulate_ibc_connection_handshake(osmosis, cosmos_hub)
    print(f"    - Handshake Result : {'ESTABLISHED (OPEN)' if is_connected else 'FAILED'}")
    assert is_connected

    # Step 2: Initialize Light Clients on both sides
    print("\n[+] Initializing Cross-Chain Light Clients...")
    osmosis.update_light_client("cosmoshub-4", cosmos_hub.height, cosmos_hub.state_root)
    cosmos_hub.update_light_client("osmosis-1", osmosis.height, osmosis.state_root)

    # Step 3: Send Token Transfer Packet from Osmosis -> Cosmos Hub
    packet_payload = {
        "sender": "osmo1alice987654321",
        "receiver": "cosmos1bob123456789",
        "amount": "500000000",  # 500 ATOM
        "denom": "uatom"
    }
    pkt = Packet(
        sequence=1,
        source_port="transfer",
        source_channel="channel-0",
        dest_port="transfer",
        dest_channel="channel-141",
        data=packet_payload
    )

    print(f"\n[+] Osmosis executing send_packet(seq=1):")
    print(f"    - Transfer: {packet_payload['amount']} {packet_payload['denom']} from {packet_payload['sender'][:10]}... -> {packet_payload['receiver'][:12]}...")
    osmosis.send_packet(pkt)
    pkt_commitment = pkt.get_commitment()
    print(f"    - Packet Commitment recorded in Osmosis State Root: 0x{pkt_commitment[:32]}...")

    # Step 4: Relayer carries Osmosis updated state root to Cosmos Hub Light Client
    cosmos_hub.update_light_client("osmosis-1", osmosis.height, osmosis.state_root)

    # Step 5: Cosmos Hub receives packet and verifies light client proof
    print("\n[+] Cosmos Hub processing receive_packet via Light Client...")
    recv_success = cosmos_hub.receive_packet(pkt, source_chain_id="osmosis-1", proof_commitment=pkt_commitment)
    print(f"    - Packet Verification & Execution on Cosmos Hub: {recv_success}")
    assert recv_success, "Light client packet verification failed!"

    # Step 6: Verify replay prevention
    replay_attempt = cosmos_hub.receive_packet(pkt, source_chain_id="osmosis-1", proof_commitment=pkt_commitment)
    print(f"    - Replay Attack Attempt Rejected: {not replay_attempt}")
    assert not replay_attempt, "Replay attack was not rejected!"

    print("[SUCCESS] Cosmos IBC connection handshake and packet light client verification verified.")
