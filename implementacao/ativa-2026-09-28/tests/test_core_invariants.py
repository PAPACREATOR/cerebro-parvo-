from copy import deepcopy

from cerebro.core import (
    ContentClass,
    build_creative_candidate,
    create_attachment,
    create_operation,
    exact_duplicate,
    provenance,
    Quarantined,
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


def test_equal_digest_never_overrides_byte_comparison(tmp_path):
    incoming=tmp_path/"incoming.bin"
    other=tmp_path/"other.bin"
    incoming.write_bytes(b"AAA")
    other.write_bytes(b"BBB")
    quarantined=Quarantined("attachment-in",incoming)
    forced_same_digest="same-digest-for-test"
    matches=exact_duplicate(
        quarantined,
        forced_same_digest,
        [("attachment-other",other,forced_same_digest)],
    )
    assert matches == []
    assert incoming.read_bytes() == b"AAA"
    assert other.read_bytes() == b"BBB"
