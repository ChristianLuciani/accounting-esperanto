"""
Schema validation tests

Run: pytest tests/
"""

import json
from pathlib import Path
from jsonschema import validate, ValidationError
import pytest

SCHEMA_PATH = Path("core/schemas/account.schema.json")
ACCOUNTS_PATH = Path("spec/machine/nodes.json")

def load_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)

def load_accounts():
    with open(ACCOUNTS_PATH) as f:
        return json.load(f)

def test_schema_exists():
    """Ensure schema file exists"""
    assert SCHEMA_PATH.exists()

def test_accounts_valid():
    """All accounts must pass schema validation"""
    schema = load_schema()
    accounts = load_accounts()
    
    for account in accounts:
        try:
            validate(instance=account, schema=schema)
        except ValidationError as e:
            pytest.fail(f"Account {account.get('uuid')} failed validation: {e.message}")

def test_unique_uuids():
    """UUIDs must be unique"""
    accounts = load_accounts()
    uuids = [a["uuid"] for a in accounts]
    assert len(uuids) == len(set(uuids)), "Duplicate UUIDs found"

def test_nature_consistency():
    """Assets (code 1.*) must be debit, Liabilities (2.*) must be credit"""
    accounts = load_accounts()
    
    for account in accounts:
        code = account["standard_code"]
        nature = account["nature"]
        
        if code.startswith("1") or code.startswith("5"):
            assert nature == "debit", f"{code} should be debit"
        elif code.startswith("2") or code.startswith("3") or code.startswith("4"):
            assert nature == "credit", f"{code} should be credit"

def test_parent_exists():
    """If parent_uuid is specified, it must exist"""
    accounts = load_accounts()
    all_uuids = {a["uuid"] for a in accounts}
    
    for account in accounts:
        parent = account.get("relations", {}).get("parent_uuid")
        if parent:
            assert parent in all_uuids, f"Parent {parent} not found for {account['uuid']}"
