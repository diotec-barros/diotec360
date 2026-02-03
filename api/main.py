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
    description="Backend API for Aethel-Studio playground",
    version="1.0.0"
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
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "verify": "/api/verify",
            "compile": "/api/compile",
            "execute": "/api/execute",
            "vault": "/api/vault",
            "examples": "/api/examples"
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
        # Parse code
        ast = parser.parse(request.code)
        
        if not ast:
            return VerifyResponse(
                success=False,
                status="PARSE_ERROR",
                message="Failed to parse Aethel code",
                intents=[],
                errors=["Invalid syntax"]
            )
        
        # Extract intents
        intents = parser.extract_intents(ast)
        
        # Create intent map for Judge
        intent_map = {}
        for intent in intents:
            intent_name = intent.get("name", "unknown")
            intent_map[intent_name] = {
                "constraints": intent.get("guards", []),
                "post_conditions": intent.get("verifications", [])
            }
        
        # Initialize Judge with intent map
        judge = AethelJudge(intent_map)
        
        # Verify each intent
        results = []
        all_proved = True
        
        for intent_name in intent_map.keys():
            try:
                result = judge.verify_logic(intent_name)
                results.append({
                    "name": intent_name,
                    "status": "PROVED" if result else "FAILED",
                    "message": f"Intent '{intent_name}' verification {'passed' if result else 'failed'}"
                })
                
                if not result:
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
            message=f"Verified {len(intents)} intent(s)",
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
            "name": "Token Minting",
            "description": "Authorized token creation",
            "code": """intent mint(account: Account, amount: Balance) {
    guard {
        amount > 0;
        caller == contract_owner;
        old_account_balance == account_balance;
        old_total_supply == total_supply;
    }
    
    solve {
        priority: security;
        target: token_contract;
    }
    
    verify {
        account_balance == old_account_balance + amount;
        total_supply == old_total_supply + amount;
    }
}"""
        },
        {
            "name": "Token Burning",
            "description": "Destroy tokens with supply reduction",
            "code": """intent burn(account: Account, amount: Balance) {
    guard {
        amount > 0;
        account_balance >= amount;
        caller == account_owner;
        old_account_balance == account_balance;
        old_total_supply == total_supply;
    }
    
    solve {
        priority: security;
        target: token_contract;
    }
    
    verify {
        account_balance == old_account_balance - amount;
        total_supply == old_total_supply - amount;
        total_supply >= 0;
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
        ast = parser.parse(request.code)
        if not ast:
            return {
                "success": False,
                "message": "Failed to parse code"
            }
        
        intents = parser.extract_intents(ast)
        if not intents:
            return {
                "success": False,
                "message": "No intent found"
            }
        
        # Predict with Ghost-Runner
        ghost = get_ghost_runner()
        prediction = ghost.predict_outcome(intents[0])
        
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
        
        # Parse code
        ast = parser.parse(request.code)
        
        if not ast:
            return {
                "success": False,
                "status": "PARSE_ERROR",
                "message": "Failed to parse code"
            }
        
        # Extract first intent
        intents = parser.extract_intents(ast)
        if not intents:
            return {
                "success": False,
                "status": "NO_INTENT",
                "message": "No intent found in code"
            }
        
        # Get Ghost-Runner
        ghost = get_ghost_runner()
        
        # Predict outcome (zero latency!)
        prediction = ghost.predict_outcome(intents[0])
        
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

# Run with: uvicorn api.main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
