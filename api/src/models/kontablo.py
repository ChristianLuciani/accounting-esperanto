from pydantic import BaseModel, Field, UUID4
from typing import List, Optional, Dict
from enum import Enum
from datetime import date
from uuid import UUID

class StatementType(str, Enum):
    balance_sheet = "balance_sheet"
    income_statement = "income_statement"
    cash_flow = "cash_flow"

class AccountNature(str, Enum):
    debit = "debit"
    credit = "credit"

class KontabloAccount(BaseModel):
    id: str = Field(..., description="Kontablo-style account ID, e.g., 'asset.current.receivables'")
    uuid: UUID4 = Field(..., description="Universal unique identifier for this account node")
    label_en: str = Field(..., description="Label in English")
    label_es: Optional[str] = Field(None, description="Label in Spanish")
    ifrs_tag: str = Field(..., description="IFRS Tag (Taxonomy 2024)")
    nature: AccountNature
    statement: StatementType
    level: int = Field(..., ge=1, le=3)
    parent: Optional[str] = None
    is_aggregate: bool
    optional: bool = False
    local_codes: Optional[Dict[str, str]] = None

class SingleMappingRequest(BaseModel):
    local_code: str
    local_name: str
    jurisdiction: str = Field(..., description="ISO 3166-1 alpha-2, e.g., 'mx'")
    nature: Optional[AccountNature] = None
    industry: Optional[str] = None

class BatchMappingRequest(BaseModel):
    company_id: str
    jurisdiction: str
    industry: Optional[str] = None
    accounts: List[SingleMappingRequest]

class SingleMappingResponse(BaseModel):
    local_code: str
    kontablo_id: str
    kontablo_uuid: UUID4
    label_en: str
    confidence_score: float = Field(..., ge=0, le=1)
    match_method: str = Field(..., description="Method used: exact_lookup, semantic_ai, fuzzy_string, not_found")
    justification: Optional[str] = None
    inconsistency_flag: bool = Field(False, description="True if a human-provided mapping contradicts a deterministic AI boundary")
    inconsistency_note: Optional[str] = Field(None, description="Detailed warning or explanation left by the AI/Human for audit trails")

class BatchMappingResponse(BaseModel):
    company_id: str
    jurisdiction: str
    total_accounts: int
    mapped_count: int
    unmapped_count: int
    coverage_pct: float
    mappings: List[SingleMappingResponse]

class TransactionClassificationRequest(BaseModel):
    narration: str
    jurisdiction: str
    amount: Optional[float] = None
    currency: Optional[str] = None
    debit_or_credit: Optional[AccountNature] = None
    context: Optional[dict] = None
    agent_id: Optional[str] = Field(None, description="Optional ID for M2M executed transactions under AP2/A2A protocols for liability auditing")

class TrialBalanceEntry(BaseModel):
    local_code: str
    local_name: Optional[str] = None
    debit: float
    credit: float

class TrialBalance(BaseModel):
    subsidiary_id: str
    jurisdiction: str
    currency: str
    reporting_date: date
    entries: List[TrialBalanceEntry]
    exchange_rate: Optional[float] = None  # Custom override for complex FX cases

class ConsolidationRequest(BaseModel):
    target_currency: str = "USD"
    trial_balances: List[TrialBalance]
