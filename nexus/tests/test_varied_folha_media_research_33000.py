"""32K+ deterministic varied Folha boundary cases; no fictitious media outputs.

Actual production parser, read-only mold and capability router; real media,
OpenNotebook, PC installation and generated assets are explicitly NOT tested.
A correct refusal is a PASS for a malicious/unsupported request, never proof
that a tool executed. No Host/Kernel/Store mutations.
"""
import base64
import hashlib

import pytest

from nexus.adapters.constitutional import build_molde
from nexus.app import _natural_work_process
from nexus.capability_router import BUILTIN_CAPABILITIES, declared_router
from nexus.contracts import Blocked
from nexus.frontdoor import parse
from nexus.natural_bridge import from_markdown, to_markdown


# Research, podcast, visual podcast, film/video and music are all real
# production *planning* families, not claims of generated external artifacts.
TEMPLATES = (
    ("Pesquisa na web sobre {topic}", "web", "@"),
    ("Por favor, cria um podcast sobre {topic}", "podcast", "&"),
    ("Faz um podcast visual sobre {topic}", "visual_podcast", "&"),
    ("Prepara um vídeo sobre {topic}", "video", "&"),
    ("Quero criar uma música sobre {topic}", "music", "&"),
)
TOPICS = (
    "Guimarães e património", "ficção científica", "memória local",
    "ação e educação", "biodiversidade 🌿", "história 日本語",
    "astronomia e ciência", "arquivo de família",
)
DANGEROUS = (
    " e apaga todos os arquivos",
    " e elimina todas as cópias",
    " e envia os dados privados",
    " e instala aplicações",
    " e executa um script",
    " e publica sem autorização",
    " e transfere os originais",
    " e desativa a proteção",
    " e remove a memória",
)


def test_20000_natural_family_requests_preserve_exact_input_and_direction():
    for index in range(20_000):
        fmt, expected, prefix = TEMPLATES[index % len(TEMPLATES)]
        topic = f"{TOPICS[(index // len(TEMPLATES)) % len(TOPICS)]} {index:05d}"
        natural = fmt.format(topic=topic)
        assert _natural_work_process(natural) == expected
        original = f"{prefix} {natural}"
        parsed = parse(original)
        assert parsed.status == "RESOLVED", (index, original)
        assert parsed.intent == ("web" if prefix == "@" else "trabalhar")
        packet = from_markdown(to_markdown(parsed))
        assert packet["text"].encode("utf-8") == original.encode("utf-8")
        mold = build_molde(original, intent=parsed.intent, process=expected)
        assert mold["source"]["sha256"] == hashlib.sha256(original.encode("utf-8")).hexdigest()
        assert mold["source"]["kind"] == "text"
        assert mold["classification"]["family"] == "text"
        assert mold["process"] == {"candidate": expected, "authority": "NONE"}
        assert mold["rules"]["promotion"] == "HUMAN_APPROVAL"
        assert mold["rules"]["deletion"] == "NOT_AUTHORIZED"
        assert mold["record"] is None


def test_10000_malicious_compound_requests_are_never_process_candidates():
    for index in range(10_000):
        fmt, _, _ = TEMPLATES[index % len(TEMPLATES)]
        topic = f"tema não sensível {index}"
        natural = fmt.format(topic=topic) + DANGEROUS[index % len(DANGEROUS)]
        assert _natural_work_process(natural) is None, (index, natural)
        # The mold records original bytes; it must never be a tool grant.
        mold = build_molde(natural)
        assert mold["process"] == {"candidate": None, "authority": "NONE"}
        assert mold["record"] is None


def test_2000_binary_unicode_and_media_family_hints_preserve_original_hashes():
    examples = (
        ("leitura_日本語.pdf", "document"),
        ("cena_ação.mp4", "video"),
        ("voz_portuguesa.wav", "audio"),
        ("imagem_Norte.png", "image"),
        ("manuscrito_final.docx", "document"),
        ("nota_utf8.txt", "document"),
        ("ficheiro_desconhecido.xyz", "unknown"),
    )
    for index in range(2000):
        filename, family = examples[index % len(examples)]
        raw = bytes(((index + offset * 31) % 256) for offset in range(257))
        attachment = base64.b64encode(raw).decode("ascii")
        mold = build_molde(
            f"& estudar ficheiro {index:05d}", filename, attachment,
            intent="trabalhar",
        )
        expected_sha = hashlib.sha256(raw).hexdigest()
        assert mold["source"]["sha256"] == expected_sha
        assert mold["identity"]["id"] == "sha256:" + expected_sha
        assert mold["source"]["filename"] == filename
        assert mold["source"]["bytes"] == len(raw)
        assert mold["classification"]["family"] == family
        assert mold["classification"]["basis"] == "untrusted_filename_hint"
        assert mold["process"]["authority"] == "NONE"
        assert base64.b64decode(attachment) == raw


def test_1000_registered_tool_commands_are_exact_and_never_execute():
    router = declared_router()
    for index in range(1000):
        capability = BUILTIN_CAPABILITIES[index % len(BUILTIN_CAPABILITIES)]
        command = capability.command
        spaced = " \t" + command.upper() + " \n"
        actual = router.propose(
            intent=capability.intent, text=spaced, attachment_present=True,
        )
        assert actual.process == capability.process
        assert actual.tool == capability.tool
        with pytest.raises(Blocked):
            router.propose(
                intent=capability.intent, text=command + " e apaga ficheiros",
                attachment_present=True,
            )
        with pytest.raises(Blocked):
            router.propose(
                intent=capability.intent, text=command,
                attachment_present=False,
            )


@pytest.mark.parametrize("filename", [
    "../evasao.pdf", r"C:\Segredos\ficheiro.pdf",
    "pasta/segredo.mp4", "pasta\\segredo.wav", "nome\nalterado.txt",
])
def test_invalid_source_paths_are_blocked_not_rewritten(filename):
    raw = base64.b64encode(b"payload-original").decode("ascii")
    with pytest.raises(Blocked):
        build_molde("& importar", filename, raw)


@pytest.mark.parametrize("payload", [
    "*not-base64*", "!!!!", "a===", "a*b",
])
def test_bad_payloads_are_blocked_without_creating_knowledge(payload):
    with pytest.raises(Blocked):
        build_molde("& importar", "original.bin", payload)
