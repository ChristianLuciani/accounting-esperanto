from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class AccountPayload(BaseModel):
    local_code: str = Field(..., description="The account code in the local ERP")
    local_name: str = Field(..., description="The account name in the local ERP")
    nature: Optional[str] = Field(None, description="Debit or Credit nature")

class MappingContext(BaseModel):
    country: str = Field(..., description="ISO 3166-1 alpha-2 country code")
    industry: Optional[str] = Field(None, description="Industry sector (retail, manufacturing, etc.)")
    currency: Optional[str] = Field(None, description="Local currency code")

class MappingRequest(BaseModel):
    company_id: str
    context: MappingContext
    accounts: List[AccountPayload]

class MappedAccount(BaseModel):
    local_code: str
    kontablo_uuid: str
    confidence_score: float
    agent_justification: str

class MappingResponse(BaseModel):
    status: str
    mapped_accounts: List[MappedAccount]
    unmapped_accounts: List[Dict] = []
