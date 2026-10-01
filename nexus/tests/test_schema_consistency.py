import pytest
from nexus.contracts import validate, Blocked, ROOT, strict_json
from nexus.tests.test_store import result
from jsonschema import Draft202012Validator
from ruamel.yaml import YAML

@pytest.mark.parametrize("outcome,expected", [("agreement","PASS"),("conflict","UNKNOWN"),("unknown","UNKNOWN"),("failure","FAIL")])
@pytest.mark.parametrize("status", ["PASS","FAIL","UNKNOWN","BLOCKED"])
def test_result_matches_workflow_policy(outcome, expected, status):
    payload = {**result(), "outcome": outcome, "status": status}
    if status == expected:
        validate("result", payload)
    else:
        with pytest.raises(Blocked):
            validate("result", payload)

def test_all_schemas_are_valid():
    for path in (ROOT / "schemas").glob("*.json"):
        Draft202012Validator.check_schema(strict_json(path.read_bytes()))

def test_yaml_policy_matches_contract():
    workflow = YAML(typ="safe").load((ROOT / "processes/verify.yaml").read_text("utf-8"))
    policy = next(step["values"] for step in workflow["agents"] if step["name"] == "policy")
    for outcome, status in policy.items():
        validate("result", {**result(), "outcome":outcome,"status":status})
