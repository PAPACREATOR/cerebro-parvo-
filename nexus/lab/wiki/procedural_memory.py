"""Experimental procedural learning from human feedback and verified Wiki sources.

This is a suggestion index, NOT another runner, policy engine, or Store. No
imports in production Host/Kernel. It never dispatches tools, changes contracts,
promotes Creative, or teaches executable regexes. Learned examples remain
revocable by loss of their Store-verified source evidence.
"""
from __future__ import annotations

from difflib import SequenceMatcher
import hashlib
from pathlib import Path
import re
import unicodedata
import uuid

from nexus.capability_router import BUILTIN_CAPABILITIES, registered_router
from nexus.contracts import Blocked, strict_json
from nexus.lab.wiki.context_packet import raw_json
from nexus.store import atomic


# Families are hints derived from the original Folha mold, not MIME proofs.
# All candidate process names must already exist in the signed product registry.
FAMILY_TOOLS = {
    "text": ("verify", "interpret", "proofread", "book", "web", "podcast",
             "visual_podcast", "video", "music"),
    "document": ("verify", "interpret", "proofread", "convert_pdf", "book",
                 "web", "podcast", "visual_podcast", "video", "music"),
    "audio": ("verify", "podcast", "visual_podcast", "music"),
    "image": ("verify", "video", "visual_podcast"),
    "video": ("verify", "video", "visual_podcast"),
    "unknown": ("verify",),
}

# Initial candidates can be used before any experience. They are NOT runnable.
INITIAL_RECIPES = {
    "verify": ("verify",),
    "interpret": ("verify", "interpret"),
    "proofread": ("verify", "proofread"),
    "convert_pdf": ("verify", "convert_pdf"),
    "book": ("interpret", "proofread", "book"),
    "web": ("web",),
    "podcast": ("web", "interpret", "podcast"),
    "visual_podcast": ("interpret", "podcast", "visual_podcast"),
    "video": ("web", "interpret", "video"),
    "music": ("interpret", "music"),
}
MAX_STEPS = 8
MAX_EVENTS = 2048


def _digest(value):
    return hashlib.sha256(raw_json(value)).hexdigest()


def _normal(text):
    if type(text) is not str or not text.strip() or len(text) > 4000:
        raise Blocked("Frase de aprendizagem inválida.")
    if any(ord(ch) < 32 and ch not in "\n\r\t" for ch in text):
        raise Blocked("Frase de aprendizagem inválida.")
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text).casefold()).strip()


def _family(molde):
    """Check shape of a read-only mold, never treat its file suffix as fact."""
    if not isinstance(molde, dict) or molde.get("schema") != "nexus.molde.v1":
        raise Blocked("Molde de origem inválido.")
    try:
        family = molde["classification"]["family"]
        source = molde["source"]
        identity = molde["identity"]
        authority = molde["process"]["authority"]
        execution = molde["rules"]["execution"]
        promotion = molde["rules"]["promotion"]
        deletion = molde["rules"]["deletion"]
    except (KeyError, TypeError):
        raise Blocked("Molde incompleto.") from None
    if (type(family) is not str or family not in FAMILY_TOOLS
            or authority != "NONE" or execution != "HUMAN_CONFIRMATION"
            or promotion != "HUMAN_APPROVAL" or deletion != "NOT_AUTHORIZED"
            or not isinstance(source, dict) or not isinstance(identity, dict)
            or type(source.get("sha256")) is not str
            or not re.fullmatch(r"[0-9a-f]{64}", source["sha256"])
            or identity.get("id") != "sha256:" + source["sha256"]):
        raise Blocked("Molde não fiável.")
    return family


