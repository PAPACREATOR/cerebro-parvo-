"""Host storage and explicit human gate. No automatic promotion API."""
import base64
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from nexus.approval_binding import HumanDecision, promotion_allowed
from nexus.contracts import Blocked, ROOT, load_policy, strict_json, validate


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def atomic(path, data):
    path = Path(path)
    raw = data if isinstance(data, bytes) else json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".pending-")
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


class Store:
    def __init__(self, path):
        self.root = Path(path).resolve()
        self.policy = load_policy()
        self.lock = threading.RLock()
        for directory in ("runs", "creative", "canonical"):
            target = self.root / directory
            if target.is_symlink() or target.is_junction():
                raise Blocked("Diretório de dados redirecionado.")
            target.mkdir(parents=True, exist_ok=True)
        for item in (self.root / "runs").glob("*/state.json"):
            state = strict_json(item.read_bytes())
            final = self.path("canonical", state["run_id"])
            if final.exists() or state["status"] == "PASS":
                try:
                    self.check_commit(state)
                    state.update(status="PASS", commit_status="COMMITTED", message="Guardado como aprovado.")
                except (OSError, ValueError, KeyError, TypeError):
                    state.update(status="BLOCKED", commit_status="RECOVERY_REQUIRED",
                                 message="A gravação aprovada precisa de reconciliação. Conteúdo conservado.")
                state["updated_at"] = now()
                atomic(item, state)
            elif state["status"] == "RUNNING":
                state.update(status="FAIL", message="Execução interrompida. Podes iniciar um novo pedido.", updated_at=now())
                atomic(item, state)

    def check_commit(self, state):
        """Verify an existing approval package; never create a new human decision."""
        run_id = state["run_id"]
        final = self.path("canonical", run_id)
        for name in ("content.md", "approval.json", "provenance.json"):
            if (final / name).is_symlink():
                raise Blocked("Pacote aprovado redirecionado.")
        content = (final / "content.md").read_bytes()
        approval = strict_json((final / "approval.json").read_bytes())
        provenance = strict_json((final / "provenance.json").read_bytes())
        if (digest(content) != state["candidate_sha256"]
                or approval["sha256"] != digest(content)
                or approval["run_id"] != run_id
                or approval["destination"] != "canonical"
                or approval["action"] != "APPROVE"
                or not approval["approval_id"] or not approval["actor"]
                or provenance["run_id"] != run_id
                or provenance["human_approval"] != approval
                or {"path": "canonical/" + run_id + "/content.md", "sha256": digest(content)}
                   not in provenance["output_references"]):
            raise Blocked("Pacote aprovado incoerente.")
        decision = HumanDecision(approval["approval_id"], approval["actor"], run_id, approval["sha256"], "APPROVE")
        if not promotion_allowed(decision, run_id, digest(content)):
            raise Blocked("Aprovação inválida.")

    def path(self, area, run_id):
        if area not in ("runs", "creative", "canonical") or not isinstance(run_id, str) or not re.fullmatch(r"[0-9a-f]{32}", run_id):
            raise Blocked("Referência inválida.")
        target = self.root / area / run_id
        if target.is_symlink() or target.is_junction() or not target.resolve().is_relative_to(self.root / area):
            raise Blocked("Destino inválido.")
        return target

    def state(self, run_id):
        return strict_json((self.path("runs", run_id) / "state.json").read_bytes())

    def update(self, run_id, **fields):
        with self.lock:
            value = self.state(run_id)
            value.update(fields, updated_at=now())
            atomic(self.path("runs", run_id) / "state.json", value)
            return value

    def create(self, request):
        validate("request", request)
        try:
            content = base64.b64decode(request["attachment"], validate=True) if request["attachment"] else request["text"].encode("utf-8")
        except (ValueError, UnicodeError) as error:
            raise Blocked("Anexo inválido.") from error
        if not content or len(content) > self.policy["max_input_bytes"]:
            raise Blocked("Escreve texto ou anexa um ficheiro até 2 MB.")
        if request["process"] not in self.policy["processes"]:
            raise Blocked("Processo não autorizado.")
        name = request["filename"] or "Texto escrito"
        if any(ord(c) < 32 for c in name) or "/" in name or "\\" in name:
            raise Blocked("Nome de anexo inválido.")
        run_id = uuid.uuid4().hex
        directory = self.path("runs", run_id)
        directory.mkdir()
        atomic(directory / "input.bin", content)
        atomic(directory / "request.json", request)
        atomic(directory / "state.json", {
            "run_id": run_id, "process_id": request["process"], "process_version": "1.0.0",
            "title": name, "status": "RUNNING", "created_at": now(), "updated_at": now(),
            "message": "A executar o processo.", "input_sha256": digest(content),
        })
        return run_id

    def accept(self, run_id, result, trace):
        validate("result", result)
        with self.lock:
            state = self.state(run_id)
            if state["status"] != "RUNNING":
                raise Blocked("A execução já terminou.")
            if state["process_id"] == "verify" and result["ai_calls"] != 0:
                raise Blocked("IA proibida neste processo.")
            candidate = self.path("creative", run_id)
            candidate.mkdir()
            content = result["markdown"].encode("utf-8")
            atomic(candidate / "content.md", content)
            atomic(candidate / "result.json", result)
            provenance = {
                "run_id": run_id, "process_id": state["process_id"], "process_version": state["process_version"],
                "step_id": "receive-validated-result", "timestamp": now(), "status": result["status"],
                "input_references": [{"path": "runs/" + run_id + "/input.bin", "sha256": state["input_sha256"]}],
                "output_references": [{"path": "creative/" + run_id + "/content.md", "sha256": digest(content)}],
                "tools": [e["capability"] for e in result["evidence"]], "execution": trace,
                "laws_sha256": digest((ROOT / "laws/CONSTITUTION.md").read_bytes()),
                "policy_sha256": digest((ROOT / "laws/policy.json").read_bytes()),
                "human_approval": None,
            }
            atomic(candidate / "provenance.json", provenance)
            return self.update(run_id, status="HUMAN_REQUIRED" if result["status"] in ("PASS", "UNKNOWN") else result["status"],
                               result_status=result["status"], outcome=result["outcome"], candidate_sha256=digest(content),
                               message="Resultado candidato. A decisão de guardar como aprovado é tua.")

    def promote(self, run_id, decision, destination="canonical"):
        """Only called by the authenticated UI after explicit confirmation."""
        with self.lock:
            if type(decision) is not HumanDecision or destination != "canonical":
                raise Blocked("BLOCK: falta uma decisão humana válida para Canonical.")
            state = self.state(run_id)
            if state["status"] not in ("HUMAN_REQUIRED", "PASS"):
                raise Blocked("Este resultado não está disponível para aprovação.")
            candidate = self.path("creative", run_id)
            content = (candidate / "content.md").read_bytes()
            if digest(content) != state["candidate_sha256"]:
                raise Blocked("O candidato mudou depois da apresentação.")
            try:
                allowed = promotion_allowed(decision, run_id, digest(content))
            except (ValueError, TypeError) as error:
                raise Blocked("A decisão não corresponde a este conteúdo.") from error
            if not allowed:
                raise Blocked("BLOCK: aprovação humana obrigatória.")
            final = self.path("canonical", run_id)
            if final.exists():
                if (final / "content.md").read_bytes() != content:
                    raise Blocked("Conflito com conhecimento já aprovado.")
                self.check_commit(state)
                return self.update(run_id, status="PASS", commit_status="COMMITTED", message="Guardado como aprovado.")
            stage = Path(tempfile.mkdtemp(prefix=".approval-", dir=self.root / "canonical"))
            approval = {
                "approval_id": decision.decision_id, "actor": decision.actor_id,
                "run_id": run_id, "sha256": digest(content), "destination": destination,
                "action": decision.action, "timestamp": now(),
            }
            provenance = strict_json((candidate / "provenance.json").read_bytes())
            provenance["human_approval"] = approval
            provenance["output_references"].append({"path": "canonical/" + run_id + "/content.md", "sha256": digest(content)})
            try:
                atomic(stage / "content.md", content)
                atomic(stage / "approval.json", approval)
                atomic(stage / "provenance.json", provenance)
                os.rename(stage, final)
            finally:
                if stage.exists():
                    shutil.rmtree(stage)
            return self.update(run_id, status="PASS", commit_status="COMMITTED", message="Guardado como aprovado.")

    def delete(self, *_args, **_kwargs):
        raise Blocked("BLOCK: eliminação não disponibilizada neste protótipo.")
