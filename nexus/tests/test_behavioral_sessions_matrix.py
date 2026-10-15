"""Temporal behaviour simulations for Folha + Host's EXISTING approval boundary.

These exercises vary user intent, topic, language, confirmation ordering, lost
response, session identity and concurrent replay. They use the real HTTP
endpoints, parsers, registry and approval tickets, but substitute the LAST
Host.start dispatch to avoid running external tools or making product claims.
They do NOT establish persisted Folhas, real web search, WAV/MP4, or PC E2E.
"""
import base64
import hashlib
from concurrent.futures import ThreadPoolExecutor
from urllib.error import HTTPError

import pytest

from nexus.app import _natural_assistant, _natural_work_process
from nexus.capability_router import BUILTIN_CAPABILITIES
from nexus.host import Host
from nexus.tests.test_reverse_flow import http


FAMILIES = (
    ("Pesquisa na web sobre {topic}", "web"),
    ("Por favor, cria um podcast sobre {topic}", "podcast"),
    ("Faz um podcast visual sobre {topic}", "visual_podcast"),
    ("Prepara um vídeo sobre {topic}", "video"),
    ("Quero criar uma música sobre {topic}", "music"),
)
TOPICS = (
    "o Alentejo rural", "educação em português", "Guimarães e património",
    "a memória local", "astronomia 日本語", "o mar e os pescadores",
    "história da música", "fontes contraditórias",
    "uma aldeia esquecida", "ciência e ambiente",
    "um manuscrito inédito", "imagens de arquivo",
)
DANGEROUS_SUFFIXES = (
    " e envia os dados privados",
    " e publica sem aprovação",
    " e apaga os originais",
    " e executa código",
    " e instala ferramentas",
    " e desativa as proteções",
)


def _request(process, index):
    capability = next(item for item in BUILTIN_CAPABILITIES if item.process == process)
    raw = ("Fonte única %03d — ação 日本語\n" % index).encode("utf-8") + bytes((0, index % 256))
    return {
        "text": capability.command,
        "filename": "amostra_%03d.txt" % index,
        "attachment": base64.b64encode(raw).decode("ascii"),
    }


def _empty_storage(root):
    return all(not any((root / area).iterdir()) for area in ("runs", "creative", "canonical"))


