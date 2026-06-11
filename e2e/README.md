# Kontablo two-ERP end-to-end harness

**What is this?** A Dockerized, production-grade counterpart to the
self-contained example at
[`examples/transnational_reconciliation.py`](../examples/transnational_reconciliation.py).
It stands up **two different free, open-source ERPs** — **ERPNext/Frappe** and
**Odoo** — provisions a transnational group (a Spanish parent on the PGC chart
in EUR + a Mexican subsidiary on the SAT chart in MXN, with one intra-group
transaction), pulls each chart of accounts and trial balance through the
Apache-2.0 connectors, runs the full Kontablo pipeline, and **asserts a correct
reconciled consolidation**: the consolidated trial balance balances and the
intercompany position nets to zero.

It is the canonical owner of the "two real ERPs end-to-end demo" deliverable.

## How does it stay consistent with the rest of the repo?

The consolidation + elimination math, the trial-balance fixtures, and the three
assertions live in **one place** —
[`examples/transnational_reconciliation.py`](../examples/transnational_reconciliation.py).
The self-contained example, the fast unit test
([`tests/test_example_reconciliation.py`](../tests/test_example_reconciliation.py)),
and this harness ([`runner.py`](runner.py)) all import the same
`reconcile()` / `assert_reconciled()` functions, and account→node resolution
reuses [`scripts/mass_consolidation_v2.resolve`](../scripts/mass_consolidation_v2.py)
verbatim. They cannot silently diverge. No LLM is involved in the asserted path
(CLAUDE.md principle #5: determinism over stochasticity).

## What is REAL vs FIXTURE? (honesty)

| Part | Real or fixture |
|---|---|
| ERPNext + Odoo servers, databases, companies, ledger accounts, journal entries | **Real** records, created via each ERP's public API |
| The connectors pulling chart + trial balance back out | **Real** API calls (ERPNext REST, Odoo XML-RPC) |
| The Kontablo `/api/v1/map` mapping call | **Real** call to the live API container |
| The transaction **amounts** and the MXN→EUR FX rate (0.05) | **Fixture** — a fixed synthetic scenario so the group is known and balanced |

> ⚠️ The MXN→EUR rate `0.05` is a fixed synthetic rate, not market data. The
> validation data is a constructed, balanced trial-balance pair — never describe
> it as real-world ledger data.

### Could this session run the live Docker stack?

The authoring environment had **no Docker daemon and could not pull the
multi-gigabyte ERPNext/Odoo images**, so the **live** path here was validated
*structurally* (it encodes the documented ERPNext REST + Odoo XML-RPC
contracts) and the **reconciliation math is proven end-to-end** by the
fixtures mode and the pytest suite, which run with no Docker. When you run
`make e2e` on a Docker host the live path executes for real. If provisioning
fails in your environment, the **Manual provisioning** section below gives the
exact commands — do not assume green without reading the runner's assertions.

## Port registry

The task referenced a host-level `PORT-REGISTRY.md` that does not exist in this
repository's environment. Ports chosen here, **never using 3000 (reserved,
FINEXOS)**:

| Service | Host port | Container |
|---|---|---|
| Kontablo API | **8000** | 8000 |
| ERPNext web | **8081** | 8080 |
| Odoo web | **8069** | 8069 |
| mariadb / postgres / redis | internal only | — |

If you maintain a central port registry, add these three entries there.

## Quick start

Requires Docker + Docker Compose v2 on the host.

```bash
# from the repo root
make e2e            # up → wait → provision both ERPs → run live assertions → down
```

or step by step:

```bash
cd e2e
cp .env.example .env

docker compose up -d --build
python wait_for.py http://localhost:8000/ \
                   http://localhost:8069/web/database/selector \
                   http://localhost:8081/api/method/ping --timeout 900

# provision the two ERPs (real records, fixture amounts)
python provision/provision_odoo.py
python provision/provision_erpnext.py     # auto-mints an API key from admin/admin

# run the full pipeline + assertions against the two live ERPs
python runner.py --mode live
```

### No Docker? Validate the logic offline

```bash
make e2e-example          # the self-contained example
python -m e2e.runner --mode fixtures   # the same runner, FIXTURE data, no ERPs
```

## Teardown

```bash
make e2e-down             # docker compose down -v  (removes volumes)
# or
cd e2e && docker compose down -v
```

## Manual provisioning (fallback)

If `erpnext_bootstrap.sh` cannot create the site automatically in your
environment, exec into the container and run bench directly:

```bash
docker compose exec erpnext bash
bench new-site kontablo.localhost --no-mariadb-socket \
  --admin-password admin --db-root-password admin --install-app erpnext
bench use kontablo.localhost && bench serve --port 8080
```

For Odoo, the database is created on first call by `provision_odoo.py`
(`db.create_database`). To do it from the UI instead, open
<http://localhost:8069/web/database/manager>, create database `kontablo` with
master password `admin` and admin password `admin`, then re-run
`python provision/provision_odoo.py`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `wait_for.py` times out on ERPNext | First boot creates the site + installs erpnext; it can take several minutes. Watch `docker compose logs -f erpnext`. Increase `--timeout`. |
| ERPNext provisioning 417/`PermissionError` | The Administrator password must match `.env` (`admin`). Re-mint the key or pass `--api-key/--api-secret`. |
| Odoo `Access Denied` / auth fails | Ensure the DB was created with admin password `admin` (matches `.env`). Recreate via the database manager. |
| Odoo `account.account` create fails on `account_type` | Odoo 17 enum values are used here (`asset_cash`, `liability_payable`, …). For other Odoo majors adjust `SAT_ACCOUNTS` in `provision/provision_odoo.py`. |
| Kontablo API container unhealthy | `docker compose logs kontablo-api`. A single unquoted ISO code in a localization YAML can 500 the mapping API (CLAUDE.md). |
| Runner assertion fails | The consolidated TB did not balance or intercompany did not net to zero — inspect the printed trial balances; usually a provisioning amount drifted from the fixture. |

## CI

The heavy live path is **opt-in** and never blocks the fast PR gate. See
[`.github/workflows/e2e.yml`](../.github/workflows/e2e.yml): it runs on manual
dispatch, on a nightly schedule, or when a PR carries the `e2e` label. The fast
gate ([`ci.yml`](../.github/workflows/ci.yml)) only runs the no-Docker unit
tests (which include the fixtures-mode reconciliation guards).
