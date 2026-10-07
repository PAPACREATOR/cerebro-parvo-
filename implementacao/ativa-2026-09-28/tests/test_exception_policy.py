import ast
from pathlib import Path


ROOT=Path(__file__).parents[1]
TARGETS=[
    ROOT/"cerebro"/"core.py",
    ROOT/"cerebro"/"persistence.py",
    ROOT/"cerebro"/"integration.py",
]


def test_generic_exception_handlers_must_reraise_explicitly():
    violations=[]
    for path in TARGETS:
        tree=ast.parse(path.read_text(encoding="utf-8"),filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node,ast.ExceptHandler):
                continue
            if not isinstance(node.type,ast.Name) or node.type.id!="Exception":
                continue
            if not any(isinstance(child,ast.Raise) for statement in node.body for child in ast.walk(statement)):
                violations.append((path.name,node.lineno))
    assert violations == []