def _steps(family, goal, steps):
    registered_router()  # fail if runner/policy registry no longer agrees
    declared = {item.process for item in BUILTIN_CAPABILITIES}
    if type(goal) is not str or goal not in declared or goal not in FAMILY_TOOLS[family]:
        raise Blocked("Objetivo não pertence à família de capacidades.")
    if type(steps) is not list or not 1 <= len(steps) <= MAX_STEPS:
        raise Blocked("Passos fora dos limites.")
    if any(type(step) is not str or step not in declared
           or step not in FAMILY_TOOLS[family] for step in steps):
        raise Blocked("Flow não pode inventar ferramenta ou autoridade.")
    if steps[-1] != goal:
        raise Blocked("O passo final tem de corresponder ao objetivo.")
    return steps


def _product_terms(text):
    """Explicitly named product families only; never infer a capability."""
    labels = {
        "podcast": r"\bpodcasts?\b",
        "music": r"\b(?:m[uú]sicas?|can[cç][oõ]es?|can[cç][aã]o)\b",
        "video": r"\b(?:v[ií]deos?|filmes?|curtas?)\b",
        "book": r"\b(?:livros?|manuscritos?)\b",
        "pdf": r"\bpdf\b",
    }
    return {name for name, pattern in labels.items() if re.search(pattern, text)}


def _unsafe_hint_pair(requested, example):
    """Fail closed on negation or conflicting named deliverable.

    Similarity may correct 'podcst' but must never turn 'não fazer' into
    'fazer', or music into podcast. This guard changes hints ONLY and grants
    no authority to commands or tool execution.
    """
    negated = r"\b(?:n[aã]o|nunca|jamais|nem)\b"
    if re.search(negated, requested) or re.search(negated, example):
        return True
    requested_products = _product_terms(requested)
    example_products = _product_terms(example)
    return bool(requested_products and example_products
                and requested_products.isdisjoint(example_products))


