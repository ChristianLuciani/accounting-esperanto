# Kontablo developer entrypoints.
#
# Fast, no-Docker targets first; the heavy two-ERP e2e is opt-in.

PYTHON ?= venv/bin/python
COMPOSE ?= docker compose
E2E_COMPOSE := $(COMPOSE) -f e2e/docker-compose.yml

.PHONY: help test claims example e2e-example e2e e2e-up e2e-provision e2e-run e2e-down

help:
	@echo "Targets:"
	@echo "  make test          - run the fast pytest suite (no Docker)"
	@echo "  make claims        - reproduce the published validation numbers"
	@echo "  make e2e-example   - run the self-contained reconciliation example (no Docker)"
	@echo "  make e2e           - full two-ERP Docker e2e: up -> provision -> assert -> down"
	@echo "  make e2e-up        - start the two-ERP stack (ERPNext + Odoo + Kontablo API)"
	@echo "  make e2e-provision - provision both ERPs (real records, fixture amounts)"
	@echo "  make e2e-run       - run the live consolidation assertions"
	@echo "  make e2e-down      - tear the stack down and remove volumes"

# ---- fast, no-Docker ------------------------------------------------------- #
test:
	$(PYTHON) -m pytest tests/ -q

claims:
	$(PYTHON) scripts/mass_consolidation_v2.py

example e2e-example:
	$(PYTHON) examples/transnational_reconciliation.py

# ---- two-ERP Docker e2e (opt-in) ------------------------------------------ #
e2e-up:
	$(E2E_COMPOSE) up -d --build
	$(PYTHON) e2e/wait_for.py \
		http://localhost:8000/ \
		http://localhost:8069/web/database/selector \
		http://localhost:8081/api/method/ping \
		--timeout 900

e2e-provision:
	$(PYTHON) e2e/provision/provision_odoo.py
	$(PYTHON) e2e/provision/provision_erpnext.py

e2e-run:
	$(PYTHON) e2e/runner.py --mode live

e2e-down:
	$(E2E_COMPOSE) down -v

e2e: e2e-up e2e-provision e2e-run e2e-down
