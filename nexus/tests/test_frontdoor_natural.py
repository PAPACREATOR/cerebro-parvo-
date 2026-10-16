"""L1/L2: natural-language and ambiguity matrix for the Front Door."""
import random

import pytest

from nexus.frontdoor import parse


VALID_TEMPLATES = {
    "arquivo": [
        "guarda {body}", "arquiva {body}", "salva {body}", "quero guardar {body}",
    ],
    "web": [
        "pesquisa na web {body}", "procura na internet {body}",
        "pesquisa online {body}", "pesquiza na net {body}",
    ],
    "fontes": [
        "encontra fontes sobre {body}", "procura fontes para {body}",
        "quais são as fontes de {body}", "pesquiza fontes sobre {body}",
    ],
    "trabalhar": [
        "trabalha este texto {body}", "revê {body}", "melhora {body}",
        "reescreve {body}", "corrige {body}",
    ],
    "perguntar": [
        "explica {body}", "responde sobre {body}", "o que é {body}",
        "quem é {body}", "como funciona {body}",
    ],
    "calcular": [
        "calcula {body}", "faz a conta {body}", "quanto é {body}",
        "soma {body}",
    ],
    "tema": [
        "tema {body}", "assunto {body}", "quero falar sobre {body}",
    ],
}


def test_l1_2000_natural_valid_cases():
    rng = random.Random(20261004)
    intents = tuple(VALID_TEMPLATES)
    alphabet = "abcxyz012345 áéç_日本語_-"
    for i in range(2000):
        intent = intents[i % len(intents)]
        template = VALID_TEMPLATES[intent][i % len(VALID_TEMPLATES[intent])]
        body = "".join(rng.choice(alphabet) for _ in range(10 + rng.randrange(40))).strip() or "conteúdo"
        original = template.format(body=body)
        parsed = parse(original)
        assert parsed.status == "RESOLVED", (i, original, parsed)
        assert parsed.intent == intent, (i, original, parsed)
        assert parsed.original == original
        assert parsed.parser == "eliza-rules-v1"
        assert parsed.explicit is False


def test_l2_1500_two_intent_cases_are_unresolved():
    rng = random.Random(4042026)
    intents = tuple(VALID_TEMPLATES)
    for i in range(1500):
        first = intents[i % len(intents)]
        second = intents[(i + 1 + rng.randrange(len(intents) - 1)) % len(intents)]
        if second == first:
            second = intents[(intents.index(first) + 1) % len(intents)]
        # Theme/subject rules are intentionally start-anchored to avoid
        # treating ordinary body words as commands. If theme was selected as
        # the second clause, swap the order so both intents remain detectable.
        if second == "tema" and first != "tema":
            first, second = second, first
        a = VALID_TEMPLATES[first][i % len(VALID_TEMPLATES[first])].format(body="documento alfa")
        b = VALID_TEMPLATES[second][i % len(VALID_TEMPLATES[second])].format(body="documento beta")
        original = a + " e também " + b
        parsed = parse(original)
        assert parsed.status == "UNRESOLVED", (i, first, second, original, parsed)
        assert parsed.intent is None
        assert parsed.original == original


@pytest.mark.parametrize("value", [
    "bom dia",
    "isto é só uma nota",
    "talvez amanhã",
    "não sei o que quero fazer",
    "um texto sem ordem",
    "Nexus",
    "olá mundo",
])
def test_l2_weak_or_chatty_text_is_unresolved(value):
    parsed = parse(value)
    assert parsed.status == "UNRESOLVED"
    assert parsed.intent is None


@pytest.mark.parametrize(("value", "intent"), [
    ("@@ pesquisa na web isto mas guarda como arquivo", "arquivo"),
    ("@ guarda isto depois mas pesquisa agora", "web"),
    ('"" calcula isto e encontra fontes', "fontes"),
    ("& pesquisa online isto e melhora o texto", "trabalhar"),
    ("?? guarda isto mas explica primeiro", "perguntar"),
    ("% procura fontes mas calcula 2+2", "calcular"),
    ("# pesquisa na internet mas o tema é astronomia", "tema"),
])
def test_explicit_prefix_has_priority_over_conflicting_natural_language(value, intent):
    parsed = parse(value)
    assert parsed.status == "RESOLVED"
    assert parsed.intent == intent
    assert parsed.explicit is True
    assert parsed.parser == "prefix-v1"


def test_natural_parser_never_changes_original_bytes():
    value = "  Explica ação 日本語 ç  "
    parsed = parse(value)
    assert parsed.original.encode("utf-8") == value.encode("utf-8")


@pytest.mark.parametrize("original", [
    "Explica como guardar um ficheiro.",
    "Explica como pesquisar na web.",
    "Explica como calcular o custo.",
    "Por favor, explica como arquivar uma nota.",
    "Explica-me como guardar este documento.",
])
def test_portuguese_question_clause_not_subordinate_command(original):
    parsed = parse(original)
    assert parsed.status == "RESOLVED"
    assert parsed.intent == "perguntar"
    assert parsed.original == original
    assert parsed.explicit is False
    assert "process" not in parsed.as_dict()


