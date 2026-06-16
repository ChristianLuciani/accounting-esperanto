"""Ensure the repository root is importable in every test session so tests can
`import core...`, `import examples...`, `import api...`, and the connector
package regardless of where pytest is invoked from."""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Keep the test session hermetic and reproducible: force the pinned static FX
# table so no test reaches the live FX endpoints. Production defaults to live
# (KONTABLO_FX_MODE=live); a developer can still override this for an explicit
# live-FX integration run. setdefault respects an already-exported value.
os.environ.setdefault("KONTABLO_FX_MODE", "static")
