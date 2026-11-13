import sys
from pathlib import Path

# PyHugo lives in the repository's scripts directory, two levels up from here.
_scripts_dir = str(Path(__file__).resolve().parent.parent.parent)
if _scripts_dir not in sys.path:
    sys.path.append(_scripts_dir)
