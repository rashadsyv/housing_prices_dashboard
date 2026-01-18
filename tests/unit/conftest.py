"""
Unit test fixtures.

Unit tests should be fast and not require external dependencies.
Only lightweight fixtures belong here.
"""

import os
import sys

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
