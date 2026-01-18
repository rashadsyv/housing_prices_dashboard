"""
Root pytest configuration.

Registers custom markers and auto-marks tests based on directory location.
Shared fixtures should be placed in unit/ or integration/ conftest files.
"""

import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test (fast, no external deps)"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test (requires full stack)"
    )
    config.addinivalue_line("markers", "slow: mark test as slow running")


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location."""
    for item in items:
        if "/unit/" in str(item.fspath) or "\\unit\\" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "/integration/" in str(item.fspath) or "\\integration\\" in str(
            item.fspath
        ):
            item.add_marker(pytest.mark.integration)
