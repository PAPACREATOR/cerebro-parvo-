from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEXT_SUFFIXES = {
    ".py", ".ps1", ".psm1", ".cmd", ".bat", ".md", ".txt", ".json",
    ".yml", ".yaml", ".toml", ".ini", ".cfg", ".xml", ".html", ".js", ".ts",
}
EXCLUDED_TOP_LEVEL = {".git"}
FORBIDDEN = "".join(chr(value) for value in (111, 108, 108, 97, 109, 97))
FORBIDDEN_TOKENS = (FORBIDDEN, "11434", "qwen3:4b", "nomic-embed-text")


def test_active_repository_has_no_forbidden_legacy_runtime_reference():
    violations = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        relative = path.relative_to(ROOT)
        if relative.parts and relative.parts[0] in EXCLUDED_TOP_LEVEL:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(lines, 1):
            folded = line.casefold()
            if any(token in folded for token in FORBIDDEN_TOKENS):
                violations.append(f"{relative}:{number}")
    assert violations == [], "forbidden legacy runtime references: " + ", ".join(violations)
