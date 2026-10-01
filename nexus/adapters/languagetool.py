"""Local LanguageTool CLI; suggestions only, without AI or automatic edits."""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from nexus.contracts import Blocked, strict_json, validate
from nexus.adapters.notebook import prepare_source


def normalize(raw):
    value = strict_json(raw)
    validate("languagetool", value)
    if value["warnings"]["incompleteResults"]:
        raise Blocked("A revisão linguística ficou incompleta.")
    matches = value["matches"]
    lines = ["# Revisão de português", "", "Sugestões locais. O original não foi alterado.", ""]
    if not matches:
        lines.append("A ferramenta não encontrou alertas. Isso não garante que o texto esteja correto.")
    for match in matches[:30]:
        suggestions = ", ".join(item["value"] for item in match["replacements"][:5])
        lines.extend(["- " + match["message"], "  Trecho: " + match["context"]["text"]])
        if suggestions:
            lines.append("  Sugestões: " + suggestions)
    if len(matches) > 30:
        lines.append("Apresentados os primeiros 30 alertas; o diagnóstico completo foi conservado.")
    return {"status": "UNKNOWN", "outcome": "candidate", "title": "Revisão de português",
            "markdown": "\n".join(lines), "ai_calls": 0,
            "evidence": [{"capability": "languagetool.cli.pt-PT", "status": "UNKNOWN",
                          "value": json.dumps({"version": value["software"]["version"],
                                               "matches": len(matches),
                                               "diagnostic": "languagetool-output.json"})}]}


def run(input_path):
    source = Path(input_path)
    prepare_source(source.read_bytes())
    config = strict_json((source.parent / "languagetool.json").read_bytes())
    if not isinstance(config, dict) or set(config) != {"java", "jar"}:
        raise Blocked("Configuração LanguageTool inválida.")
    for key in ("java", "jar"):
        if not isinstance(config[key], str) or not Path(config[key]).is_absolute() or not Path(config[key]).is_file():
            raise Blocked("Java ou LanguageTool indisponível.")
    if Path(config["java"]).name.lower() != "java.exe" or Path(config["jar"]).name != "languagetool-commandline.jar":
        raise Blocked("Ferramenta não autorizada para revisão linguística.")
    # Stream to files so malformed/noisy tool output cannot fill Host memory.
    output = source.parent / "languagetool-output.json"
    with output.open("wb") as stdout, (source.parent / "languagetool.stderr.txt").open("wb") as stderr:
        try:
            result = subprocess.run([config["java"], "-Xmx512m", "-jar", config["jar"],
                                     "-l", "pt-PT", "-c", "utf-8", "--json", str(source)],
                                    stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                    timeout=45, creationflags=subprocess.CREATE_NO_WINDOW)
        except subprocess.TimeoutExpired:
            raise Blocked("A revisão linguística excedeu o tempo permitido.") from None
    if result.returncode != 0 or output.stat().st_size > 2_000_000:
        raise Blocked("A revisão linguística falhou ou devolveu dados excessivos.")
    return normalize(output.read_bytes())


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        print(json.dumps(run(sys.argv[1]), ensure_ascii=False))
    except Exception:
        print("Revisão linguística indisponível ou resposta rejeitada.", file=sys.stderr)
        raise SystemExit(1)
