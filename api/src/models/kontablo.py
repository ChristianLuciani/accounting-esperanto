from pydantic import BaseModel, Field, UUID4, field_validator
from typing import List, Optional, Dict
from enum import Enum
from datetime import date
from uuid import UUID

from core.harness.validation import ensure_finite, ensure_positive_finite

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
    narration: str = Field(..., description="Free-text transaction narration to classify")
    jurisdiction: str = Field(..., description="ISO 3166-1 alpha-2, e.g. 'mx'")
    amount: Optional[float] = Field(None, description="Optional transaction amount (must be finite)")
    currency: Optional[str] = Field(None, description="Optional ISO 4217 currency, e.g. 'MXN'")
    debit_or_credit: Optional[AccountNature] = None
    context: Optional[dict] = None
    agent_id: Optional[str] = Field(None, description="Optional ID for M2M executed transactions under AP2/A2A protocols for liability auditing")

    @field_validator("amount")
    @classmethod
    def _finite_amount(cls, v: Optional[float]) -> Optional[float]:
        return None if v is None else ensure_finite(v, "amount")

class TrialBalanceEntry(BaseModel):
    local_code: str = Field(..., description="Local statutory account code as a string, e.g. '101'")
    local_name: Optional[str] = Field(None, description="Local account name, e.g. 'Caja'")
    debit: float = Field(..., description="Debit amount in the trial balance's currency (finite; negatives allowed)")
    credit: float = Field(..., description="Credit amount in the trial balance's currency (finite; negatives allowed)")

    @field_validator("debit", "credit")
    @classmethod
    def _finite_amount(cls, v: float, info) -> float:
        return ensure_finite(v, info.field_name)

class TrialBalance(BaseModel):
    subsidiary_id: str = Field(..., description="Stable subsidiary identifier")
    jurisdiction: str = Field(..., description="ISO 3166-1 alpha-2, e.g. 'mx'")
    currency: str = Field(..., description="ISO 4217 currency of this trial balance, e.g. 'MXN'")
    reporting_date: date = Field(..., description="Reporting date (ISO 8601)")
    entries: List[TrialBalanceEntry] = Field(..., description="Trial-balance rows in local currency")
    exchange_rate: Optional[float] = Field(
        None,
        description="Optional manual FX rate to the target currency (must be > 0). "
        "Overrides the runtime FX provider for asynchronous/contract-rate transactions.",
    )
    # Audit metadata for a manual exchange_rate (asynchronous transactions
    # priced at a contract/invoice rate): its effective date and the rationale.
    exchange_rate_as_of: Optional[str] = Field(
        None, description="Effective date of a manual exchange_rate, e.g. '2026-03-31'"
    )
    exchange_rate_note: Optional[str] = Field(
        None, description="Rationale for a manual exchange_rate, for the audit trail"
    )

    @field_validator("exchange_rate")
    @classmethod
    def _positive_finite_rate(cls, v: Optional[float]) -> Optional[float]:
        # A 0 rate zeroes every converted amount; a negative rate sign-flips
        # them — both corrupt the consolidation while looking legitimate.
        return None if v is None else ensure_positive_finite(v, "exchange_rate")

class ConsolidationRequest(BaseModel):
    target_currency: str = Field("USD", description="Reporting currency for the consolidated trial balance")
    trial_balances: List[TrialBalance] = Field(..., description="Subsidiary trial balances to consolidate")
