"""Kontablo agent-native MCP surface.

This package exposes Kontablo's *deterministic* accounting operations as
Model Context Protocol (MCP) tools, so an LLM/agent can consume them as the
agent-native layer described in CLAUDE.md architectural principle #4. It is a
thin adapter over the same ``core.harness`` / ``core.engine`` brain that backs
the REST API and the gRPC server — one mapping/consolidation engine, exposed
over multiple machine-consumable faces. No tool here calls an LLM.

The server lives in :mod:`api.mcp.server`; import ``build_mcp`` / ``mcp`` from
there. (Kept import-light here so ``python -m api.mcp.server`` runs without a
runpy double-import warning.)
"""
