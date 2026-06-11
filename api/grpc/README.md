# Kontablo gRPC interface

`kontablo.proto` defines the gRPC surface. `server.py` is a **minimal server that
implements the deterministic RPCs only**, over the same `core.engine` that backs
the REST API — so REST and gRPC agree for the deterministic core.

## Status (honest)

| Service / RPC | Status |
|---|---|
| `AccountService.ListAccounts / GetAccount / GetLocalCodes` | ✅ implemented |
| `MappingService.MapAccount / MapBatch (stream) / ValidateChart` | ✅ implemented (Tier-1/Tier-2 deterministic) |
| `ConsolidationService.ConsolidateTrialBalances` | ✅ implemented (with intercompany elimination) |
| `ValidationService.ValidateBalanceSheet` | ✅ implemented |
| `ClassificationService.*` | ⛔ `UNIMPLEMENTED` — depends on stochastic LLM inference |
| `ConsolidationService.GenerateFinancialStatements` | ⛔ `UNIMPLEMENTED` — planned |
| `ValidationService.ValidateCompleteness`, `SynonymService.*` | ⛔ `UNIMPLEMENTED` — planned |

The `UNIMPLEMENTED` RPCs return `grpc.StatusCode.UNIMPLEMENTED` rather than a
faked deterministic answer — exposing a stochastic capability as if it were
deterministic would violate the project's epistemic standards.

## Run

```bash
pip install -r requirements.txt
python -m api.grpc.server          # serves on 0.0.0.0:50051
```

## Regenerate stubs after editing the proto

Generated code lives in `api/grpc/gen/` and is committed. After changing
`kontablo.proto`:

```bash
python -m grpc_tools.protoc -I api/grpc \
  --python_out=api/grpc/gen --grpc_python_out=api/grpc/gen \
  api/grpc/kontablo.proto
# the grpc stub imports the pb2 module by a flat name; make it package-relative:
sed -i 's/^import kontablo_pb2 as kontablo__pb2/from api.grpc.gen import kontablo_pb2 as kontablo__pb2/' \
  api/grpc/gen/kontablo_pb2_grpc.py
```

`grpcio`/`grpcio-tools` are pinned to a protobuf-5.x line in `requirements.txt`
so they coexist with `google-generativeai`.

## Test

`tests/grpc/test_grpc_smoke.py` starts the real server and round-trips
`ListAccounts`, `MapAccount` (Tier-1 exact), streaming `MapBatch`,
`ConsolidateTrialBalances` (with elimination), and `ValidateBalanceSheet`, and
asserts a planned RPC returns `UNIMPLEMENTED`.