@pytest.mark.parametrize("original", [
    "Explica como guardar e depois guarda a nota.",
    "Explica como pesquisar na web e depois pesquisa na web.",
    "Explica como calcular e calcula o resultado.",
    "Explica como guardar e depois corrige o documento.",
    "Não expliques como guardar esta nota.",
    'O texto diz «explica como guardar a nota».',
])
def test_portuguese_clause_does_not_mask_second_action_or_negation(original):
    parsed = parse(original)
    assert parsed.status == "UNRESOLVED"
    assert parsed.intent is None
    assert parsed.original == original


@pytest.mark.parametrize(("original", "intent"), [
    ("Podes guardar este documento?", "arquivo"),
    ("Guarde este ficheiro.", "arquivo"),
    ("Quero que guardes esta nota.", "arquivo"),
    ("Por favor, arquive este original.", "arquivo"),
    ("Poderias pesquisar na internet?", "web"),
    ("Gostaria de pesquisar na net.", "web"),
    ("Procure fontes sobre geografia.", "fontes"),
    ("Encontre fontes de história.", "fontes"),
    ("Reveja este parágrafo.", "trabalhar"),
    ("Corrija esta frase.", "trabalhar"),
    ("Explique este conceito.", "perguntar"),
    ("Calcule o total.", "calcular"),
    ("Como posso pesquisar na web?", "perguntar"),
    ("Podes explicar como guardar este ficheiro?", "perguntar"),
    ("De que forma posso calcular o valor?", "perguntar"),
])
def test_pt_operational_lexicon_and_clause_grammar(original, intent):
    parsed = parse(original)
    assert parsed.status == "RESOLVED"
    assert parsed.intent == intent
    assert parsed.original.encode("utf-8") == original.encode("utf-8")
    assert parsed.explicit is False
    assert "process" not in parsed.as_dict()


@pytest.mark.parametrize("original", [
    "Não podes guardar esta nota.",
    "Nunca guardes esta nota.",
    "Explica como guardar e depois guarda o documento.",
    "Como guardar e também tema astronomia.",
    "Podes explicar como pesquisar e depois pesquisa na web.",
    "O texto diz «guarde o ficheiro».",
    "A palavra guarde surge na frase.",
])
def test_pt_operational_lexicon_cannot_force_an_action(original):
    parsed = parse(original)
    assert parsed.status == "UNRESOLVED"
    assert parsed.intent is None
    assert parsed.original == original


@pytest.mark.parametrize("original", [
    "Responde sobre documento alfa e também pesquiza fontes sobre documento beta.",
    "Como funciona documento alfa e também quais são as fontes de documento beta?",
    "Como guardar uma nota e depois guarde o ficheiro.",
    "Podes explicar como pesquisar e depois pesquise na internet.",
    "Quero que guardes o texto e também arquive outro documento.",
])
def test_pt_lexicon_grammar_preserves_distinct_clauses_and_inflections(original):
    parsed = parse(original)
    assert parsed.status == "UNRESOLVED"
    assert parsed.intent is None
    assert parsed.original == original


def test_pt_markdown_fts5_lexicon_grammar_is_local_and_read_only():
    from nexus.frontdoor import _PT_LANGUAGE_DB, _PT_GRAMMAR, _PT_FORM_INTENTS, _pt_lookup
    assert len(_PT_FORM_INTENTS) >= 60
    assert "pergunta_inicio" in _PT_GRAMMAR
    assert "segunda_acao" in _PT_GRAMMAR
    assert _PT_LANGUAGE_DB.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='pt_operational'"
    ).fetchone() is not None
    assert _pt_lookup("guarde") == ("arquivo",)
    assert _pt_lookup("pesquise") == ("web",)
    assert _pt_lookup("revê") == ("trabalhar",)
    assert _pt_lookup('guarde" OR 1=1 --') == ()
    assert _pt_lookup("canonico") == ()


def test_pt_markdown_is_digest_bound_to_the_host_sealed_frontdoor():
    import hashlib
    from nexus.frontdoor import _PT_LANGUAGE_PATH, _PT_LANGUAGE_SHA256
    assert hashlib.sha256(_PT_LANGUAGE_PATH.read_bytes()).hexdigest() == _PT_LANGUAGE_SHA256


@pytest.mark.parametrize(("text", "expected"), [
    ("Guarde este ficheiro.", "arquivo"),
    ("Como posso guardar esta nota?", "perguntar"),
    ("De que forma posso calcular o preço?", "perguntar"),
    ("Poderias pesquisar na internet?", "web"),
    ("Encontre fontes de história.", "fontes"),
    ("Corrija esta frase.", "trabalhar"),
])
def test_pt_regex_plus_fts5_vs_command_head_baseline(text, expected):
    parsed = parse(text)
    assert parsed.status == "RESOLVED"
    assert parsed.intent == expected
    assert parsed.original == text


@pytest.mark.parametrize("text", [
    "Não podes guardar esta nota.",
    "Explica como guardar e depois guarda o original.",
    "Como guardar e também pesquisa na web.",
    'A palavra "guarde" aparece na frase.',
])
def test_pt_fts5_presence_never_overrides_negation_or_two_actions(text):
    assert parse(text).status == "UNRESOLVED"
