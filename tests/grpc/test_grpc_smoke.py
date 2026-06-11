"""Smoke test: start the real gRPC server and round-trip core RPCs.

Asserts (not print-only) that the deterministic gRPC surface actually works and
matches the engine that backs REST — so README/CLAUDE.md can claim gRPC parity
for the deterministic core honestly.
"""

import os
import sys

import pytest

grpc = pytest.importorskip("grpc", reason="grpcio not installed")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api.grpc.gen import kontablo_pb2 as pb  # noqa: E402
from api.grpc.gen import kontablo_pb2_grpc as pb_grpc  # noqa: E402
from api.grpc.server import build_server  # noqa: E402


@pytest.fixture(scope="module")
def channel():
    server = build_server(address="127.0.0.1:50077")
    server.start()
    ch = grpc.insecure_channel("127.0.0.1:50077")
    grpc.channel_ready_future(ch).result(timeout=5)
    yield ch
    ch.close()
    server.stop(grace=None)


def test_list_accounts(channel):
    stub = pb_grpc.AccountServiceStub(channel)
    resp = stub.ListAccounts(pb.ListAccountsRequest())
    assert resp.total > 0
    assert resp.total == len(resp.accounts)
    ids = {a.id for a in resp.accounts}
    assert "asset.current.receivables" in ids


def test_get_account_not_found(channel):
    stub = pb_grpc.AccountServiceStub(channel)
    with pytest.raises(grpc.RpcError) as exc:
        stub.GetAccount(pb.GetAccountRequest(account_id="does.not.exist"))
    assert exc.value.code() == grpc.StatusCode.NOT_FOUND


def test_map_account_tier1_exact(channel):
    stub = pb_grpc.MappingServiceStub(channel)
    # Spanish PGC 572 (Bancos) → cash; deterministic Tier-1 exact lookup.
    resp = stub.MapAccount(
        pb.MapAccountRequest(local_code="572", local_name="Bancos", jurisdiction="es")
    )
    assert resp.kontablo_id == "asset.current.cash"
    assert resp.match_method == pb.MATCH_EXACT_LOOKUP
    assert resp.confidence_score == 1.0
    assert resp.kontablo_uuid  # non-empty UUID round-tripped


def test_map_batch_streaming(channel):
    stub = pb_grpc.MappingServiceStub(channel)
    reqs = [
        pb.MapAccountRequest(local_code="105", local_name="Clientes", jurisdiction="mx"),
        pb.MapAccountRequest(local_code="201", local_name="Proveedores", jurisdiction="mx"),
    ]
    out = list(stub.MapBatch(iter(reqs)))
    assert [r.kontablo_id for r in out] == [
        "asset.current.receivables",
        "liability.current.payables",
    ]


def test_consolidate_with_intercompany_elimination(channel):
    """Round-trip the two-ERP reconciliation through gRPC and confirm it
    balances and the elimination is applied."""
    stub = pb_grpc.ConsolidationServiceStub(channel)
    parent = pb.SubsidiaryTrialBalance(
        subsidiary_id="iberica-es",
        jurisdiction="es",
        currency="EUR",
        entries=[
            pb.TrialBalanceEntry(local_code="430", local_name="Clientes", debit=300_000),
            pb.TrialBalanceEntry(local_code="700", local_name="Ventas", credit=300_000),
        ],
    )
    sub = pb.SubsidiaryTrialBalance(
        subsidiary_id="norte-mx",
        jurisdiction="mx",
        currency="MXN",
        entries=[
            pb.TrialBalanceEntry(local_code="102", local_name="Bancos", debit=1_724_137.93),
            pb.TrialBalanceEntry(local_code="201", local_name="Proveedores", credit=1_724_137.93),
        ],
    )
    # Double-entry elimination: parent receivable ↔ subsidiary payable.
    elim = pb.IntercompanyElimination(
        from_subsidiary="iberica-es",
        to_subsidiary="norte-mx",
        amount=100_000.0,
        kontablo_id="asset.current.receivables",
        contra_kontablo_id="liability.current.payables",
    )
    req = pb.ConsolidationRequest(
        parent_company_id="iberica-es",
        target_currency="USD",
        subsidiaries=[parent, sub],
        eliminations=[elim],
    )
    resp = stub.ConsolidateTrialBalances(req)
    assert resp.eliminations_applied == 1
    total_debit = sum(e.debit for e in resp.trial_balance)
    total_credit = sum(e.credit for e in resp.trial_balance)
    assert round(total_debit - total_credit, 2) == 0.0


def test_validate_balance_sheet(channel):
    stub = pb_grpc.ValidationServiceStub(channel)
    ok = stub.ValidateBalanceSheet(
        pb.ValidationRequest(
            jurisdiction="es",
            entries=[
                pb.TrialBalanceEntry(local_code="572", debit=100.0),
                pb.TrialBalanceEntry(local_code="100", credit=100.0),
            ],
        )
    )
    assert ok.is_valid is True
    assert ok.balance_difference == 0.0

    bad = stub.ValidateBalanceSheet(
        pb.ValidationRequest(
            entries=[pb.TrialBalanceEntry(local_code="572", debit=100.0)]
        )
    )
    assert bad.is_valid is False
    assert bad.balance_difference == 100.0


def test_planned_rpc_returns_unimplemented(channel):
    stub = pb_grpc.ValidationServiceStub(channel)
    with pytest.raises(grpc.RpcError) as exc:
        stub.ValidateCompleteness(pb.CompletenessRequest(jurisdiction="es"))
    assert exc.value.code() == grpc.StatusCode.UNIMPLEMENTED
