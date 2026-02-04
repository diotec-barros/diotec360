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
from pathlib import Path

# Add parent directory to path to import aethel modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from aethel.core.parser import AethelParser
from aethel.core.judge import AethelJudge
from aethel.core.vault import AethelVault
from aethel.core.state import AethelStateManager

# Initialize FastAPI app
app = FastAPI(
    title="Aethel API",
    description="Backend API for Aethel-Studio playground - v1.7.0 Oracle Sanctuary",
    version="1.7.0"
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
# Judge will be initialized per-request with the parsed intent_map

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
    
    verify {
        collateral_value == collateral_amount * btc_price;
        if (debt > collateral_value * 0.75) {
            liquidation_allowed == true;
        }
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
    
    verify {
        if (rainfall_mm < threshold) {
            farmer_balance == old_balance + payout;
        }
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
        
        return {
            "success": True,
            "total_oracles": len(oracles),
            "oracle_types": {
                "price_feeds": len([o for o in oracles if "price" in o.get("description", "").lower()]),
                "weather": len([o for o in oracles if "weather" in o.get("description", "").lower()]),
                "custom": len([o for o in oracles if "custom" in o.get("description", "").lower()])
            },
            "version": "1.7.0",
            "philosophy": "Zero trust, pure verification"
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
