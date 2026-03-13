from fastapi import FastAPI, HTTPException
from api.rest.models import MappingRequest, MappingResponse, MappedAccount
from logic.knowledge_base import KnowledgeBase
from logic.agents.router_agent import RouterAgent
from logic.agents.semantic_matcher import SemanticMatcherAgent
from logic.agents.tax_compliance import TaxComplianceAgent
from logic.validators.integrity import IntegrityValidator
import uvicorn
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kontablo-mapping-api")

app = FastAPI(
    title="SAT-Kontablo Mapping MicroSaaS",
    description="AI-powered accounting standard mapping engine (Multi-Agent Architecture)",
    version="1.0.0"
)

# Initialize Components
try:
    kb = KnowledgeBase()
    router_agent = RouterAgent()
    semantic_matcher = SemanticMatcherAgent(kb)
    tax_compliance = TaxComplianceAgent()
    validator = IntegrityValidator()
    logger.info("✅ All agents and Knowledge Base initialized")
except Exception as e:
    logger.error(f"❌ Initialization failed: {e}")

@app.get("/")
async def root():
    return {
        "message": "Kontablo Mapping API is active", 
        "version": "1.0.0", 
        "status": "operational"
    }

@app.post("/api/v1/map", response_model=MappingResponse)
async def map_accounts(request: MappingRequest):
    """
    Full Multi-Agent Pipeline:
    1. Router Agent: Detect context.
    2. Semantic Matcher: Exact Knowledge Base + AI RAG-lite.
    3. Tax Compliance: Jurisdiction-specific overrides.
    4. Validator: Final integrity check.
    """
    logger.info(f"Processing batch of {len(request.accounts)} accounts for company {request.company_id}")
    
    try:
        # Step 1: Detect Routing & Country Context
        routing_info = router_agent.route(request)
        country = routing_info["country"]
        logger.info(f"Detected country: {country}")
        
        # Step 2: Semantic Matching
        mapped = semantic_matcher.match_batch(request.accounts, routing_info)
        
        # Step 3: Apply Jurisdictional Tax Compliance Overrides
        final_mapped = tax_compliance.process(mapped, country)
        
        # Step 4: Final Integrity Validation
        is_valid = validator.validate(final_mapped)
        
        unmapped = [m.model_dump() for m in final_mapped if m.confidence_score < 0.5]
        
        return MappingResponse(
            status="success" if is_valid else "warning",
            mapped_accounts=final_mapped,
            unmapped_accounts=unmapped
        )
    except Exception as e:
        logger.error(f"Mapping failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
