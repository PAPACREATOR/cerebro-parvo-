import ast
from pathlib import Path

import pytest

from cerebro.core import PolicyUndefined, delete_authorized_original


ROOT=Path(__file__).parents[1]
PRODUCT=[
    ROOT/"cerebro"/"core.py",
    ROOT/"cerebro"/"persistence.py",
    ROOT/"cerebro"/"integration.py",
]
TESTS=list((ROOT/"tests").glob("test_*.py"))


def test_active_suite_does_not_use_filesystem_mocks():
    violations=[]
    for path in TESTS:
        tree=ast.parse(path.read_text(encoding="utf-8"),filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node,ast.ImportFrom) and node.module == "unittest.mock":
                violations.append((path.name,node.lineno))
            if isinstance(node,ast.Import):
                for alias in node.names:
                    if alias.name in {"mock","unittest.mock"}:
                        violations.append((path.name,node.lineno))
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr == "patch":
                owner=node.func.value
                if isinstance(owner,ast.Name) and owner.id == "mock":
                    violations.append((path.name,node.lineno))
    assert violations == []


def test_no_bare_except_or_silent_pass_handlers():
    violations=[]
    for path in PRODUCT:
        tree=ast.parse(path.read_text(encoding="utf-8"),filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node,ast.ExceptHandler):
                continue
            if node.type is None:
                violations.append((path.name,node.lineno,"bare-except"))
            if any(isinstance(statement,ast.Pass) for statement in node.body):
                violations.append((path.name,node.lineno,"silent-pass"))
    assert violations == []


def test_no_mutable_module_globals_in_product():
    violations=[]
    mutable_nodes=(ast.Dict,ast.List,ast.Set)
    for path in PRODUCT:
        tree=ast.parse(path.read_text(encoding="utf-8"),filename=str(path))
        for node in tree.body:
            value=None
            if isinstance(node,ast.Assign):
                value=node.value
            elif isinstance(node,ast.AnnAssign):
                value=node.value
            if isinstance(value,mutable_nodes):
                violations.append((path.name,node.lineno))
    assert violations == []


def test_original_deletion_remains_fail_closed(tmp_path):
    original=tmp_path/"original.bin"
    original.write_bytes(b"original-bytes")
    authorization={"approved":True}
    with pytest.raises(PolicyUndefined):
        delete_authorized_original(authorization,original)
    assert original.read_bytes() == b"original-bytes"
