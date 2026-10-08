"""A/B candidate only; not imported by the product before equivalence passes."""
import json
import os
import sys
from pathlib import Path

if __package__ in (None, ""):
    import importlib.util
    package_root = Path(__file__).absolute().parents[1]
    spec = importlib.util.spec_from_file_location(
        "nexus", package_root / "__init__.py", submodule_search_locations=[str(package_root)])
    package = importlib.util.module_from_spec(spec)
    sys.modules["nexus"] = package
    spec.loader.exec_module(package)

from nexus.contracts import Blocked, strict_json, validate

PROCESSES = frozenset({"verify", "interpret", "proofread", "convert_pdf", "video",
                       "podcast", "visual_podcast", "book", "music", "web"})


def _input(value):
    if os.name == "nt":
        from nexus.windows_sandbox import require_native_boundary
        require_native_boundary()
    path = Path(value)
    if (not path.is_absolute() or path.name != "input.bin" or not path.is_file()
            or path.is_symlink() or path.is_junction() or path.parent.is_junction()
            or path.parent.parent.name != "runs"
            or path.resolve().parent != path.parent.resolve()
            or (os.name == "nt" and path.parent.resolve() != Path.cwd().resolve())):
        raise Blocked("Input fora da área atribuída.")
    return path.resolve()


def _dispatch(process, path):
    if process == "verify":
        from nexus.adapters.verify_direct import execute
        return execute(path)["result"]
    if process == "interpret":
        from nexus.adapters.notebook import run
        return run(path)
    if process == "proofread":
        from nexus.adapters.languagetool import run
        return run(path)
    if process in ("convert_pdf", "book"):
        from nexus.adapters.office import run
        return run(path)
    if process in ("video", "podcast", "visual_podcast"):
        from nexus.adapters.product_routes import run_open_notebook
        return run_open_notebook(path, process)
    if process == "music":
        from nexus.adapters.product_routes import run_music
        return run_music(path)
    if process == "web":
        from nexus.adapters.product_routes import run_web
        return run_web(path)
    raise Blocked("Processo indisponível.")


def execute(process, input_path):
    if process not in PROCESSES:
        raise Blocked("Processo indisponível.")
    try:
        value = _dispatch(process, _input(input_path))
        raw = json.dumps(value, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
        if len(raw) > 1_000_000:
            raise Blocked("Resposta excede o limite Nexus.")
        return validate("result", strict_json(raw))
    except Blocked:
        raise
    except Exception as error:
        raise Blocked("Adapter falhou de forma controlada.") from error


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        print(json.dumps({"result": execute(*sys.argv[1:3])}, ensure_ascii=False))
    except Exception:
        print("Execução direta rejeitada.", file=sys.stderr)
        raise SystemExit(1)
