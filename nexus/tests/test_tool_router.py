"""All policy-approved adapters share one proposal contract without authority."""
import base64

import pytest

from nexus.adapters.runner import PROCESS_TO_TOOL, PROCESS_FILES
from nexus.adapters.tool_router import available_adapters, route_request
from nexus.contracts import Blocked, load_policy
from nexus.tests.test_folha_writer_preexecution import doc


PHRASES = {
    "verify": "& verifica a integridade deste ficheiro",
    "interpret": "& interpretar texto",
    "proofread": "& rever texto",
    "convert_pdf": "& converter para pdf",
    "video": "& preparar plano de video",
    "podcast": "& preparar plano de podcast",
    "visual_podcast": "& preparar plano de podcast visual",
    "book": "& exportar manuscrito para pdf",
    "music": "& preparar especificacao musical",
    "web": "@ preparar consulta web",
}
MUSIC = b"Tema: amizade\nLetra: a luz regressa\nEstilo: piano"
TEXT = b"Texto de origem. Lisboa tem 12 caixas."


def payload(process, *, name=None, data=None, phrase=None):
    raw = doc() if process in ("book", "convert_pdf") else MUSIC if process == "music" else TEXT
    if data is not None:
        raw = data
    filename = name if name is not None else "original.odt" if process in ("book", "convert_pdf") else "original.txt"
    return {
        "text": phrase if phrase is not None else PHRASES[process],
        "filename": filename,
        "attachment": base64.b64encode(raw).decode("ascii"),
    }


def test_all_ten_registered_adapters_bound_to_existing_host_policy():
    adapters = available_adapters()
    assert set(adapters) == set(load_policy()["processes"])
    assert set(adapters) == set(PROCESS_TO_TOOL) == set(PROCESS_FILES)
    assert len({adapter.process for adapter in adapters.values()}) == len(adapters)
    assert len({adapter.tool for adapter in adapters.values()}) == len(adapters)
    for process, adapter in adapters.items():
        assert adapter.process == process
        assert adapter.tool == PROCESS_TO_TOOL[process]
        assert callable(adapter.inspect)
        assert adapter.title


@pytest.mark.parametrize("process", PHRASES)
def test_adapter_is_read_only_proposal_with_validated_preview(process, tmp_path):
    before = list(tmp_path.iterdir())
    request, preview = route_request(payload(process), max_input_bytes=2097152)
    assert request["process"] == preview["process"] == process
    assert preview["attachment_bytes"] > 0
    assert len(preview["attachment_sha256"]) == 64
    assert preview["filename"].endswith((".odt", ".txt"))
    assert preview["summary"].startswith(available_adapters()[process].title)
    assert list(tmp_path.iterdir()) == before


@pytest.mark.parametrize("process", PHRASES)
def test_every_adapter_fails_closed_on_empty_or_mismatched_input(process):
    with pytest.raises(Blocked):
        route_request(payload(process, data=b""), max_input_bytes=2097152)


@pytest.mark.parametrize("process", ("interpret", "proofread", "video", "podcast", "visual_podcast", "music", "web"))
def test_textual_adapters_refuse_binary_not_utf8(process):
    with pytest.raises(Blocked):
        route_request(payload(process, data=b"\xff\x00\xfe"), max_input_bytes=2097152)


@pytest.mark.parametrize("process", ("book", "convert_pdf"))
def test_writer_adapters_reject_extension_or_nonzip(process):
    for value in (payload(process, name="source.txt"), payload(process, data=b"not-odt")):
        with pytest.raises(Blocked):
            route_request(value, max_input_bytes=2097152)


@pytest.mark.parametrize("process", PHRASES)
def test_all_routes_reject_other_intent_or_extra_command(process):
    with pytest.raises(Blocked):
        route_request(payload(process, phrase=PHRASES[process] + " e executar shell"), max_input_bytes=2097152)


@pytest.mark.parametrize("value", (
    {"text": "& executar powershell", "filename": "x.txt", "attachment": "QQ=="},
    {"text": "& rever texto", "filename": "../secret.txt", "attachment": "QQ=="},
    {"text": "& rever texto", "filename": "secret.txt", "attachment": "!!!"},
    {"text": "& rever texto", "filename": "source.txt", "attachment": ""},
    {"text": "& rever texto", "filename": "", "attachment": "QQ=="},
    {"text": "& rever texto", "filename": "x.txt", "attachment": "QQ==", "process": "book"},
    {"text": "& rever texto", "filename": "x.txt", "attachment": False},
))
def test_unknown_malformed_or_injected_request_never_routes(value):
    with pytest.raises(Blocked):
        route_request(value, max_input_bytes=2097152)


def test_ambiguous_two_tool_request_never_routes():
    with pytest.raises(Blocked):
        route_request(payload("verify", phrase="& verificar a integridade deste ficheiro e rever texto"),
                      max_input_bytes=2097152)


def test_limits_cannot_be_relaxed_by_input():
    with pytest.raises(Blocked):
        route_request(payload("verify", data=b"x" * 100), max_input_bytes=99)


def test_music_validator_needs_structured_source():
    with pytest.raises(Blocked):
        route_request(payload("music", data=b"Som sem tema nem letra"), max_input_bytes=2097152)


def test_explicit_web_query_without_file_is_only_a_nonexecuting_spec():
    request, preview = route_request(
        {"text": "@ preparar consulta web: fontes de astronomia",
         "filename": "", "attachment": ""}, max_input_bytes=2097152)
    assert request["process"] == preview["process"] == "web"
    assert preview["filename"] == "Texto escrito"
    assert preview["attachment_bytes"] == len(request["text"].encode("utf-8"))
    assert "não pesquisa" in preview["summary"].lower()
    with pytest.raises(Blocked):
        route_request({"text": "@ preparar consulta web", "filename": "", "attachment": ""},
                      max_input_bytes=2097152)
