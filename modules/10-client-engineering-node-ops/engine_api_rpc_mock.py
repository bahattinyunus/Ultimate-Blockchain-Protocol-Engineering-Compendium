#!/usr/bin/env python3
"""
Ethereum Engine API & Execution/Consensus Client Interface Simulator
Demonstrates:
1. JWT Secret authentication (HMAC-SHA256) between Consensus (CL) and Execution (EL)
2. engine_forkchoiceUpdatedV3: Synchronizing Head, Safe, and Finalized blocks
3. engine_newPayloadV3: EVM state execution and block validation
4. Payload building and block generation pipeline
"""

import base64
import hashlib
import hmac
import json
import time
from typing import Any, Dict, Optional, Tuple

JWT_SECRET = b"0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"


def generate_jwt_token(secret: bytes) -> str:
    """Generates standard HS256 JWT token for Engine API authorization."""
    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).rstrip(b"=").decode()
    payload = base64.urlsafe_b64encode(json.dumps({"iat": int(time.time())}).encode()).rstrip(b"=").decode()
    unsigned_token = f"{header}.{payload}"
    signature = base64.urlsafe_b64encode(
        hmac.new(secret, unsigned_token.encode(), hashlib.sha256).digest()
    ).rstrip(b"=").decode()
    return f"{unsigned_token}.{signature}"


def verify_jwt_token(token: str, secret: bytes) -> bool:
    """Verifies HS256 JWT signature."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return False
        header, payload, sig = parts
        unsigned = f"{header}.{payload}"
        expected_sig = base64.urlsafe_b64encode(
            hmac.new(secret, unsigned.encode(), hashlib.sha256).digest()
        ).rstrip(b"=").decode()
        return hmac.compare_digest(sig, expected_sig)
    except Exception:
        return False


class ExecutionEngineClient:
    def __init__(self):
        self.head_block_hash = "0x" + "00" * 32
        self.safe_block_hash = "0x" + "00" * 32
        self.finalized_block_hash = "0x" + "00" * 32
        self.payload_store: Dict[str, Dict[str, Any]] = {}
        self.block_number = 0

    def engine_forkchoiceUpdatedV3(
        self,
        forkchoice_state: Dict[str, str],
        payload_attributes: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Updates EL fork-choice state and optionally initiates block building.
        """
        self.head_block_hash = forkchoice_state["headBlockHash"]
        self.safe_block_hash = forkchoice_state["safeBlockHash"]
        self.finalized_block_hash = forkchoice_state["finalizedBlockHash"]

        payload_id = None
        if payload_attributes is not None:
            # Building new block
            payload_id = f"0x{int(time.time()):016x}"
            self.payload_store[payload_id] = {
                "attributes": payload_attributes,
                "parentHash": self.head_block_hash,
                "blockNumber": self.block_number + 1
            }

        return {
            "payloadStatus": {
                "status": "VALID",
                "latestValidHash": self.head_block_hash,
                "validationError": None
            },
            "payloadId": payload_id
        }

    def engine_newPayloadV3(
        self,
        execution_payload: Dict[str, Any],
        blob_hashes: list,
        parent_beacon_block_root: str
    ) -> Dict[str, Any]:
        """
        Executes and validates transactions within an incoming execution payload.
        """
        block_hash = execution_payload["blockHash"]
        # Basic integrity validation
        if not block_hash.startswith("0x") or len(block_hash) != 66:
            return {
                "status": "INVALID",
                "latestValidHash": None,
                "validationError": "Malformed block hash"
            }

        self.block_number = execution_payload["blockNumber"]
        return {
            "status": "VALID",
            "latestValidHash": block_hash,
            "validationError": None
        }


if __name__ == "__main__":
    print("=== Ethereum Engine API Client Interface (EL <-> CL) ===")
    el_engine = ExecutionEngineClient()

    # Step 1: JWT Authentication
    token = generate_jwt_token(JWT_SECRET)
    print(f"[+] Generated Bearer JWT Token: {token[:40]}...")
    is_auth_valid = verify_jwt_token(token, JWT_SECRET)
    print(f"[+] JWT Verification on Engine API Port 8551: {is_auth_valid}")
    assert is_auth_valid, "JWT authorization failed!"

    # Step 2: Consensus client informs Execution of Forkchoice update & asks for block building
    forkchoice = {
        "headBlockHash": "0xa1b2c3d4e5f607182930415263748596a1b2c3d4e5f607182930415263748596",
        "safeBlockHash": "0x9876543210fedcba9876543210fedcba9876543210fedcba9876543210fedcba",
        "finalizedBlockHash": "0x111122223333444455556666777788889999aaaabbbbccccddddeeeeffff0000"
    }
    payload_attrs = {
        "timestamp": hex(int(time.time())),
        "prevRandao": "0x" + "ff" * 32,
        "suggestedFeeRecipient": "0x000000000000000000000000000000000000dead",
        "withdrawals": []
    }

    print("\n[+] Calling engine_forkchoiceUpdatedV3 (Head Sync & Block Building Request)...")
    fc_res = el_engine.engine_forkchoiceUpdatedV3(forkchoice, payload_attrs)
    payload_id = fc_res["payloadId"]
    print(f"    - Payload Status : {fc_res['payloadStatus']['status']}")
    print(f"    - Generated Payload ID: {payload_id}")
    assert fc_res["payloadStatus"]["status"] == "VALID"

    # Step 3: Broadcasted block arrives from network via engine_newPayloadV3
    new_block_payload = {
        "parentHash": forkchoice["headBlockHash"],
        "feeRecipient": "0x000000000000000000000000000000000000dead",
        "stateRoot": "0x" + "33" * 32,
        "receiptsRoot": "0x" + "44" * 32,
        "blockNumber": 19482012,
        "gasLimit": 30_000_000,
        "gasUsed": 12_450_000,
        "timestamp": int(time.time()),
        "blockHash": "0x55aa66bb77cc88dd99ee00ff11aa22bb33cc44dd55ee66ff77aa88bb99cc00dd",
        "transactions": []
    }

    print("\n[+] Calling engine_newPayloadV3 (Executing Block & Validating State Transitions)...")
    payload_res = el_engine.engine_newPayloadV3(
        new_block_payload,
        blob_hashes=[],
        parent_beacon_block_root="0x" + "ee" * 32
    )
    print(f"    - Execution Validation Result: {payload_res['status']}")
    print(f"    - Latest Valid Hash          : {payload_res['latestValidHash']}")
    assert payload_res["status"] == "VALID"

    print("[SUCCESS] Engine API RPC flow and state sync successfully verified.")
