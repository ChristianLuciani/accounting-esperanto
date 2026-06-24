"""End-to-end MCP demo: an agent client talking to the Kontablo MCP server.

This launches ``api.mcp.server`` as a subprocess over **stdio** (the standard
local-agent MCP transport) and drives it through the official MCP *client* — the
same handshake an LLM agent runtime performs. It is the runnable proof that the
agent-native MCP surface works end to end, not just in-process.

Run:
    python -m api.mcp.demo
"""

from __future__ import annotations

import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def _payload(result) -> dict:
    """Extract the JSON dict a Kontablo tool returns from a CallToolResult."""
    if result.structuredContent:
        return result.structuredContent
    return json.loads(result.content[0].text)


async def main() -> None:
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env = dict(os.environ)
    # Keep the demo hermetic/offline by default: pinned static FX, no network.
    env.setdefault("KONTABLO_FX_MODE", "static")

    params = StdioServerParameters(
        command=sys.executable, args=["-m", "api.mcp.server"], cwd=root, env=env
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Kontablo MCP tools:", [t.name for t in tools.tools])

            # 1. Resolve a local statutory account → universal UUID.
            #    MX SAT code 101 "Caja" → asset.current.cash (Tier-1 exact).
            r = _payload(
                await session.call_tool(
                    "resolve_account",
                    {"jurisdiction": "mx", "local_code": "101", "local_name": "Caja"},
                )
            )
            print(
                f"\nresolve(MX, SAT, 101, 'Caja') -> {r['kontablo_id']} "
                f"(uuid={r['kontablo_uuid']}, tier={r['tier']}, conf={r['confidence']})"
            )

            # 2. Look the node back up by UUID.
            g = _payload(await session.call_tool("get_account", {"uuid": r["kontablo_uuid"]}))
            print(f"get_account(uuid) -> {g['kontablo_id']}: {g['label_en']} ({g['nature']})")

            # 3. Validate a balanced trial balance.
            v = _payload(
                await session.call_tool(
                    "validate_balance_sheet",
                    {"entries": [{"debit": 100.0}, {"credit": 100.0}]},
                )
            )
            print(f"validate_balance_sheet -> is_valid={v['is_valid']}, diff={v['balance_difference']}")

            # 4. Coverage headline numbers (claims-evidence: 195 / 60 / 56).
            lj = _payload(await session.call_tool("list_jurisdictions", {}))
            s = lj["summary"]
            print(
                f"list_jurisdictions -> total={s['total']}, statutory_chart="
                f"{s['statutory_chart']}, tier1_codes_available={s['tier1_codes_available']}"
            )


if __name__ == "__main__":
    asyncio.run(main())
