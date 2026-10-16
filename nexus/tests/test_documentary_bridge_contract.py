"""Documentary lab bridge contracts; no cloud, model or GPU is executed."""
import base64
import importlib.util
import json
from pathlib import Path

import pytest

SOURCE = Path(__file__).resolve().parents[1] / "windows" / "documentary_bridge.py"
spec = importlib.util.spec_from_file_location("nexus_documentary_lab", SOURCE)
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


@pytest.mark.parametrize("url", [
    "https://127.0.0.1:5055/api/transformations/execute",
    "http://127.0.0.1:5055.evil.test/api/transformations/execute",
    "http://127.0.0.1:7861.evil.test/sdapi/v1/options",
    "http://127.0.0.1:5055@evil.test/sdapi/v1/options",
    "http://localhost:5055/api/transformations/execute",
    "http://127.0.0.1:5056/api/transformations/execute",
    "http://127.0.0.1:7861//evil.test/redirect",
    "http://127.0.0.1:7861/sdapi/v1/options#fragment",
])
def test_documentary_rejects_non_exact_local_origins(url):
    with pytest.raises(bridge.BridgeError, match="Non-local"):
        bridge.get_local_json(url)
    with pytest.raises(bridge.BridgeError, match="Non-local"):
        bridge.post_local_json(url, {"prompt": "not-executed"})


@pytest.mark.parametrize("url", [
    "http://127.0.0.1:5055/api/transformations/execute",
    "http://127.0.0.1:7861/sdapi/v1/options",
])
def test_documentary_accepts_only_the_two_declared_origins(url):
    bridge._ensure_local_url(url)


def storyboard():
    return {"title": "História local", "script": "Texto confirmado. " * 10,
            "scenes": [{"visual_prompt": "A small town, no text", "seconds": 8}
                       for _ in range(6)]}


def test_storyboard_rejects_invented_steps_oversized_scene_and_bad_duration():
    source = storyboard()
    assert len(bridge.validate_storyboard(source)["scenes"]) == 6
    source["scenes"][0]["seconds"] = True
    with pytest.raises(bridge.BridgeError):
        bridge.validate_storyboard(source)
    source = storyboard()
    source["scenes"][0]["unexpected_command"] = "rm -rf files"
    with pytest.raises(bridge.BridgeError):
        bridge.validate_storyboard(source)


def test_local_source_stays_unchanged_and_extends_only_explicit_brief(tmp_path):
    original = "Origem íntegra: ação 日本語.\n".encode("utf-8")
    path = tmp_path / "source.txt"
    path.write_bytes(original)
    text = bridge.load_source(path, "Filme documental de 4 minutos", 4)
    assert text.endswith(original.decode("utf-8"))
    assert "Approximately 4 minutes" in text
    assert path.read_bytes() == original


def test_single_forge_scene_candidate_per_authorized_storyboard_scene(tmp_path, monkeypatch):
    calls = []
    raw = b"\x89PNG\r\n\x1a\n" + b"\x00" * 1500

    def fake_get(url, **kwargs):
        assert url == "http://127.0.0.1:7861/sdapi/v1/options"
        return {"sd_model_checkpoint": "model-name"}

    def fake_post(url, payload, **kwargs):
        calls.append((url, payload))
        return {"images": [base64.b64encode(raw).decode("ascii")]}

    monkeypatch.setattr(bridge, "get_local_json", fake_get)
    monkeypatch.setattr(bridge, "post_local_json", fake_post)
    names = bridge.render_scene_images(storyboard(), tmp_path, "16:9")
    assert len(names) == 6
    assert len(calls) == 6
    assert all(url == "http://127.0.0.1:7861/sdapi/v1/txt2img" for url, _ in calls)
    assert all(payload["width"] == 768 and payload["height"] == 432
               and payload["batch_size"] == 1 for _, payload in calls)
    assert all(path.is_file() and path.read_bytes() == raw for path in names)


def test_product_bridge_is_non_authoritative_and_checks_artifact_path(tmp_path, monkeypatch):
    # Full CLI flow is tested without external services or false media claims.
    source = tmp_path / "source.txt"
    source.write_text("Fonte pública com proveniência intacta.", encoding="utf-8")
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    (runtime / "open-notebook-documentary.json").write_text(json.dumps({
        "base_url": bridge.OPEN_NOTEBOOK_BASE, "password": "local-only",
        "model_id": "test-model", "transformation_id": "test-transform",
    }), encoding="utf-8")
    (runtime / "moneyprinterturbo.json").write_text(json.dumps({
        "root": str(tmp_path), "uv": "test-only",
        "ffmpeg": "test-only", "commit": "test-only",
    }), encoding="utf-8")

    def fake_images(story, output, aspect):
        folder = output / "scenes"
        folder.mkdir()
        paths = []
        for i in range(6):
            p = folder / f"scene-{i + 1:02d}.png"
            p.write_bytes(b"IMAGE-MOCK")
            paths.append(p)
        return paths

    def fake_mpt(_config, _story, _scenes, output, _aspect, _audio=None):
        p = output / "documentary-candidate.mp4"
        p.write_bytes(b"FAKE-VIDEO-FOR-CONTRACT-ONLY" * 80)
        return p

    monkeypatch.setattr(bridge, "open_notebook_storyboard", lambda *_: storyboard())
    monkeypatch.setattr(bridge, "render_scene_images", fake_images)
    monkeypatch.setattr(bridge, "run_moneyprinter", fake_mpt)
    output = tmp_path / "candidate"
    monkeypatch.setattr(bridge.sys, "argv", ["documentary_bridge.py",
                        "--source", str(source), "--brief", "História local",
                        "--runtime", str(runtime), "--output", str(output)])
    assert bridge.main() == 0
    receipt = json.loads((output / "report.json").read_text())
    assert receipt["status"] == "PASS_CANDIDATE"
    assert receipt["authority"] == "NONE"
    assert receipt["canonical_write"] is False
    assert receipt["pipeline"] == ["open-notebook", "forge", "moneyprinterturbo", "ffmpeg"]
    assert receipt["video"]["sha256"] == bridge.sha256_bytes(
        (output / "documentary-candidate.mp4").read_bytes())
    assert source.read_text() == "Fonte pública com proveniência intacta."
    assert not (tmp_path / "canonical").exists()
