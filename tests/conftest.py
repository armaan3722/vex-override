import sys
from unittest.mock import MagicMock


def pytest_configure() -> None:
    """Make ``from vex import *`` succeed during testing."""
    sys.modules["vex"] = MagicMock()