class ProceduralMemory:
    """One independently auditable lab receipt per explicit operator review."""

    def __init__(self, wiki_bridge):
        self.bridge = wiki_bridge
        self.root = Path(wiki_bridge.root) / "procedural-memory"
        if self.root.is_symlink():
            raise Blocked("Memória processual redirecionada.")
        self.root.mkdir(exist_ok=True)

    def _events(self):
        entries = sorted(self.root.iterdir())
        if len(entries) > MAX_EVENTS:
            raise Blocked("Memória processual atingiu o limite.")
        for folder in entries:
            if (folder.is_symlink() or not folder.is_dir()
                    or not re.fullmatch(r"[0-9a-f]{32}", folder.name)):
                raise Blocked("Entrada processual desconhecida.")
            files = [folder / "event.json", folder / "manifest.json"]
            if any(p.is_symlink() or not p.is_file() for p in files):
                raise Blocked("Registo de aprendizagem incompleto.")
            try:
                manifest = strict_json(files[1].read_bytes())
                event = strict_json(files[0].read_bytes())
            except (OSError, ValueError, TypeError) as error:
                raise Blocked("Registo de aprendizagem ilegível.") from error
            if (not isinstance(manifest, dict) or set(manifest) != {"sha256"}
                    or manifest["sha256"] != _digest(event)):
                raise Blocked("Registo de aprendizagem adulterado.")
            self._validate(event)
            yield event

    def _validate(self, event):
        required = {"version", "kind", "authority", "family", "goal", "steps",
                    "phrase", "decision", "objective", "source_ids", "context_sha256"}
        if not isinstance(event, dict) or set(event) != required:
            raise Blocked("Registo processual inválido.")
        if (type(event["version"]) is not int or event["version"] != 1
                or event["kind"] != "LAB_HUMAN_REVIEWED_EXAMPLE"
                or event["authority"] != "NONE"
                or event["decision"] not in ("ACCEPT", "REJECT")
                or event["family"] not in FAMILY_TOOLS):
            raise Blocked("Autoridade ou versão processual inválida.")
        _steps(event["family"], event["goal"], event["steps"])
        _normal(event["phrase"])
        if (type(event["objective"]) is not str or not event["objective"].strip()
                or len(event["objective"]) > 500
                or type(event["source_ids"]) is not list
                or not 1 <= len(event["source_ids"]) <= 8):
            raise Blocked("Referências processuais inválidas.")
        if (type(event["context_sha256"]) is not str
                or not re.fullmatch(r"[0-9a-f]{64}", event["context_sha256"])):
            raise Blocked("Hash processual inválido.")
        # Re-read the live canonical Store evidence; do not trust a Wiki index.
        try:
            packet = self.bridge.prepare(event["objective"], event["source_ids"],
                                         include_creative=False)
        except (ValueError, KeyError, TypeError) as error:
            raise Blocked("Origem processual não verificável.") from error
        if _digest(packet) != event["context_sha256"]:
            raise Blocked("Fontes processuais mudaram.")

    def review(self, molde, *, goal, steps, phrase, source_ids, objective,
               decision, human_confirmed=False):
        """Store feedback, NOT an execution approval. Called only in isolated lab.

        human_confirmed is a local experimental assertion, not an identity
        or signed production approval. No production path imports this module.
        """
        family = _family(molde)
        _steps(family, goal, steps)
        _normal(phrase)
        if type(human_confirmed) is not bool or not human_confirmed:
            raise Blocked("Revisão humana da experiência obrigatória.")
        if decision not in ("ACCEPT", "REJECT"):
            raise Blocked("Decisão processual inválida.")
        if type(objective) is not str or not objective.strip() or len(objective) > 500:
            raise Blocked("Objetivo processual inválido.")
        packet = self.bridge.prepare(objective, source_ids, include_creative=False)
        # Canonical is necessary evidence, not a grant to use this learned flow.
        if any(s["authority"] != "canonical" for s in packet["sources"]):
            raise Blocked("Só exemplos canónicos verificados podem ensinar.")
        event = {
            "version": 1, "kind": "LAB_HUMAN_REVIEWED_EXAMPLE", "authority": "NONE",
            "family": family, "goal": goal, "steps": list(steps),
            "phrase": phrase, "decision": decision, "objective": objective,
            "source_ids": list(source_ids), "context_sha256": _digest(packet),
        }
        self._validate(event)
        # On a partial write, the uncommitted receipt cannot be read as learned.
        if len(list(self.root.iterdir())) >= MAX_EVENTS:
            raise Blocked("Memória processual atingiu o limite.")
        entry = self.root / uuid.uuid4().hex
        entry.mkdir()
        atomic(entry / "event.json", raw_json(event))
        atomic(entry / "manifest.json", raw_json({"sha256": _digest(event)}))
        return {"id": entry.name, "status": "LAB_RECORDED",
                "authority": "NONE", "execution": "NOT_AUTHORIZED"}

    def propose_correction(self, molde, *, goal, steps, failed_run_id,
                           verified_run_ids, original_phrase, corrected_phrase,
                           objective):
        """Observe a failed Store run and propose a NON-executable correction.

        This is not a repair of Host tools. Verified sources prove individual
        steps, NOT that a multi-step sequence has executed successfully.
        """
        family = _family(molde)
        _steps(family, goal, steps)
        if len(set(steps)) != len(steps):
            raise Blocked("Receita corrigida contém passos repetidos.")
        original = _normal(original_phrase)
        corrected = _normal(corrected_phrase)
        if original == corrected or _unsafe_hint_pair(original, corrected):
            raise Blocked("Correção de linguagem ambígua ou contraditória.")
        if type(objective) is not str or not objective.strip() or len(objective) > 500:
            raise Blocked("Objetivo de correção inválido.")
        if type(verified_run_ids) is not list or len(verified_run_ids) != len(steps):
            raise Blocked("Cada passo exige uma fonte canónica independente.")
        store = self.bridge.store
        failed = store.state(failed_run_id)
        store.check_input(failed)
        if (failed.get("status") not in ("FAIL", "BLOCKED")
                or failed.get("process_id") != goal
                or store.path("canonical", failed_run_id).exists()
                or failed_run_id in verified_run_ids):
            raise Blocked("A falha não é uma execução independente comprovada.")
        packet = self.bridge.prepare(objective, verified_run_ids, include_creative=False)
        if (len(packet["sources"]) != len(steps)
                or any(source["authority"] != "canonical"
                       or source["process_id"] != step
                       for source, step in zip(packet["sources"], steps))):
            raise Blocked("Os resultados não comprovam cada capacidade proposta.")
        candidate = {
            "version": 1, "kind": "LAB_CORRECTION_CANDIDATE",
            "authority": "NONE", "execution": "NOT_AUTHORIZED",
            "evidence_scope": "PER_STEP_ONLY",
            "goal": goal, "steps": list(steps),
            "original_phrase": original_phrase, "corrected_phrase": corrected_phrase,
            "objective": objective, "failed_run_id": failed_run_id,
            "failed_state_sha256": _digest(failed),
            "verified_run_ids": list(verified_run_ids),
            "verified_context_sha256": _digest(packet),
        }
        candidate["candidate_sha256"] = _digest(candidate)
        return candidate

    def review_correction(self, molde, candidate, *, human_confirmed=False):
        """Re-check live evidence, then record ONLY a human-reviewed hint.

        Never executes/retries a failed run, repairs a tool or grants a gate.
        """
        expected_keys = {"version", "kind", "authority", "execution",
                         "evidence_scope", "goal", "steps", "original_phrase",
                         "corrected_phrase", "objective", "failed_run_id",
                         "failed_state_sha256", "verified_run_ids",
                         "verified_context_sha256", "candidate_sha256"}
        if not isinstance(candidate, dict) or set(candidate) != expected_keys:
            raise Blocked("Proposta de correção inválida.")
        if (type(candidate["version"]) is not int or candidate["version"] != 1
                or candidate["kind"] != "LAB_CORRECTION_CANDIDATE"
                or candidate["authority"] != "NONE"
                or candidate["execution"] != "NOT_AUTHORIZED"
                or candidate["evidence_scope"] != "PER_STEP_ONLY"
                or candidate["candidate_sha256"] != _digest({
                    k: v for k, v in candidate.items() if k != "candidate_sha256"
                })):
            raise Blocked("Identidade de correção alterada.")
        fresh = self.propose_correction(
            molde, goal=candidate["goal"], steps=candidate["steps"],
            failed_run_id=candidate["failed_run_id"],
            verified_run_ids=candidate["verified_run_ids"],
            original_phrase=candidate["original_phrase"],
            corrected_phrase=candidate["corrected_phrase"],
            objective=candidate["objective"],
        )
        if fresh != candidate:
            raise Blocked("Evidências da correção mudaram.")
        if type(human_confirmed) is not bool:
            raise Blocked("Confirmação humana inválida.")
        if not human_confirmed:
            return {"status": "REVIEW_REQUIRED", "authority": "NONE",
                    "execution": "NOT_AUTHORIZED", "candidate_sha256": candidate["candidate_sha256"]}
        record = self.review(
            molde, goal=candidate["goal"], steps=candidate["steps"],
            phrase=candidate["corrected_phrase"],
            source_ids=candidate["verified_run_ids"], objective=candidate["objective"],
            decision="ACCEPT", human_confirmed=True,
        )
        return dict(record, evidence_scope="PER_STEP_ONLY",
                    candidate_sha256=candidate["candidate_sha256"])

    def suggest(self, molde, *, goal, phrase=None):
        """Rank bounded source-backed recipes and reusable initial templates."""
        family = _family(molde)
        if phrase is not None:
            _normal(phrase)
        _steps(family, goal, [goal])
        grouped = {}
        for event in self._events():
            if event["family"] != family or event["goal"] != goal:
                continue
            key = tuple(event["steps"])
            item = grouped.setdefault(key, {"accept": 0, "reject": 0, "refs": []})
            item["accept" if event["decision"] == "ACCEPT" else "reject"] += 1
            if event["decision"] == "ACCEPT":
                item["refs"].extend(event["source_ids"])

        initial = [step for step in INITIAL_RECIPES[goal] if step in FAMILY_TOOLS[family]]
        if not initial or initial[-1] != goal:
            initial = [goal]
        candidates = set(grouped) | {tuple(initial)}
        suggestions = []
        for steps in candidates:
            accepted = grouped.get(steps, {}).get("accept", 0)
            rejected = grouped.get(steps, {}).get("reject", 0)
            if rejected and rejected >= accepted:
                continue
            suggestions.append({
                "steps": list(steps), "origin": "LEARNED" if accepted else "INITIAL",
                "positive_examples": accepted, "negative_examples": rejected,
                "canonical_source_ids": list(dict.fromkeys(
                    grouped.get(steps, {}).get("refs", [])))[:8],
            })
        suggestions.sort(key=lambda x: (-x["positive_examples"] + x["negative_examples"],
                                        -x["positive_examples"], len(x["steps"]), x["steps"]))
        return {"kind": "LAB_FLOW_SUGGESTIONS", "authority": "NONE",
                "execution": "NOT_AUTHORIZED", "promotion": "NOT_AUTHORIZED",
                "family": family, "goal": goal, "candidates": suggestions[:8],
                "requires_human_review": True}

    def bind_wiki_candidate(self, molde, *, goal, source_ids, objective):
        """Link a learned/initial suggestion to the EXISTING Wiki flow v1 gate.

        Only the four processes explicitly accepted by Wiki flow v1 can produce
        a validated candidate here. Any other family/tool stays a suggestion,
        never an invented executor, workflow engine or bypass.
        """
        from nexus.lab.wiki.flow_proposal import ALLOWED_STEPS, propose, validate_proposal
        suggestions = self.suggest(molde, goal=goal)["candidates"]
        if not suggestions:
            raise Blocked("Não existe receita candidata confirmável.")
        steps = suggestions[0]["steps"]
        if any(step not in ALLOWED_STEPS for step in steps):
            raise Blocked("A Wiki v1 não suporta esta sequência; sem execução.")
        packet = self.bridge.prepare(objective, source_ids, include_creative=False)
        plan = propose(packet, steps)
        return validate_proposal(packet, plan)

    def recognise(self, molde, text):
        """Tolerant candidate retrieval, never auto-dispatch or executable regex."""
        family = _family(molde)
        normal = _normal(text)
        # A human-rejected recipe cannot survive solely through a fuzzy hint.
        # Keep evidence grouped by the exact registered process sequence.
        groups = {}
        for event in self._events():
            if event["family"] != family:
                continue
            key = (event["goal"], tuple(event["steps"]))
            group = groups.setdefault(key, {"accepted": [], "rejected": 0})
            if event["decision"] == "REJECT":
                group["rejected"] += 1
            else:
                group["accepted"].append(_normal(event["phrase"]))
        matches = {}
        for (goal, _steps), group in groups.items():
            accepted = group["accepted"]
            # Disagreement is unresolved; the human must review new evidence.
            if group["rejected"] >= len(accepted):
                continue
            for sample in accepted:
                if _unsafe_hint_pair(normal, sample):
                    continue
                ratio = SequenceMatcher(None, normal, sample, autojunk=False).ratio()
                if ratio >= 0.78:
                    matches[goal] = max(matches.get(goal, 0), ratio)
        return {"kind": "LAB_INTENT_HINTS", "authority": "NONE",
                "execution": "NOT_AUTHORIZED", "requires_human_review": True,
                "candidates": [{"goal": goal, "similarity": round(score, 3)}
                               for goal, score in sorted(matches.items(),
                                                          key=lambda x: (-x[1], x[0]))[:5]]}
