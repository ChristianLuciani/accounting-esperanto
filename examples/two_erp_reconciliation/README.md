# Two-ERP transnational reconciliation (ERPNext + Odoo → Kontablo)

This walkthrough reconciles a transnational group whose two subsidiaries keep
their books in two **different real open-source ERPs**, on two **different
national charts of accounts**, in two **different currencies** — and produces one
consolidated, intercompany-eliminated, cross-border trial balance in USD.

| Role | Company | Jurisdiction / chart | Currency | ERP |
|---|---|---|---|---|
| Parent | Ibérica Manufactura, S.A. | Spain — PGC | EUR | **ERPNext** |
| Subsidiary (100%) | Manufactura del Norte, S.A. de C.V. | Mexico — SAT | MXN | **Odoo** |

There is one intercompany balance: the parent carries a receivable from the
subsidiary; the subsidiary carries the matching payable to the parent. On
consolidation Kontablo eliminates the pair.

## How do I run it without Docker?

The default `fixtures` source runs the entire pipeline against committed
trial-balance exports — deterministic, offline, and identical to the live run:

```bash
python run_reconciliation.py            # equivalent to --source fixtures
```

Expected tail:

```
  Σ DEBITS    2,585,200.00   Σ CREDITS   2,585,200.00   diff       0.00
  Intercompany eliminations applied: 1
  Reconciliation: BALANCED ✓
```

This is what `tests/examples/test_two_erp_reconciliation.py` asserts, and it is
verified to match the self-contained Tier-1 example line for line.

## How do I run it against the real ERPs?

> Requires Docker. This live path is **not** exercised in CI (there is no
> ERPNext/Odoo in CI); the deterministic engine it feeds is covered by tests.

### 1. Bring the ERPs up

```bash
docker compose up -d
# ERPNext → http://localhost:8080   Odoo → http://localhost:8069
```

Initialise each ERP the first time (create an ERPNext site; create the Odoo
`norte` database from the Odoo UI). Then create an ERPNext API key/secret under
*Settings → API Access*.

### 2. Seed the demo group

```bash
# Mexico subsidiary in Odoo
ODOO_URL=http://localhost:8069 ODOO_DB=norte ODOO_USER=admin ODOO_PASSWORD=admin \
  python seed/seed_odoo.py

# Spain parent in ERPNext
ERPNEXT_URL=http://localhost:8080 \
ERPNEXT_API_KEY=xxxx ERPNEXT_API_SECRET=yyyy \
ERPNEXT_COMPANY="Ibérica Manufactura, S.A." \
  python seed/seed_erpnext.py
```

The seed scripts post the exact balances in `fixtures/`, so the live result
equals the fixtures result.

### 3. Run the reconciliation against live data

```bash
export ERPNEXT_URL=http://localhost:8080 ERPNEXT_API_KEY=xxxx ERPNEXT_API_SECRET=yyyy
export ERPNEXT_COMPANY="Ibérica Manufactura, S.A."
export ODOO_URL=http://localhost:8069 ODOO_DB=norte ODOO_USER=admin ODOO_PASSWORD=admin
python run_reconciliation.py --source live
```

## What is the pipeline, exactly?

1. **Pull** each subsidiary's trial balance from its ERP via the Apache-2.0
   connectors (ERPNext REST; Odoo XML-RPC).
2. **Resolve** every local account to a Kontablo UUID node — Tier-1 exact
   local-code lookup, Tier-2 multilingual keyword fallback. Deterministic; no LLM.
3. **Normalise** EUR and MXN to USD with the shared FX table.
4. **Consolidate** by summing each universal node across both subsidiaries.
5. **Eliminate** the intercompany receivable/payable pair (structured fields,
   not free text).
6. **Reconcile**: emit the unified trial balance and assert Σdebits = Σcredits.

Steps 2–6 are the *same* `core.engine` code path used by the self-contained
example and the gRPC server, so all three surfaces agree.

## Files

| File | Purpose |
|---|---|
| `run_reconciliation.py` | Driver (`--source fixtures|live`) |
| `docker-compose.yml` | ERPNext + Odoo + datastores |
| `fixtures/*.json` | Committed trial-balance exports (offline mode) |
| `seed/seed_odoo.py` | Create the Mexican subsidiary in Odoo |
| `seed/seed_erpnext.py` | Create the Spanish parent in ERPNext |

## Honesty

Amounts are synthetic trial balances (balanced by construction), **not** real
ledger data. Local PGC/SAT codes are real statutory codes from the Kontablo
ontology. The reconciliation is fully deterministic and reproducible.
