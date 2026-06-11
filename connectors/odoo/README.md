# Odoo ↔ Kontablo connector

Apache-2.0. Bridges [Odoo](https://www.odoo.com/) (open-source ERP) to the
Kontablo mapping/consolidation API. Per Kontablo's connector-licensing policy,
connectors to open-source ERPs are Apache-2.0 (open the interface to grow the
ecosystem); connectors to proprietary ERPs are licensed separately.

## What it does

`OdooKontabloConnector` (in `odoo_client.py`) authenticates to Odoo over XML-RPC
(stdlib `xmlrpc.client` — no third-party dependency), then:

- `get_chart_of_accounts()` — reads `account.account` (code, name, type).
- `get_trial_balance()` — aggregates posted `account.move.line` into per-account
  debit/credit totals, shaped as `{local_code, local_name, debit, credit}`.
- `sync_to_kontablo()` — POSTs the chart to Kontablo `/mapping/batch`.
- `consolidate_in_kontablo()` — POSTs the trial balance to `/consolidation`.

The payloads match the ERPNext connector's, so a single Kontablo engine
consolidates books from either ERP. No logic keys on free text; jurisdiction is
an explicit argument (CLAUDE.md principle #5).

## Tests

`tests/test_odoo_client.py` mocks Odoo XML-RPC and the Kontablo API:
trial-balance parsing, payload shaping, and auth-failure handling. No live Odoo
is required.

## See also

A full two-ERP reconciliation walkthrough (ERPNext + Odoo via Docker) lives in
[`examples/two_erp_reconciliation/`](../../examples/two_erp_reconciliation/).
