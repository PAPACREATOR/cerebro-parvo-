from __future__ import annotations

from .persistence import RecoveryRequired


class IntegrationError(RuntimeError):
    pass


def commit_prepared_event(event, writer, relative_path):
    if not isinstance(event, dict) or event.get("type") != "CREATIVE_CANDIDATE_PREPARED":
        raise IntegrationError("expected prepared creative event")
    payload=event.get("payload")
    if not isinstance(payload, dict):
        raise IntegrationError("prepared event payload missing")
    candidate=payload.get("candidate")
    provenance=payload.get("provenance")
    if not isinstance(candidate, dict) or not isinstance(provenance, dict):
        raise IntegrationError("candidate/provenance missing")
    if candidate.get("domain") != "CREATIVE" or candidate.get("authority") != "CANDIDATE":
        raise IntegrationError("invalid creative candidate authority")
    operation_id=candidate.get("operation_id")
    candidate_id=candidate.get("candidate_id")
    attachment_id=candidate.get("attachment_id")
    if not all(isinstance(value, str) and value for value in (operation_id,candidate_id,attachment_id)):
        raise IntegrationError("candidate correlation missing")
    if event.get("operation_id") != operation_id:
        raise IntegrationError("event operation mismatch")
    if provenance.get("operation_id") != operation_id:
        raise IntegrationError("provenance operation mismatch")
    if provenance.get("candidate_id") != candidate_id:
        raise IntegrationError("provenance candidate mismatch")
    if provenance.get("attachment_id") != attachment_id:
        raise IntegrationError("provenance attachment mismatch")
    content=candidate.get("content")
    if not isinstance(content, str):
        raise IntegrationError("creative materialization requires text content")

    receipt=writer.write(operation_id,"CREATIVE",relative_path,content)
    if receipt.state != "COMMITTED":
        raise RecoveryRequired("writer returned without committed state")

    return {
        "type":"CREATIVE_CANDIDATE_COMMITTED",
        "operation_id":operation_id,
        "candidate_id":candidate_id,
        "attachment_id":attachment_id,
        "relative_path":receipt.relative_path,
        "expected_hash":receipt.expected_hash,
        "state":receipt.state,
    }