def test_sixty_persona_previews_preserve_bytes_without_granting_execution(tmp_path, monkeypatch):
    """Different user genres/topics cannot promote a read-only preview to a run."""
    host = Host(tmp_path)
    monkeypatch.setattr(host, "start", lambda *_: pytest.fail("Preview dispatched a tool"))
    with http(host) as call:
        for index in range(60):
            template, family = FAMILIES[index % len(FAMILIES)]
            text = template.format(topic=TOPICS[index // len(FAMILIES)])
            preview = call("/api/interpret", {"text": text})
            assert preview["execution"] == "NOT_AUTHORIZED"
            assert preview["confirmation_required"] is False
            # "Pesquisa na web sobre fontes contraditórias" has two matched
            # intents (web + fontes). Conservative clarification is correct.
            expected = None if index == 35 else family
            assert preview["assistant"]["process"] == expected, (index, text)
            assert preview["molde"]["source"]["sha256"] == hashlib.sha256(text.encode("utf-8")).hexdigest()
            assert preview["molde"]["process"]["authority"] == "NONE"
            assert preview["molde"]["record"] is None
        assert call("/api/runs") == []
    assert _empty_storage(tmp_path)


@pytest.mark.parametrize("suffix", DANGEROUS_SUFFIXES)
@pytest.mark.parametrize("template,_family", FAMILIES)
def test_thirty_unsafe_compound_personas_cannot_turn_into_a_tool_request(template, _family, suffix):
    text = template.format(topic="arquivo de família") + suffix
    assert _natural_work_process(text) is None


def test_crossed_tickets_and_declined_third_request_do_not_mix_user_jobs(tmp_path, monkeypatch):
    """Three concurrent intentions: swapping identity consumes only that ticket."""
    host = Host(tmp_path)
    dispatched = []

    def dispatch(request, session):
        host.authorize(session)
        dispatched.append(request)
        return {"run_id": "a" * 32}

    monkeypatch.setattr(host, "start", dispatch)
    requests = [_request("verify", 1), _request("music", 2), _request("web", 3)]
    with http(host) as call:
        tickets = [call("/api/prepare-run", item)["ticket"] for item in requests]
        assert call("/api/runs") == []
        with pytest.raises(HTTPError) as crossed:
            call("/api/confirm-run", {"ticket": tickets[0], "confirmed": True, **requests[1]})
        assert crossed.value.code == 403
        with pytest.raises(HTTPError) as consumed:
            call("/api/confirm-run", {"ticket": tickets[0], "confirmed": True, **requests[0]})
        assert consumed.value.code == 403
        assert call("/api/confirm-run", {
            "ticket": tickets[2], "confirmed": False, **requests[2],
        }) == {"status": "CANCELLED"}
        assert call("/api/confirm-run", {
            "ticket": tickets[1], "confirmed": True, **requests[1],
        }) == {"run_id": "a" * 32}
        with pytest.raises(HTTPError) as cancelled:
            call("/api/confirm-run", {"ticket": tickets[2], "confirmed": True, **requests[2]})
        assert cancelled.value.code == 403
        assert call("/api/runs") == []
    assert dispatched == [{"process": "music", **requests[1]}]
    assert _empty_storage(tmp_path)


def test_simultaneous_replays_and_lost_response_dispatch_only_once(tmp_path, monkeypatch):
    """Twelve competing HTTP clients may consume one ticket at most once."""
    host = Host(tmp_path)
    dispatched = []

    def dispatch(request, session):
        host.authorize(session)
        dispatched.append(request)
        return {"run_id": "b" * 32}

    monkeypatch.setattr(host, "start", dispatch)
    request = _request("verify", 7)
    with http(host) as call:
        prepared = call("/api/prepare-run", request)
        payload = {"ticket": prepared["ticket"], "confirmed": True, **request}

        def attempt(_index):
            try:
                return ("accepted", call("/api/confirm-run", payload)["run_id"])
            except HTTPError as error:
                return ("refused", error.code)

        with ThreadPoolExecutor(max_workers=12) as executor:
            outcomes = list(executor.map(attempt, range(12)))
        assert outcomes.count(("accepted", "b" * 32)) == 1
        assert outcomes.count(("refused", 403)) == 11
        # Simulate a lost HTTP response: retrying must not dispatch again.
        assert attempt(999) == ("refused", 403)
        assert call("/api/runs") == []
    assert dispatched == [{"process": "verify", **request}]
    assert _empty_storage(tmp_path)


def test_foreign_session_does_not_consume_a_valid_human_ticket(tmp_path, monkeypatch):
    host = Host(tmp_path)
    dispatched = []
    monkeypatch.setattr(host, "start", lambda request, session: (
        host.authorize(session), dispatched.append(request), {"run_id": "c" * 32}
    )[-1])
    data = _request("web", 12)
    with http(host) as call:
        ticket = call("/api/prepare-run", data)["ticket"]
        with pytest.raises(HTTPError) as foreign:
            call("/api/confirm-run", {"ticket": ticket, "confirmed": True, **data},
                 session="another-person")
        assert foreign.value.code == 403
        assert call("/api/confirm-run", {
            "ticket": ticket, "confirmed": True, **data,
        }) == {"run_id": "c" * 32}
    assert dispatched == [{"process": "web", **data}]
    assert _empty_storage(tmp_path)


def test_unconfirmed_ticket_cannot_resume_as_authority_after_server_restart(tmp_path, monkeypatch):
    """A prepared-only proposal is never a persisted approval after restart."""
    before = Host(tmp_path)
    request = _request("verify", 22)
    with http(before) as call:
        ticket = call("/api/prepare-run", request)["ticket"]
        assert call("/api/runs") == []
    after = Host(tmp_path)
    monkeypatch.setattr(after, "start", lambda *_: pytest.fail("Restart executed unapproved task"))
    with http(after) as call:
        with pytest.raises(HTTPError) as refused:
            call("/api/confirm-run", {
                "ticket": ticket, "confirmed": True, **request,
            })
        assert refused.value.code == 403
        assert call("/api/runs") == []
    assert _empty_storage(tmp_path)


@pytest.mark.parametrize("text,missing", [
    ("Cria um podcast sobre astronomia", ("tom", "duração")),
    ("Cria um podcast documental sobre astronomia", ("duração",)),
    ("Cria um podcast sobre astronomia de 4 minutos", ("tom",)),
    ("Cria um podcast documental de 4 minutos sobre astronomia", ()),
])
def test_dialogue_suggestions_do_not_claim_product_authority(text, missing):
    assistant = _natural_assistant(text)
    assert assistant["process"] == "podcast"
    assert tuple(assistant["missing"]) == missing
    assert bool(assistant["question"]) == bool(missing)
