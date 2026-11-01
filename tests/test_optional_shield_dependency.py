"""Package reachability and metadata for the optional Shield dependency."""

from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _literal(node: ast.AST, constants: dict[str, object]) -> object:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return constants[node.id]
    if isinstance(node, ast.List):
        return [_literal(item, constants) for item in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(_literal(item, constants) for item in node.elts)
    if isinstance(node, ast.Dict):
        return {
            _literal(key, constants): _literal(value, constants)
            for key, value in zip(node.keys, node.values)
        }
    raise AssertionError(f"unsupported setup metadata expression: {ast.dump(node)}")


def _setup_metadata() -> tuple[dict[str, object], dict[str, object]]:
    tree = ast.parse((ROOT / "setup.py").read_text(encoding="utf-8"))
    constants: dict[str, object] = {}
    setup_call: ast.Call | None = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                try:
                    constants[target.id] = _literal(node.value, constants)
                except (KeyError, AssertionError):
                    pass
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call = node.value
            if isinstance(call.func, ast.Name) and call.func.id == "setup":
                setup_call = call
    assert setup_call is not None
    metadata = {
        keyword.arg: _literal(keyword.value, constants)
        for keyword in setup_call.keywords
        if keyword.arg in {"install_requires", "extras_require", "version"}
    }
    return constants, metadata


def test_base_install_excludes_shield_but_legacy_extra_keeps_pin() -> None:
    constants, metadata = _setup_metadata()

    assert metadata["install_requires"] == ["python-dotenv==1.2.2"]
    extras = metadata["extras_require"]
    assert isinstance(extras, dict)
    assert extras["legacy-shield"] == ["facehuggershield==1.0.0"]
    assert constants["FACEHUGGERSHIELD_REQUIREMENT"] == "facehuggershield==1.0.0"
    assert metadata["version"] == "6.1.8"
    package_metadata = ast.parse(
        (ROOT / "airunner_common" / "package_metadata.py").read_text(
            encoding="utf-8"
        )
    )
    package_version = next(
        ast.literal_eval(node.value)
        for node in package_metadata.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "VERSION" for target in node.targets)
    )
    assert package_version == metadata["version"]


def test_runtime_imports_and_llm_request_contract_without_shield(tmp_path: Path) -> None:
    blocked_import_program = r'''
import importlib.abc
import importlib.util
from pathlib import Path
import sys

class BlockShield(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "facehuggershield" or fullname.startswith("facehuggershield."):
            raise AssertionError("common runtime attempted to import FacehuggerShield")
        return None

sys.meta_path.insert(0, BlockShield())
import airunner_common
expected = Path(sys.argv[1]).resolve()
assert Path(airunner_common.__file__).resolve().parent == expected
import airunner_common.settings
from airunner_common.contract_enums import MessageRole
from airunner_common.llm_request import LLMRequest

request = LLMRequest()
assert request.role is MessageRole.USER
assert request.max_new_tokens == 8192
assert "facehuggershield" not in sys.modules
'''
    env = {
        "HOME": str(tmp_path),
        "TMPDIR": str(tmp_path),
        "PYTHONPATH": str(ROOT),
        "PYTHONNOUSERSITE": "1",
        "DEV_ENV": "0",
        "AIRUNNER_SAVE_LOG_TO_FILE": "0",
        "AIRUNNER_OFFLINE_MODE": "1",
        "PATH": os.environ.get("PATH", ""),
    }
    result = subprocess.run(
        [sys.executable, "-c", blocked_import_program, str(ROOT / "airunner_common")],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
