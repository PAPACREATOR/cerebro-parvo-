from __future__ import annotations

import hashlib

import pytest

from nexus.contracts import Blocked
from nexus.lab.wiki.context_packet import raw_json
from nexus.lab.wiki.flow_proposal import propose, validate_proposal


def packet():
    content = "fonte wiki verificada"
    return {
        "version": 1,
        "objective": "Rever e preparar PDF com contexto verificado",
        "trust": "UNTRUSTED_CONTEXT",
        "sources": [
            {
                "run_id": "1" * 32,
                "content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                "provenance_sha256": "3" * 64,
                "authority": "canonical",
                "content": content,
                "process_id": "verify",
                "input_sha256": "4" * 64,
            }
        ],
    }


def digest(value):
    return hashlib.sha256(raw_json(value)).hexdigest()


def resign(plan):
    unsigned = dict(plan)
    unsigned.pop("plan_sha256", None)
    plan["plan_sha256"] = digest(unsigned)
    return plan


def test_wiki_context_can_build_flow_candidate_without_authority():
    value = propose(packet(), ["proofread", "convert_pdf"])
    assert value["kind"] == "LAB_FLOW_CANDIDATE"
    assert value["authority"] == "NONE"
    assert value["steps"] == ["proofread", "convert_pdf"]
    assert value["sources"][0]["run_id"] == "1" * 32
    assert "content" not in value["sources"][0]
    assert validate_proposal(packet(), value) == value


@pytest.mark.parametrize("steps", [
    [], ["canonical"], ["approve"], ["shell"], ["web"], ["proofread", "proofread"],
    [None], "proofread", ["verify"] * 9,
])
def test_wiki_flow_candidate_rejects_unauthorized_or_ambiguous_steps(steps):
    with pytest.raises(Blocked):
        propose(packet(), steps)


@pytest.mark.parametrize(("field", "value"), [
    ("authority", "CANONICAL"),
    ("kind", "EXECUTABLE_FLOW"),
    ("objective", "changed"),
    ("context_sha256", "0" * 64),
    ("steps", ["verify", "canonical"]),
    ("sources", []),
])
def test_wiki_flow_candidate_tamper_is_blocked_even_if_rehashed(field, value):
    candidate = propose(packet(), ["verify", "proofread"])
    candidate[field] = value
    resign(candidate)
    with pytest.raises(Blocked):
        validate_proposal(packet(), candidate)


def test_wiki_flow_candidate_plain_byte_tamper_is_blocked():
    candidate = propose(packet(), ["verify"])
    candidate["plan_sha256"] = "0" * 64
    with pytest.raises(Blocked, match="adulterada"):
        validate_proposal(packet(), candidate)


def test_wiki_flow_candidate_is_deterministic_and_source_bound():
    first = propose(packet(), ["verify", "proofread"])
    second = propose(packet(), ["verify", "proofread"])
    assert first == second

    changed = packet()
    changed["sources"][0]["content"] += " alterada"
    changed["sources"][0]["content_sha256"] = hashlib.sha256(
        changed["sources"][0]["content"].encode("utf-8")
    ).hexdigest()
    with pytest.raises(Blocked):
        validate_proposal(changed, first)


# Fail-first regression: untrusted context/flow JSON must never exploit Python's
# bool == 1 or float == 1.0 coercion or leak TypeError into the caller.
@pytest.mark.parametrize("wrong", [True, 1.0, "1", None])
def test_context_protocol_version_is_exact_integer(wrong):
    from nexus.lab.wiki.context_packet import check_packet

    value = packet()
    value["version"] = wrong
    with pytest.raises(ValueError):
        check_packet(value)


@pytest.mark.parametrize("wrong", [True, 1.0])
def test_resigned_flow_protocol_version_cannot_alias_integer_v1(wrong):
    candidate = propose(packet(), ["verify"])
    candidate["version"] = wrong
    resign(candidate)
    with pytest.raises(Blocked):
        validate_proposal(packet(), candidate)


@pytest.mark.parametrize("wrong", [None, True, False, 7, 1.5])
def test_resigned_flow_with_non_list_steps_is_blocked_not_crashed(wrong):
    candidate = propose(packet(), ["verify"])
    candidate["steps"] = wrong
    resign(candidate)
    with pytest.raises(Blocked):
        validate_proposal(packet(), candidate)
