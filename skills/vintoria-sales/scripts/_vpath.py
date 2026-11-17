"""Puts every scripts/<group>/ folder on sys.path, so a script in one group can import a module from another
(e.g. outreach/outreach.py imports core/pipeline.py). Each script runs:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import _vpath  # noqa: F401
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GROUPS = ("core", "leads", "research", "outreach", "replies", "ops")

for _g in reversed(GROUPS):
    _p = str(ROOT / _g)
    if _p not in sys.path:
        sys.path.insert(0, _p)
