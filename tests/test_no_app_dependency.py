"""Regression tests for the extraction itself (issue #2197).

The whole point of extracting this package into its own repository was
that it depends on nothing from Capsize-Games/airunner -- every other
distribution in that repository depends on this one, and it depends on
none of them. Confirmed before extraction by grepping every import
statement in the source tree; these tests pin that here, independent of
whichever host application eventually installs this package.
"""

from __future__ import annotations

import re
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "airunner_common"

_APP_IMPORT_PATTERN = re.compile(
    r"^\s*(?:from|import)\s+(airunner\.|airunner_services\.|airunner_native\.)",
    re.MULTILINE,
)


def test_package_imports_nothing_from_the_source_application():
    offenders = []
    for path in _PACKAGE_ROOT.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        match = _APP_IMPORT_PATTERN.search(text)
        if match:
            offenders.append((str(path), match.group(0).strip()))
    assert offenders == []


def test_every_module_present():
    expected = {
        "__init__.py",
        "contract_enums.py",
        "contract_version.py",
        "dev_build_token.py",
        "get_logger.py",
        "linux_bundle_layout.py",
        "llm_response.py",
        "logging_utils.py",
        "package_metadata.py",
        "settings.py",
        "startup_env.py",
    }
    actual = {p.name for p in _PACKAGE_ROOT.glob("*.py")}
    assert expected.issubset(actual)
