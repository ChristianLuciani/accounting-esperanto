# OpenSpec: AI Training Dataset Specification

**Change ID:** ai-training-dataset-spec  
**Status:** Proposal  
**Date:** January 27, 2026  
**Phase:** Phase 0 (Specification), Phase 2 (Implementation)

---

## 📋 Proposal: Structure for Training AI Transaction Classifiers

### Problem
- Phase 2 will need to fine-tune LLaMA 3 on transaction classification
- No dataset structure defined yet
- Blocks Phase 2 AI classifier development

### Solution
- **Phase 0:** Define dataset structure & format (THIS DOCUMENT)
- **Phase 1:** Could create sample dataset (optional)
- **Phase 2:** Implement full training pipeline
- **Phase 3:** Deploy fine-tuned model

### Current Scope: Phase 0 (Specification Only - No Data Yet)

---

## 🎯 Design: Transaction Classification Dataset

### Dataset Structure

```yaml
# ai-training/datasets/transactions_2026_Q1.yaml

dataset_metadata:
  dataset_id: "kontablo_transactions_2026_q1"
  version: "0.1.0"
  created_date: "2026-Q2"  # After Phase 1 research
  
  description: |
    Training dataset for LLaMA 3 fine-tuning on accounting transaction classification.
    Maps raw transaction descriptions → Kontablo Level 3 accounts.
  
  data_sources:
    - source: "Mexico SAT sample transactions"
      records: 300
      country: "mexico"
    - source: "Colombia PUC sample transactions"
      records: 250
      country: "colombia"
    - source: "Panama DGI sample transactions"
      records: 200
      country: "panama"
  
  total_records: 750
  train_test_split: "80/20"  # 600 train, 150 test
  
  task:
    input: "transaction_description (text)"
    output: "kontablo_account_uuid (classification)"
    example:
      input: "Pagué a Banco Santander $50,000 MXN para fondos de caja"
      output: "550e8400-e29b-41d4-a716-446655440000"  # 1.1.01: Cash
```

### Single Transaction Record Format

```yaml
transaction:
  transaction_id: "txn_mx_0001"
  
  # Input (what AI will read)
  description: "Depósito en Banco Santander CuentaCorreinte No. 12345"
  description_lang: "es_MX"
  date: "2026-01-15"
  amount: 50000.00
  currency: "MXN"
  
  # Context (helps AI understand)
  context:
    country: "mexico"
    department: "accounting"
    company_industry: "manufacturing"
    company_size: "mid-market"
    transaction_type: "cash_inflow"
  
  # Ground truth label (what the AI should learn)
  label:
    kontablo_account_uuid: "550e8400-e29b-41d4-a716-446655440000"
    kontablo_code: "1.1.01"
    kontablo_label_en: "Cash and Cash Equivalents"
    kontablo_label_es: "Efectivo y Equivalentes de Efectivo"
    confidence: 0.99  # Human is 99% sure
  
  # Metadata
  metadata:
    labeled_by: "eva"
    label_date: "2026-02-15"
    notes: "Clear cash deposit, no ambiguity"
    alternative_codes: []  # Could also map to other accounts
    
    # For difficult cases
    if_difficult: false
    difficulty_reason: null
```

### Complex Transaction Example (1:N Mapping)

```yaml
transaction:
  transaction_id: "txn_pa_0042"
  description: "Inventario recibido - Materiales $30K + Suministros $5K"
  
  # Single description → Multiple accounts
  labels:
    - kontablo_account_uuid: "1.1.06-uuid"
      kontablo_code: "1.1.06"
      label_en: "Inventories"
      amount: 30000
      confidence: 0.98
    
    - kontablo_account_uuid: "1.1.07-uuid"
      kontablo_code: "1.1.07"
      label_en: "Prepaid Expenses"
      amount: 5000
      confidence: 0.97
  
  metadata:
    labeled_by: "eva"
    notes: "Single transaction, two accounts (split based on item type)"
    instruction_for_ai: |
      Learn to split transactions when description contains multiple item types.
      "Materiales" (materials) → Inventory
      "Suministros" (supplies) → Prepaid Expenses
```

---

## 📊 Dataset Statistics (Target)

```yaml
dataset_statistics:
  
  # Size
  total_transactions: 750
  training_set: 600
  test_set: 150
  
  # Distribution by account type
  distribution_by_account:
    cash: 120  # 16%
    receivables: 95  # 13%
    inventory: 100  # 13%
    ppe: 80  # 11%
    ap: 105  # 14%
    debt: 75  # 10%
    equity: 60  # 8%
    revenue: 65  # 9%
    cogs: 40  # 5%
    opex: 10  # 1%
  
  # Distribution by country
  distribution_by_country:
    mexico: 300  # 40%
    colombia: 250  # 33%
    panama: 200  # 27%
  
  # Distribution by complexity
  simple_1_to_1: 600  # 80%: one description → one account
  complex_1_to_n: 100  # 13%: one description → multiple accounts
  ambiguous: 50   # 7%: could map to multiple accounts (human judgment needed)
  
  # Language distribution
  spanish: 750  # 100% (all Latin American samples in Spanish)
  english: 0    # 0% (translations will be generated)
  
  # Quality metrics
  labeling_agreement: 0.98  # 98% consistency when 2 people labeled same
  ambiguous_cases: 50      # Flagged for additional review
  needs_expert_review: 15  # Edge cases needing EVA approval
```

---

## 🔧 Data Collection Process (Phase 2)

### How transactions will be sourced

