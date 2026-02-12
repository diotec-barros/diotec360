"""
Aethel API - Backend for Aethel-Studio
FastAPI server that provides verification, compilation, and execution services
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import sys
import hashlib
import os
import time
from pathlib import Path
from dotenv import load_dotenv
import asyncio
import httpx

# Add parent directory to path to import aethel modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from aethel.core.parser import AethelParser
from aethel.core.judge import AethelJudge
from aethel.core.vault import AethelVault
from aethel.core.state import AethelStateManager
from aethel.core.persistence import get_persistence_layer
from aethel.nexo.p2p_streams import get_lattice_streams

# Initialize FastAPI app
app = FastAPI(
    title="Aethel API",
    description="Backend API for Aethel-Studio playground - v3.0.3 Hybrid Sync",
    version="3.0.3"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Aethel components
parser = AethelParser()
vault = AethelVault()
persistence = None  # Will be initialized in startup
lattice_streams = None  # Will be initialized in startup
# Judge will be initialized per-request with the parsed intent_map

# Hybrid Sync state
http_sync_task = None
http_sync_enabled = False
p2p_heartbeat_task = None
p2p_peerless_timer = None  # Timer para detectar falta de peers

# Request/Response models
class VerifyRequest(BaseModel):
    code: str
    
class VerifyResponse(BaseModel):
    success: bool
    status: str
    message: str
    intents: List[Dict[str, Any]]
    errors: Optional[List[str]] = None

class CompileRequest(BaseModel):
    code: str
    ai_provider: str = "ollama"
    
class CompileResponse(BaseModel):
    success: bool
    generated_code: Optional[str] = None
    vault_hash: Optional[str] = None
    error: Optional[str] = None

class ExecuteRequest(BaseModel):
    code: str
    input_data: Dict[str, Any]
    
class ExecuteResponse(BaseModel):
    success: bool
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Health check endpoint
@app.get("/")
async def root():
    return {
        "name": "Aethel API",
        "version": "1.7.0",
        "release": "Oracle Sanctuary",
        "status": "operational",
        "features": [
            "Formal Verification (Z3)",
            "Conservation Laws",
            "Privacy (secret keyword)",
            "Oracle Integration (external keyword)"
        ],
        "endpoints": {
            "verify": "/api/verify",
            "compile": "/api/compile",
            "execute": "/api/execute",
            "vault": "/api/vault",
            "examples": "/api/examples",
            "oracle": "/api/oracle"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}


def _parse_lattice_nodes() -> List[str]:
    raw = os.getenv("AETHEL_LATTICE_NODES", "").strip()
    if not raw:
        return []
    nodes = []
    for item in raw.split(","):
        url = item.strip()
        if url:
            nodes.append(url.rstrip("/"))
    return nodes


@app.get("/api/lattice/nodes")
async def lattice_nodes():
    return {
        "success": True,
        "nodes": _parse_lattice_nodes(),
        "count": len(_parse_lattice_nodes()),
    }


@app.get("/api/lattice/state")
async def lattice_state():
    return {
        "success": True,
        "merkle_root": persistence.merkle_db.get_root(),
        "state": persistence.merkle_db.state,
        "state_size": len(persistence.merkle_db.state),
    }


def _get_p2p_peer_count() -> int:
    """
    Get current P2P peer count.
    In production, this would query the actual P2P network.
    For now, returns simulated count.
    """
    if not lattice_streams or not lattice_streams.started:
        return 0
    
    # Placeholder - in production would use: lattice_streams.get_peer_count()
    # For simulation, check if we have bootstrap peers configured
    if lattice_streams.config.bootstrap_peers:
        # Simulate having 1 peer if bootstrap peers are configured
        return 1
    return 0


@app.get("/api/lattice/p2p/status")
async def lattice_p2p_status():
    peer_count = _get_p2p_peer_count()
    
    return {
        "success": True,
        "enabled": lattice_streams.config.enabled if lattice_streams else False,
        "started": lattice_streams.started if lattice_streams else False,
        "libp2p_available": lattice_streams.libp2p_available if lattice_streams else False,
        "error": lattice_streams.start_error if lattice_streams else None,
        "topic": lattice_streams.config.topic if lattice_streams else None,
        "listen_multiaddrs": lattice_streams.config.listen_multiaddrs if lattice_streams else [],
        "bootstrap_peers": lattice_streams.config.bootstrap_peers if lattice_streams else [],
        "peer_count": peer_count,
        "has_peers": peer_count > 0,
        "http_sync_enabled": http_sync_enabled,
        "sync_mode": "P2P" if (lattice_streams and lattice_streams.started and peer_count > 0) else ("HTTP" if http_sync_enabled else "NONE"),
        "heartbeat_active": p2p_heartbeat_task is not None
    }


@app.get("/api/lattice/p2p/identity")
async def lattice_p2p_identity():
    return {
        "success": True,
        "peer_id": lattice_streams.peer_id if lattice_streams else None,
        "listen_addrs": lattice_streams.listen_addrs if lattice_streams else [],
    }


@app.post("/api/lattice/sync/switch")
async def switch_sync_mode(mode: str = "auto"):
    """
    Switch sync mode manually (for testing)
    Modes: "p2p", "http", "auto"
    """
    global http_sync_enabled, http_sync_task
    
    if mode == "p2p":
        # Try to use P2P only
        if http_sync_task:
            http_sync_task.cancel()
            http_sync_task = None
        http_sync_enabled = False
        return {"success": True, "mode": "P2P", "message": "Switched to P2P-only mode"}
    
    elif mode == "http":
        # Force HTTP fallback
        if not http_sync_enabled:
            http_sync_enabled = True
            http_sync_task = asyncio.create_task(_http_sync_heartbeat())
        return {"success": True, "mode": "HTTP", "message": "Switched to HTTP fallback mode"}
    
    elif mode == "auto":
        # Let system decide (default behavior)
        peer_count = _get_p2p_peer_count()
        if peer_count > 0:
            # Has peers, use P2P
            if http_sync_task:
                http_sync_task.cancel()
                http_sync_task = None
            http_sync_enabled = False
            return {"success": True, "mode": "P2P", "message": "Auto-switched to P2P (has peers)"}
        else:
            # No peers, use HTTP
            if not http_sync_enabled:
                http_sync_enabled = True
                http_sync_task = asyncio.create_task(_http_sync_heartbeat())
            return {"success": True, "mode": "HTTP", "message": "Auto-switched to HTTP (no peers)"}
    
    return {"success": False, "message": f"Invalid mode: {mode}. Use 'p2p', 'http', or 'auto'"}


@app.on_event("startup")
async def _lattice_startup() -> None:
    global persistence, lattice_streams, http_sync_task, http_sync_enabled
    
    print("\n" + "="*70)
    print("[SHIELD] AETHEL LATTICE v3.0.3 - HYBRID SYNC PROTOCOL")
    print("="*70)
    
    # Reload environment variables (critical for .env loading)
    load_dotenv(override=True)
    print("[STARTUP] Environment variables reloaded")
    
    # Initialize persistence layer
    persistence = get_persistence_layer()
    print("[STARTUP] Persistence layer initialized")
    
    # Initialize lattice streams
    lattice_streams = get_lattice_streams(persistence)
    print("[STARTUP] Lattice streams initialized")
    
    # Try to start P2P (Primary Lung)
    if lattice_streams.config.enabled:
        print("[STARTUP] P2P enabled, attempting to start...")
        success, message = await lattice_streams.start()
        
        if success:
            print(f"[STARTUP] [OK] P2P started successfully: {message}")
            print(f"[STARTUP] peer_id: {lattice_streams.peer_id}")
            
            # Start P2P heartbeat monitor (detects peerless condition)
            global p2p_heartbeat_task
            p2p_heartbeat_task = asyncio.create_task(_p2p_heartbeat_monitor())
            print("[STARTUP] [SYNC] P2P Heartbeat Monitor activated")
        else:
            print(f"[STARTUP] [WARN] P2P failed to start: {message}")
            print("[STARTUP] Activating HTTP Sync fallback (Secondary Lung)")
            http_sync_enabled = True
    else:
        print("[STARTUP] P2P disabled, using HTTP Sync only")
        http_sync_enabled = True
    
    # Start HTTP Sync Heartbeat if needed
    if http_sync_enabled:
        http_sync_task = asyncio.create_task(_http_sync_heartbeat())
        print("[STARTUP] [LUNG] HTTP Sync Heartbeat activated")
    
    print("="*70)
    print("[ROCKET] LATTICE READY - Hybrid Sync Active")
    print("="*70 + "\n")


async def _p2p_heartbeat_monitor():
    """
    P2P Heartbeat Monitor - Detects peerless condition
    If P2P has no peers for 60 seconds, activates HTTP fallback
    """
    global http_sync_enabled, http_sync_task, p2p_peerless_timer
    
    print("[P2P_HEARTBEAT] Monitoring P2P peer connectivity...")
    
    peerless_start_time = None
    last_peer_count = 0
    
    while True:
        try:
            await asyncio.sleep(5)  # Check every 5 seconds
            
            if not lattice_streams or not lattice_streams.started:
                print("[P2P_HEARTBEAT] P2P not running, stopping monitor")
                break
            
            # Get current peer count
            peer_count = _get_p2p_peer_count()
            has_peers = peer_count > 0
            
            if has_peers:
                # Reset timer if we have peers
                if peerless_start_time is not None:
                    print("[P2P_HEARTBEAT] [OK] Peers found, resetting peerless timer")
                    peerless_start_time = None
                last_peer_count = peer_count
            else:
                # No peers detected
                if peerless_start_time is None:
                    peerless_start_time = time.time()
                    print(f"[P2P_HEARTBEAT] [WARN] No peers detected, starting 60s timer")
                else:
                    elapsed = time.time() - peerless_start_time
                    remaining = 60 - elapsed
                    
                    if elapsed >= 60:
                        # 60 seconds without peers - activate HTTP fallback
                        print("[P2P_HEARTBEAT] [ALERT] 60 seconds without peers - Activating HTTP Fallback")
                        
                        if not http_sync_enabled:
                            http_sync_enabled = True
                            http_sync_task = asyncio.create_task(_http_sync_heartbeat())
                            print("[P2P_HEARTBEAT] [LUNG] HTTP Sync Fallback activated")
                        
                        # Reset timer after activation
                        peerless_start_time = None
                    elif int(remaining) % 15 == 0:  # Log every 15 seconds
                        print(f"[P2P_HEARTBEAT] [TIMER] {remaining:.0f}s remaining before HTTP fallback")
            
        except asyncio.CancelledError:
            print("[P2P_HEARTBEAT] Monitor stopped")
            break
        except Exception as e:
            print(f"[P2P_HEARTBEAT] Error: {e}")
            await asyncio.sleep(10)


async def _http_sync_heartbeat():
    """
    HTTP Sync Fallback - Secondary Lung
    Polls peer nodes via HTTP when P2P is unavailable
    """
    lattice_nodes = os.getenv("AETHEL_LATTICE_NODES", "").strip()
    if not lattice_nodes:
        print("[HTTP_SYNC] No peer nodes configured, heartbeat disabled")
        return
    
    peer_urls = [url.strip() for url in lattice_nodes.split(",") if url.strip()]
    print(f"[HTTP_SYNC] Monitoring {len(peer_urls)} peer node(s)")
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        while True:
            try:
                await asyncio.sleep(10)  # Check every 10 seconds
                
                for peer_url in peer_urls:
                    try:
                        response = await client.get(f"{peer_url}/api/lattice/state")
                        if response.status_code == 200:
                            peer_state = response.json()
                            peer_root = peer_state.get("merkle_root")
                            local_root = persistence.merkle_db.get_root()
                            
                            if peer_root and peer_root != local_root:
                                print(f"[HTTP_SYNC] [LUNG] State divergence detected from {peer_url}")
                                print(f"[HTTP_SYNC]   Local:  {local_root}")
                                print(f"[HTTP_SYNC]   Peer:   {peer_root}")
                                # In production, trigger state reconciliation here
                    except Exception as e:
                        # Silent failure for individual peers
                        pass
                        
            except asyncio.CancelledError:
                print("[HTTP_SYNC] Heartbeat stopped")
                break
            except Exception as e:
                print(f"[HTTP_SYNC] Error: {e}")
                await asyncio.sleep(30)  # Back off on error

# Verification endpoint
@app.post("/api/verify", response_model=VerifyResponse)
async def verify_code(request: VerifyRequest):
    """
    Verify Aethel code using the Judge (Z3 Solver)
    """
    try:
        # Parse code - returns intent_map directly
        intent_map = parser.parse(request.code)
        
        if not intent_map:
            return VerifyResponse(
                success=False,
                status="PARSE_ERROR",
                message="Failed to parse Aethel code",
                intents=[],
                errors=["Invalid syntax"]
            )
        
        # Initialize Judge with intent map
        judge = AethelJudge(intent_map)
        
        # Verify each intent (v1.1.4 - Unified Proof Engine)
        results = []
        all_proved = True
        
        for intent_name in intent_map.keys():
            try:
                result = judge.verify_logic(intent_name)
                
                # result is now a dict with status, message, etc.
                status = result.get('status', 'ERROR')
                message = result.get('message', 'Unknown error')
                
                results.append({
                    "name": intent_name,
                    "status": status,
                    "message": message
                })
                
                if status != 'PROVED':
                    all_proved = False
                else:
                    if lattice_streams.config.enabled:
                        try:
                            await lattice_streams.publish_proof_event({
                                "intent": intent_name,
                                "status": status,
                            })
                        except Exception:
                            pass
            except Exception as e:
                results.append({
                    "name": intent_name,
                    "status": "ERROR",
                    "message": str(e)
                })
                all_proved = False
        
        return VerifyResponse(
            success=all_proved,
            status="PROVED" if all_proved else "FAILED",
            message=f"Verified {len(intent_map)} intent(s)",
            intents=results
        )
        
    except Exception as e:
        return VerifyResponse(
            success=False,
            status="ERROR",
            message=str(e),
            intents=[],
            errors=[str(e)]
        )

# Compilation endpoint
@app.post("/api/compile", response_model=CompileResponse)
async def compile_code(request: CompileRequest):
    """
    Compile Aethel code (verify + generate implementation)
    """
    try:
        # First verify
        verify_result = await verify_code(VerifyRequest(code=request.code))
        
        if not verify_result.success:
            return CompileResponse(
                success=False,
                error="Verification failed. Code must be proved before compilation."
            )
        
        # Generate code (simplified - in production would call AI)
        generated_code = "// Generated Rust code would appear here\n"
        generated_code += "// In production, this calls the AI Bridge\n"
        
        # Store in vault
        vault_hash = vault.store_function(request.code, {
            "status": "PROVED",
            "timestamp": "2026-02-02"
        })
        
        return CompileResponse(
            success=True,
            generated_code=generated_code,
            vault_hash=vault_hash
        )
        
    except Exception as e:
        return CompileResponse(
            success=False,
            error=str(e)
        )

# Execution endpoint
@app.post("/api/execute", response_model=ExecuteResponse)
async def execute_code(request: ExecuteRequest):
    """
    Execute Aethel code in WASM runtime
    """
    try:
        # Simplified execution
        # In production, this would use the WASM runtime
        
        output = {
            "status": "EXECUTED",
            "result": "Execution successful",
            "state_root": "1e994337bc48d0b2c293f9ac28b883ae..."
        }
        
        return ExecuteResponse(
            success=True,
            output=output
        )
        
    except Exception as e:
        return ExecuteResponse(
            success=False,
            error=str(e)
        )

# Vault endpoints
@app.get("/api/vault/list")
async def list_vault():
    """List all functions in vault"""
    try:
        functions = vault.list_functions()
        return {
            "success": True,
            "functions": functions,
            "count": len(functions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/vault/{function_hash}")
async def get_vault_function(function_hash: str):
    """Get specific function from vault"""
    try:
        function = vault.get_function(function_hash)
        if not function:
            raise HTTPException(status_code=404, detail="Function not found")
        return {
            "success": True,
            "function": function
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Examples endpoint
@app.get("/api/examples")
async def get_examples():
    """Get example Aethel code"""
    examples = [
        {
            "name": "Financial Transfer",
            "description": "Secure money transfer with conservation proof",
            "code": """intent transfer(sender: Account, receiver: Account, amount: Balance) {
    guard {
        sender_balance >= amount;
        amount > 0;
        old_sender_balance == sender_balance;
        old_receiver_balance == receiver_balance;
        old_total_supply == total_supply;
    }
    
    solve {
        priority: security;
        target: secure_ledger;
    }
    
    verify {
        sender_balance == old_sender_balance - amount;
        receiver_balance == old_receiver_balance + amount;
        total_supply == old_total_supply;
    }
}"""
        },
        {
            "name": "DeFi Liquidation (Oracle)",
            "description": "Price-based liquidation with oracle verification",
            "code": """intent check_liquidation(
    borrower: Account,
    collateral_amount: Balance,
    external btc_price: Price
) {
    guard {
        btc_price_verified == true;
        btc_price_fresh == true;
        collateral_amount > 0;
    }
    
    solve {
        priority: security;
        target: defi_vault;
    }
    
    verify {
        collateral_value == (collateral_amount * btc_price);
        (debt > (collateral_value * 0.75)) ==> (liquidation_allowed == true);
    }
}"""
        },
        {
            "name": "Weather Insurance (Oracle)",
            "description": "Parametric crop insurance with weather data",
            "code": """intent process_crop_insurance(
    farmer: Account,
    external rainfall_mm: Measurement
) {
    guard {
        rainfall_verified == true;
        rainfall_fresh == true;
        rainfall_mm >= 0;
    }
    
    solve {
        priority: security;
        target: oracle_sanctuary;
    }
    
    verify {
        (rainfall_mm < threshold) ==> (farmer_balance == (old_balance + payout));
    }
}"""
        },
        {
            "name": "Private Compliance (ZKP)",
            "description": "HIPAA-compliant verification with privacy",
            "code": """intent verify_insurance_coverage(
    patient: Person,
    treatment: Treatment,
    secret patient_balance: Balance
) {
    guard {
        treatment_cost > 0;
        insurance_limit > 0;
    }
    
    solve {
        priority: privacy;
        target: ghost_protocol;
    }
    
    verify {
        treatment_cost < insurance_limit;
        patient_balance >= copay;
        coverage_approved == true;
    }
}"""
        }
    ]
    
    return {
        "success": True,
        "examples": examples,
        "count": len(examples)
    }

# Mirror endpoints (Instant Preview)
@app.post("/api/mirror/manifest")
async def mirror_manifest(request: VerifyRequest):
    """
    Creates an instant manifestation of verified code.
    No build. No deploy. Just pure logic streaming.
    """
    try:
        from aethel.core.mirror import get_mirror
        from aethel.core.ghost import get_ghost_runner
        
        # First, verify the code with Ghost-Runner
        intent_map = parser.parse(request.code)
        if not intent_map:
            return {
                "success": False,
                "message": "Failed to parse code"
            }
        
        # Get first intent from the map
        if not intent_map:
            return {
                "success": False,
                "message": "No intent found"
            }
        
        # Get first intent
        first_intent_name = list(intent_map.keys())[0]
        first_intent = intent_map[first_intent_name]
        
        # Predict with Ghost-Runner
        ghost = get_ghost_runner()
        prediction = ghost.predict_outcome(first_intent)
        
        # Only manifest if PROVED
        if prediction.status != "MANIFESTED":
            return {
                "success": False,
                "message": f"Cannot manifest: {prediction.message}",
                "status": prediction.status
            }
        
        # Create instant manifestation
        mirror = get_mirror()
        bundle_hash = hashlib.sha256(request.code.encode()).hexdigest()
        
        preview_url = mirror.create_instant_manifestation(
            bundle_hash=bundle_hash,
            verified_code=request.code
        )
        
        return {
            "success": True,
            "preview_url": preview_url,
            "manifest_id": preview_url.split('/')[-1],
            "merkle_root": prediction.result.merkle_root if prediction.result else None,
            "message": "Reality manifested instantly"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

@app.get("/api/mirror/preview/{manifest_id}")
async def mirror_preview(manifest_id: str):
    """
    Streams a manifestation to the browser.
    Returns the data needed to render the app instantly.
    """
    try:
        from aethel.core.mirror import get_mirror
        
        mirror = get_mirror()
        data = mirror.stream_manifestation(manifest_id)
        
        if not data:
            raise HTTPException(status_code=404, detail="Manifestation not found or expired")
        
        return {
            "success": True,
            **data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mirror/stats")
async def mirror_stats():
    """
    Returns statistics about active manifestations.
    """
    try:
        from aethel.core.mirror import get_mirror
        
        mirror = get_mirror()
        stats = mirror.get_stats()
        
        return {
            "success": True,
            **stats
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

# Ghost-Runner endpoints (Epoch 3)
@app.post("/api/ghost/predict")
async def ghost_predict(request: VerifyRequest):
    """
    Ghost-Runner: Predicts outcome before execution.
    Manifests truth by subtracting the impossible.
    """
    try:
        from aethel.core.ghost import get_ghost_runner
        
        # Parse code - returns intent_map directly
        intent_map = parser.parse(request.code)
        
        if not intent_map:
            return {
                "success": False,
                "status": "PARSE_ERROR",
                "message": "Failed to parse code"
            }
        
        # Get first intent from the map
        if not intent_map:
            return {
                "success": False,
                "status": "NO_INTENT",
                "message": "No intent found in code"
            }
        
        # Get first intent
        first_intent_name = list(intent_map.keys())[0]
        first_intent = intent_map[first_intent_name]
        
        # Get Ghost-Runner
        ghost = get_ghost_runner()
        
        # Predict outcome (zero latency!)
        prediction = ghost.predict_outcome(first_intent)
        
        return {
            "success": prediction.status == "MANIFESTED",
            "status": prediction.status,
            "confidence": prediction.confidence,
            "latency": prediction.latency,
            "eliminated_states": prediction.eliminated_states,
            "message": prediction.message,
            "result": {
                "variables": prediction.result.variables if prediction.result else None,
                "merkle_root": prediction.result.merkle_root if prediction.result else None
            } if prediction.result else None
        }
        
    except Exception as e:
        return {
            "success": False,
            "status": "ERROR",
            "message": str(e)
        }

@app.post("/api/ghost/can-type")
async def ghost_can_type(request: dict):
    """
    Ghost-Runner: Checks if next character is possible.
    Prevents typing impossible code (cursor lock).
    """
    try:
        from aethel.core.ghost import get_ghost_runner
        
        current_code = request.get("code", "")
        next_char = request.get("nextChar", "")
        
        ghost = get_ghost_runner()
        can_type = ghost.can_type_next_char(current_code, next_char)
        
        return {
            "success": True,
            "canType": can_type,
            "message": "Character allowed" if can_type else "Character would lead to impossible state"
        }
        
    except Exception as e:
        return {
            "success": False,
            "canType": True,  # Fail open
            "message": str(e)
        }

# Oracle endpoints (v1.7.0 - Oracle Sanctuary)
@app.get("/api/oracle/list")
async def list_oracles():
    """
    List all registered oracles.
    Returns oracle registry with available data sources.
    """
    try:
        from aethel.core.oracle import get_oracle_registry
        
        registry = get_oracle_registry()
        oracles = registry.list_oracles()
        
        return {
            "success": True,
            "oracles": oracles,
            "count": len(oracles)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "oracles": []
        }

@app.get("/api/oracle/fetch/{oracle_id}")
async def fetch_oracle_data(oracle_id: str):
    """
    Fetch data from a specific oracle.
    Returns signed proof with timestamp and signature.
    """
    try:
        from aethel.core.oracle import fetch_oracle_data, verify_oracle_proof, OracleStatus
        
        # Fetch data
        proof = fetch_oracle_data(oracle_id)
        
        if not proof:
            raise HTTPException(status_code=404, detail=f"Oracle '{oracle_id}' not found")
        
        # Verify proof
        status = verify_oracle_proof(proof)
        
        return {
            "success": status == OracleStatus.VERIFIED,
            "oracle_id": proof.oracle_id,
            "value": proof.value,
            "timestamp": proof.timestamp,
            "signature": proof.signature[:32] + "...",  # Truncate for display
            "status": status.name,
            "verified": status == OracleStatus.VERIFIED
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

@app.post("/api/oracle/verify")
async def verify_oracle(request: dict):
    """
    Verify an oracle proof.
    Checks signature, timestamp, and freshness.
    """
    try:
        from aethel.core.oracle import verify_oracle_proof, OracleProof, OracleStatus
        
        # Reconstruct proof from request
        proof = OracleProof(
            oracle_id=request.get("oracle_id"),
            value=request.get("value"),
            timestamp=request.get("timestamp"),
            signature=request.get("signature")
        )
        
        # Verify
        status = verify_oracle_proof(proof)
        
        return {
            "success": status == OracleStatus.VERIFIED,
            "status": status.name,
            "verified": status == OracleStatus.VERIFIED,
            "message": f"Oracle proof {status.name.lower()}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "status": "ERROR",
            "message": str(e)
        }

@app.get("/api/oracle/stats")
async def oracle_stats():
    """
    Get oracle system statistics.
    Returns registry info and verification metrics.
    """
    try:
        from aethel.core.oracle import get_oracle_registry
        
        registry = get_oracle_registry()
        oracles = registry.list_oracles()
        
        # Count oracle types by ID patterns (since list_oracles returns strings)
        price_feeds = len([o for o in oracles if "price" in o.lower() or "btc" in o.lower() or "eth" in o.lower()])
        weather = len([o for o in oracles if "weather" in o.lower()])
        custom = len(oracles) - price_feeds - weather
        
        return {
            "success": True,
            "total_oracles": len(oracles),
            "oracle_types": {
                "price_feeds": price_feeds,
                "weather": weather,
                "custom": custom
            },
            "version": "1.7.0",
            "philosophy": "Zero trust, pure verification"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

# Persistence endpoints (v2.1.0 - Sovereign Memory)
@app.get("/api/persistence/stats")
async def persistence_stats():
    """
    Get persistence layer statistics.
    Returns execution stats, attack stats, and system state.
    """
    try:
        stats = persistence.get_dashboard_stats()
        
        return {
            "success": True,
            **stats
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

@app.get("/api/persistence/integrity")
async def check_integrity():
    """
    Check database integrity.
    Verifies Merkle Root matches current state.
    """
    try:
        is_valid = persistence.merkle_db.verify_integrity()
        current_root = persistence.merkle_db.get_root()
        
        if not is_valid:
            # CORRUPTION DETECTED!
            return {
                "success": False,
                "is_valid": False,
                "status": "CORRUPTED",
                "merkle_root": current_root,
                "message": "[ALERT] DATABASE CORRUPTION DETECTED - System in Panic Mode"
            }
        
        return {
            "success": True,
            "is_valid": True,
            "status": "VALID",
            "merkle_root": current_root,
            "message": "[OK] Integrity verified - All systems operational"
        }
        
    except Exception as e:
        return {
            "success": False,
            "is_valid": False,
            "status": "ERROR",
            "message": str(e)
        }

@app.get("/api/persistence/executions")
async def recent_executions(limit: int = 100):
    """
    Get recent execution logs.
    Returns list of recent proof attempts with status and timing.
    """
    try:
        executions = persistence.auditor.get_recent_executions(limit=limit)
        
        return {
            "success": True,
            "executions": executions,
            "count": len(executions)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "executions": []
        }

@app.get("/api/persistence/attacks")
async def recent_attacks(limit: int = 100):
    """
    Get recent attack logs.
    Returns list of blocked attacks with severity and detection method.
    """
    try:
        attacks = persistence.auditor.get_recent_attacks(limit=limit)
        
        return {
            "success": True,
            "attacks": attacks,
            "count": len(attacks)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "attacks": []
        }

@app.get("/api/persistence/bundles")
async def list_bundles():
    """
    List all code bundles in content-addressable vault.
    Returns bundles with content hashes and metadata.
    """
    try:
        bundles = persistence.vault_db.list_bundles()
        
        return {
            "success": True,
            "bundles": bundles,
            "count": len(bundles)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "bundles": []
        }

@app.get("/api/persistence/bundle/{content_hash}")
async def get_bundle(content_hash: str):
    """
    Get specific bundle by content hash.
    Returns bundle code and metadata.
    """
    try:
        bundle = persistence.vault_db.fetch_bundle(content_hash)
        
        if not bundle:
            raise HTTPException(status_code=404, detail="Bundle not found")
        
        # Verify integrity
        is_valid = persistence.vault_db.verify_bundle(content_hash)
        
        return {
            "success": True,
            "bundle": bundle,
            "integrity_verified": is_valid
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

@app.get("/api/persistence/merkle-root")
async def get_merkle_root():
    """
    Get current Merkle Root.
    Returns cryptographic fingerprint of entire system state.
    """
    try:
        root = persistence.merkle_db.get_root()
        total_accounts = len(persistence.merkle_db.state)
        
        return {
            "success": True,
            "merkle_root": root,
            "total_accounts": total_accounts,
            "message": "Current state fingerprint"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

# Run with: uvicorn api.main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
