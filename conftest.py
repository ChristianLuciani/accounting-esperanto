"""Ensure the repository root is importable in every test session so tests can
`import core...`, `import examples...`, `import api...`, and the connector
package regardless of where pytest is invoked from."""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