```yaml
data_collection_phase_2:
  
  step_1_source_raw_transactions:
    source: "Real company financial records (anonymized)"
    countries: [mexico, colombia, panama]
    time_period: "2025-2026"
    anonymization:
      - remove_company_names: true
      - remove_employee_names: true
      - remove_tax_ids: true
      - randomize_amounts: "scale by random factor"
  
  step_2_human_labeling:
    process: "Each transaction gets labeled by human"
    labelers: ["eva"]  # Could hire more
    instructions: |
      For each transaction:
      1. Read description (in Spanish)
      2. Identify account(s) from Kontablo Level 3 list
      3. Mark confidence (0-1.0)
      4. Note any ambiguities
    
    time_per_transaction: "2-3 minutes"
    total_labeling_time: "25-37 hours"
    
  step_3_qa_spot_check:
    process: "Randomly review 10% of labels"
    agreement_target: ">95%"
    if_disagreement: "Discuss and resolve with EVA"
  
  step_4_create_splits:
    training_80_percent: 600
    test_20_percent: 150
    stratify_by: [account_type, country, complexity]
    random_seed: 42  # Reproducible
  
  step_5_export_formats:
    formats:
      - json_lines: "ai-training/datasets/transactions.jsonl"
      - parquet: "ai-training/datasets/transactions.parquet"
      - huggingface_dataset: "huggingface_dataset_upload"
```

---

## 🤖 Model Training Process (Phase 2)

### How the dataset will be used

```yaml
fine_tuning_pipeline:
  
  model: "LLaMA 3.1-70B or similar"
  
  task: "Transaction classification"
  
  input_format:
    - "transaction_description: [TEXT]"
    - "country: [MX/CO/PA]"
    - "amount: [NUMBER]"
  
  output_format:
    - "predicted_uuid: [UUID]"
    - "confidence_score: [0.0-1.0]"
    - "alternative_suggestions: [LIST OF UUIDS]"
  
  training_config:
    optimizer: "AdamW"
    learning_rate: 5e-5
    batch_size: 16
    epochs: 3
    validation_split: 0.1
    early_stopping: "if val_loss not improving for 2 epochs"
  
  expected_performance:
    accuracy_top1: ">90%"
    accuracy_top3: ">95%"
    f1_score: ">0.88"
    per_country_accuracy:
      mexico: ">92%"
      colombia: ">88%"
      panama: ">85%"
  
  inference_latency:
    per_transaction: "<500ms"
    batch_100_transactions: "<30s"
    deployment: "API endpoint"
```

---

## 📋 Data Quality Checklist

```yaml
quality_assurance:
  
  before_training:
    - [ ] All 750 transactions labeled
    - [ ] No NULL/missing labels
    - [ ] 80/20 train/test split correct
    - [ ] Stratification correct (balanced by account)
    - [ ] 10% spot-check passed (>95% agreement)
    - [ ] Data export formats match spec
  
  during_training:
    - [ ] Training loss decreasing
    - [ ] Validation loss decreasing (not increasing)
    - [ ] No numerical instabilities
    - [ ] Batch processing working
  
  after_training:
    - [ ] Accuracy >90% on test set
    - [ ] Confusion matrix reviewed
    - [ ] Error analysis completed
    - [ ] Edge cases documented
    - [ ] Model saved with version tag
```

---

## 🔧 Implementation Tasks (Phase 0 - This Spec)

- [x] Define transaction record format
- [x] Document labeling process
- [x] Specify dataset statistics targets
- [x] Document training pipeline
- [x] Create data quality checklist

### Phase 2 Tasks

- [ ] Collect 750 real transactions (anonymized)
- [ ] Have EVA label all transactions
- [ ] QA spot-check (10%)
- [ ] Create train/test splits
- [ ] Export in JSON/Parquet/HuggingFace formats
- [ ] Fine-tune LLaMA 3

---

## ✅ Success Criteria (Phase 0)

- [x] Transaction record format designed
- [x] Dataset size targets defined (750 transactions)
- [x] Labeling process documented
- [x] Training pipeline outlined
- [x] Quality metrics specified
- [x] Roadmap for Phase 2 created

---

## 📅 Timeline

- **Week 1-4:** Phase 0 (this specification)
- **Week 5-8:** Phase 1 (collect real transaction samples)
- **Week 9-16:** Phase 2 (label dataset, train model)
- **Week 17+:** Phase 3 (deploy, monitor, iterate)

---

## 📦 Storage & Access

### During Phase 0-1 (Spec Only)

```
ai-training/
  ├── datasets/
  │   ├── README.md (this file)
  │   ├── schema.yaml (transaction format)
  │   └── (data will be added in Phase 2)
  ├── prompts/
  │   └── classification_prompt.txt
  └── models/
      └── (trained models will be stored in Phase 2)
```

### Phase 2+

```
ai-training/
  ├── datasets/
  │   ├── transactions.jsonl (750 records)
  │   ├── transactions.parquet
  │   ├── train_split_80.jsonl (600 records)
  │   ├── test_split_20.jsonl (150 records)
  │   └── labels_distribution.csv
  ├── models/
  │   ├── kontablo_classifier_v0.1/
  │   │   ├── model.safetensors
  │   │   ├── config.json
  │   │   └── training_log.csv
  │   └── metrics.json
  └── analysis/
      ├── confusion_matrix.png
      ├── error_analysis.md
      └── per_country_performance.csv
```

---

## 🚀 Future Enhancements (Phase 3+)

- Multi-label classification (1:N mappings)
- Confidence confidence thresholding
- Active learning (model suggests which transactions to label)
- Continuous retraining with new data
- Model monitoring & drift detection

