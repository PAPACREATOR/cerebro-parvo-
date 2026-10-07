from copy import deepcopy

from cerebro.core import (
    ContentClass,
    build_creative_candidate,
    create_attachment,
    create_operation,
    provenance,
    receive_file,
)


def test_provenance_does_not_modify_candidate_content(tmp_path):
    source=tmp_path/"source.txt"
    source.write_bytes(b"conteudo original")
    received=receive_file(source)
    operation=create_operation(received)
    attachment=create_attachment(operation,received)
    candidate=build_creative_candidate(
        operation,
        attachment,
        {"text":"conteudo original","nested":{"value":1}},
        ContentClass.READY,
    )
    before=deepcopy(candidate)
    record=provenance(
        candidate,
        {"id":"test-tool","version":"1"},
        {"source_sha256":"evidence-only"},
    )
    assert candidate == before
    assert candidate["content"] == before["content"]
    assert record["candidate_id"] == candidate["candidate_id"]
    assert record["operation_id"] == candidate["operation_id"]
    assert record["attachment_id"] == candidate["attachment_id"]
