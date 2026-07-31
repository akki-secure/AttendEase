import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

os.environ.setdefault("ATTENDEASE_BASE_URL", "http://localhost:8000")
os.environ.setdefault("ATTENDEASE_EMPLOYEE_ID", "EMP001")
os.environ.setdefault("ATTENDEASE_PASSWORD", "dummy-password")
