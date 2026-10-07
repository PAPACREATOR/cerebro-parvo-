from cerebro.core import (
    ContentClass,
    build_creative_candidate,
    create_attachment,
    create_operation,
    prepare_events,
    provenance,
    receive_file,
)
from cerebro.integration import commit_prepared_event
from cerebro.persistence import RecoverableMarkdownWriter


def test_core_to_persistence_commits_before_success_event(tmp_path):
    source=tmp_path/"source.md"
    source.write_bytes(b"# original\n")
    received=receive_file(source)
    operation=create_operation(received)
    attachment=create_attachment(operation,received)
    candidate=build_creative_candidate(
        operation,
        attachment,
        "# candidato\n",
        ContentClass.READY,
    )
    prov=provenance(
        candidate,
        {"id":"deterministic-test","version":"1"},
        {"source":"source.md"},
    )
    prepared=prepare_events(candidate,prov)[0]
    writer=RecoverableMarkdownWriter(
        tmp_path/"state"/"cerebro.sqlite3",
        tmp_path/"vault",
    )

    committed=commit_prepared_event(prepared,writer,"imports/candidato.md")

    assert committed["type"] == "CREATIVE_CANDIDATE_COMMITTED"
    assert committed["state"] == "COMMITTED"
    assert writer.reconcile(operation.operation_id) == "COMMITTED"
    assert (tmp_path/"vault"/"creative"/"imports"/"candidato.md").read_bytes() == b"# candidato\n"
    assert source.read_bytes() == b"# original\n"
    assert committed["operation_id"] == operation.operation_id
    assert committed["candidate_id"] == candidate["candidate_id"]
    assert committed["attachment_id"] == attachment.attachment_id
