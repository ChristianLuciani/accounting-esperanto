from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from typing import List, Optional
from .models.kontablo import (
    KontabloAccount, SingleMappingRequest, SingleMappingResponse,
    BatchMappingRequest, BatchMappingResponse,
    TransactionClassificationRequest, ConsolidationRequest
)
from .services.mapping import MappingService
from .services.ontology import OntologyService
from .services.ai import AIService
from .services.consolidation import ConsolidationService

# Paths for data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ONTOLOGY_PATH = os.path.join(BASE_DIR, "core/schemas/level3_accounts.yaml")
STANDARDS_DIR = os.path.join(BASE_DIR, "research/standards")

# Initialize services
ontology_service = OntologyService(ONTOLOGY_PATH)
ai_service = AIService()
mapping_service = MappingService(STANDARDS_DIR, ontology_service, ai_service)
consolidation_service = ConsolidationService(mapping_service, ontology_service)

app = FastAPI(
    title="Kontablo Universal Accounting API",
    description="Universal accounting account mapping, transaction classification, and consolidation.",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "project": "Kontablo",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

# ─────────────────────────────────────────────
# ACCOUNTS — ONTOLOGY QUERIES
# ─────────────────────────────────────────────

@app.get("/accounts", response_model=dict, tags=["accounts"])
async def list_accounts(
    level: Optional[int] = Query(None, ge=1, le=3),
    nature: Optional[str] = None,
    statement: Optional[str] = None
):
    accounts = ontology_service.list_accounts(level, nature, statement)
    return {
        "total": len(accounts),
        "accounts": accounts
    }

@app.get("/accounts/{account_id}", response_model=KontabloAccount, tags=["accounts"])
async def get_account(account_id: str):
    account = ontology_service.get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

# ─────────────────────────────────────────────
# MAPPING
# ─────────────────────────────────────────────

@app.post("/mapping/account", response_model=SingleMappingResponse, tags=["mapping"])
async def map_account(request: SingleMappingRequest):
    return mapping_service.map_account(request)

@app.post("/mapping/batch", response_model=BatchMappingResponse, tags=["mapping"])
async def map_batch(request: BatchMappingRequest):
    results = [mapping_service.map_account(acc) for acc in request.accounts]
    mapped_count = sum(1 for r in results if r.match_method != "not_found")
    
    return BatchMappingResponse(
        company_id=request.company_id,
        jurisdiction=request.jurisdiction,
        total_accounts=len(request.accounts),
        mapped_count=mapped_count,
        unmapped_count=len(request.accounts) - mapped_count,
        coverage_pct=mapped_count / len(request.accounts) if request.accounts else 0,
        mappings=results
    )

@app.post("/classification/transaction", tags=["classification"])
async def classify_transaction(request: TransactionClassificationRequest):
    ontology_summary = mapping_service._get_ontology_summary()
    return await ai_service.classify_transaction(request.narration, request.jurisdiction, ontology_summary)

@app.post("/consolidation", tags=["reporting"])
async def consolidate_balances(request: ConsolidationRequest):
    return await consolidation_service.consolidate(request.trial_balances, request.target_currency)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
