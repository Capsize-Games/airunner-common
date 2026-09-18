"""Every module must import cleanly on a clean install (issue #2197).

The package's own verification requirement:
``python -c "import airunner_common"`` succeeds with nothing else from
Capsize-Games/airunner present. Exercises every submodule individually,
not just the package's own ``__init__.py``, since ``__init__.py`` does
not itself import any of them (see its own docstring).
"""

from __future__ import annotations

import importlib

import pytest

_SUBMODULES = [
    "airunner_common",
    "airunner_common.contract_enums",
    "airunner_common.contract_version",
    "airunner_common.dev_build_token",
    "airunner_common.generation_presets",
    "airunner_common.get_logger",
    "airunner_common.linux_bundle_layout",
    "airunner_common.llm_request",
    "airunner_common.llm_response",
    "airunner_common.logging_utils",
    "airunner_common.package_metadata",
    "airunner_common.settings",
    "airunner_common.startup_env",
]


@pytest.mark.parametrize("module_name", _SUBMODULES)
def test_module_imports(module_name: str) -> None:
    importlib.import_module(module_name)


def test_contract_version_compatibility() -> None:
    from airunner_common.contract_version import is_compatible_contract_version

    assert is_compatible_contract_version("1.0.0", "1.2.3")
    assert not is_compatible_contract_version("1.0.0", "2.0.0")


def test_get_logger_resolver_injection(tmp_path, monkeypatch) -> None:
    """A registered log-base-path resolver is used for file logging.

    The resolver is only consulted when file logging is enabled
    (AIRUNNER_SAVE_LOG_TO_FILE=1); get_logger() alone never touches it.
    """
    from airunner_common.get_logger import (
        get_logger,
        set_log_base_path_resolver,
    )

    monkeypatch.setenv("AIRUNNER_SAVE_LOG_TO_FILE", "1")
    monkeypatch.delenv("AIRUNNER_LOG_FILE", raising=False)
    calls = []

    def _resolver() -> str:
        calls.append(1)
        return str(tmp_path)

    set_log_base_path_resolver(_resolver)
    try:
        get_logger("test_module_imports_resolver_injection")
        assert calls, "resolver was never invoked"
        assert (tmp_path / "airunner.log").exists()
    finally:
        set_log_base_path_resolver(None)
