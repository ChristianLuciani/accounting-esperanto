from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import math
import uvicorn
import os
from typing import Any, List, Optional
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
    description=(
        "Universal, UUID-keyed accounting ontology over a deterministic engine. "
        "Map local statutory accounts to universal nodes, query the ontology, and "
        "consolidate multi-jurisdiction trial balances with auditable FX.\n\n"
        "**Deterministic vs. LLM:** account mapping, ontology queries, and "
        "consolidation are deterministic (graph lookup + rules + arithmetic). "
        "`/classification/transaction` is the one LLM-dependent endpoint and is "
        "stochastic by nature.\n\n"
        "**Input robustness:** monetary amounts must be finite (NaN/±Infinity "
        "rejected with 422); manual FX rates must be > 0 (422); a finite-sum "
        "overflow is reported as 400, never an opaque 500. The same invariants "
        "back the gRPC and MCP faces (`core.harness.validation`)."
    ),
    version="1.0.0",
)

# CORS configuration. Wildcard origins + credentials is an invalid combo
# (browsers reject it; Starlette silently drops the header), so credentials
# stay off; set KONTABLO_CORS_ORIGINS to a comma-separated allowlist to
# re-enable them behind explicit origins.
_cors_origins = [o.strip() for o in os.getenv("KONTABLO_CORS_ORIGINS", "*").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=_cors_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def _sanitize_non_finite(obj: Any) -> Any:
    """Replace NaN/±Infinity floats with their string form, recursively.

    FastAPI's 422 validation-error body echoes the offending input value; when
    that value is a non-finite float, Starlette's JSON renderer (allow_nan=False)
    raises on serialization and the clean 422 turns into an opaque 500. Scrubbing
    the error payload keeps a malformed-amount request a clean, explained 422."""
    if isinstance(obj, float) and not math.isfinite(obj):
        return repr(obj)  # "nan" / "inf" / "-inf"
    if isinstance(obj, dict):
        return {k: _sanitize_non_finite(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize_non_finite(v) for v in obj]
    return obj


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # jsonable_encoder first (turns the ValueError in each error's ctx into a
    # string), then scrub any non-finite input echo so the 422 serializes.
    detail = _sanitize_non_finite(jsonable_encoder(exc.errors()))
    return JSONResponse(status_code=422, content={"detail": detail})


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

@app.get("/accounts/{account_id}/local-codes", tags=["accounts"])
async def get_local_codes(account_id: str, jurisdiction: Optional[str] = None):
    """Return jurisdiction-specific local codes mapped to a Kontablo account ID."""
    account = ontology_service.get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    local_codes_map = getattr(account, "local_codes", {}) or {}
    if jurisdiction:
        code = local_codes_map.get(jurisdiction.lower())
        codes = [{"jurisdiction": jurisdiction.lower(), "code": code}] if code else []
    else:
        codes = [{"jurisdiction": jur, "code": code} for jur, code in local_codes_map.items()]
    return {"account_id": account_id, "local_codes": codes}

# ─────────────────────────────────────────────
# MAPPING
# ─────────────────────────────────────────────

@app.post("/mapping/account", response_model=SingleMappingResponse, tags=["mapping"],
          summary="Map one local account to a universal node",
          description="Resolve a single local statutory account (jurisdiction + code/name) "
          "to a universal Kontablo node via the deterministic resolver. Returns the node id, "
          "UUID, confidence, and match_method ('exact_lookup' | 'semantic_ai' | 'not_found').")
async def map_account(request: SingleMappingRequest):
    return await mapping_service.map_account(request)

@app.post("/mapping/batch", response_model=BatchMappingResponse, tags=["mapping"])
async def map_batch(request: BatchMappingRequest):
    results = [await mapping_service.map_account(acc) for acc in request.accounts]
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

@app.post("/classification/transaction", tags=["classification"],
          summary="Classify a transaction narration (LLM-dependent)",
          description="Classify a free-text narration to a Kontablo node. **Stochastic:** this "
          "is the one LLM-backed endpoint; unlike mapping/consolidation it is not deterministic "
          "and requires a configured provider key.")
async def classify_transaction(request: TransactionClassificationRequest):
    ontology_summary = mapping_service._get_ontology_summary()
    return await ai_service.classify_transaction(request.narration, request.jurisdiction, ontology_summary)

@app.post("/consolidation", tags=["reporting"],
          summary="Consolidate multi-jurisdiction trial balances",
          description="Consolidate subsidiary trial balances into one target-currency trial "
          "balance. Each subsidiary is resolved deterministically and converted with an "
          "auditable FX quote (manual `exchange_rate` > 0, else the runtime provider). The "
          "response reports per-node debit/credit/net, totals, `balanced`/`balance_difference`, "
          "and a per-entity `fx_audit`. Returns 400 for an unpriceable currency or a non-finite "
          "overflow; 422 for a non-finite amount or non-positive FX rate.")
async def consolidate_balances(request: ConsolidationRequest):
    try:
        return await consolidation_service.consolidate(request.trial_balances, request.target_currency)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
