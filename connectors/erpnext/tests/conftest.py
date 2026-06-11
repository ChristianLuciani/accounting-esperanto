"""Path + fixture setup for the ERPNext connector tests."""

import os
import sys

import pytest

# Make `import kontablo_client` resolve to the connector module.
CONNECTOR_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if CONNECTOR_DIR not in sys.path:
    sys.path.insert(0, CONNECTOR_DIR)

# Repo root, so the contract test can import the real api.src models/app.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(CONNECTOR_DIR)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


class FakeResponse:
    """Minimal stand-in for a requests.Response."""

    def __init__(self, json_data=None, status_code=200):
        self._json = json_data if json_data is not None else {}
        self.status_code = status_code

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests
            err = requests.exceptions.HTTPError(f"{self.status_code} error")
            err.response = self
            raise err


@pytest.fixture
def fake_response_cls():
    return FakeResponse
