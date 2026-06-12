# Kontablo developer entrypoints.
#
# Thin convenience wrappers over existing repo entrypoints — no logic lives here.
# The two-ERP reconciliation demo itself lives in examples/two_erp_reconciliation/.

PYTHON ?= python
COMPOSE ?= docker compose
DEMO := examples/two_erp_reconciliation
DEMO_COMPOSE := $(COMPOSE) -f $(DEMO)/docker-compose.yml

.PHONY: help test claims reconcile reconcile-live e2e-up e2e-seed e2e-down

help:
	@echo "Targets:"
	@echo "  make test          - run the fast pytest suite (no Docker)"
	@echo "  make claims        - reproduce the published validation numbers"
	@echo "  make reconcile     - two-ERP reconciliation, fixtures source (no Docker)"
	@echo "  make e2e-up        - start the two-ERP stack (ERPNext + Odoo)"
	@echo "  make e2e-seed      - seed both ERPs (real records, synthetic amounts)"
	@echo "  make reconcile-live- two-ERP reconciliation against the live ERPs"
	@echo "  make e2e-down      - tear the stack down and remove volumes"

# ---- fast, no-Docker ------------------------------------------------------- #
test:
	$(PYTHON) -m pytest tests/ -q

claims:
	$(PYTHON) scripts/mass_consolidation_v2.py

reconcile:
	$(PYTHON) $(DEMO)/run_reconciliation.py --source fixtures

# ---- two-ERP Docker demo (opt-in; see examples/two_erp_reconciliation/README) #
e2e-up:
	$(DEMO_COMPOSE) up -d --build

# Seeding needs the ERPNext site + API keys to exist first; see the demo README.
# ERPNEXT_API_KEY / ERPNEXT_API_SECRET (and the ODOO_* vars) must be exported.
e2e-seed:
	$(PYTHON) $(DEMO)/seed/seed_odoo.py
	$(PYTHON) $(DEMO)/seed/seed_erpnext.py

reconcile-live:
	$(PYTHON) $(DEMO)/run_reconciliation.py --source live

e2e-down:
	$(DEMO_COMPOSE) down -v
