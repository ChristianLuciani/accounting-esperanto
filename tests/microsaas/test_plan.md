# Test Plan: SAT-Kontablo MicroSaaS AI Engine
**Version:** 1.0.0-draft
**Target:** Multi-Agent Mapping Pipeline

## 1. Overview
The SAT-Kontablo MicroSaaS must be validated against the 21 unique accounting environments researched. Before a single line of production code is written, these tests must be defined. The CI/CD pipeline will execute these tests by feeding mock payloads to the `/api/v1/map` endpoint.

## 2. Test Categories (TDD Scenarios)

### 2.1 Semantic Noise Translation (Multi-language Support)
**Objective:** Verify the Semantic Matcher Agent correctly identifies the same core concept across multiple languages and terminologies.
*   **Test Case 1 (Spanish-LatAm):** Payload contains `{"name": "Caja Fuerte", "country": "MX"}`. Expected UUID: `...0101` (Cash).
*   **Test Case 2 (English-UK):** Payload contains `{"name": "Trade Debtors", "country": "UK"}`. Expected UUID: `...0104` (Trade Receivables).
*   **Test Case 3 (Hebrew-IL):** Payload contains `{"name": "קופה", "country": "IL"}`. Expected UUID: `...0101` (Cash).
*   **Test Case 4 (Russian-RU):** Payload contains `{"name": "Налоги", "country": "RU"}`. Expected UUID: `...0203` (Taxes Payable).

### 2.2 Hyperinflation Resilience (Venezuela Case)
**Objective:** Validate that the Tax Compliance Agent intervenes when hyperinflationary indicators are present.
*   **Test Payload:** A Venezuelan chart containing accounts labeled "REMA" or "Ajuste por Inflación".
*   **Expected Result:** The agent must *not* map this to a standard Equity account or generic expense. It *must* enforce the NIC-29 compliant UUIDs defined in ADR 007 (`is_inflation_adjustment: true`).

### 2.3 Cascading Taxes & Multi-Slab Logic (Brazil / India)
**Objective:** Verify precision in handling complex tax codes without defaulting to generic VAT bins.
*   **Test Case 1 (Brazil SPED):** Payload contains `{"name": "COFINS a Recolher"}`. Expected UUID must be the Brazil-specific `30000000-0000-4000-8000-000000000001` (PIS/COFINS).
*   **Test Case 2 (India GST):** Payload contains `{"name": "Output IGST @ 18%"}`. Expected UUID must be the India-specific Multi-slab `40000000-0000-4000-8000-000000000001`.

### 2.4 Structural Rigidity & Codification (France / Germany)
**Objective:** Verify that the Router Agent respects mandatory numerical hierarchies (like the 8 Classes of France PCG).
*   **Test Case 1 (France PCG):** Payload contains `{"code": "411", "name": "Clients"}`. The agent must process the digit `4` as Class 4 (Comptes de tiers) and correctly map it to Trade Receivables (`...0104`).
*   **Test Case 2 (Germany SKR 04):** Payload contains `{"code": "1600", "name": "Kasse"}`. The agent must recognize the process-oriented 4-digit code and map it to Cash (`...0101`).

### 2.5 Null Hypothesis (Unknown Standard)
**Objective:** Validate graceful degradation when an unmapped country is provided (e.g., "Mali" or "Vietnam").
*   **Expected Result:** The Router Agent falls back to pure Semantic Matching using IFRS generic weights, but flags the response with a lower `confidence_score` (<0.7) and prompts for manual human review.
