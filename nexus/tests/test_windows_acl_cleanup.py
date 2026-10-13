"""Cleanup regression on disposable ACLs; no child, profile or tool launch."""
import ctypes as C
import json
import os
from types import SimpleNamespace
import uuid

import pytest

from nexus.contracts import Blocked
from nexus.windows_sandbox import _API, ConfinedProcess, READ_EXECUTE


pytestmark = pytest.mark.skipif(os.name != "nt", reason="Native Windows ACLs")


def declarations(api):
    """Independent readers and restoration, usable against the old implementation."""
    from ctypes import wintypes as W
    signatures = {
        "GetAclInformation": (W.BOOL, [api.P, api.P, api.D, api.D]),
        "GetAce": (W.BOOL, [api.P, api.D, api.P]),
        "GetSecurityDescriptorControl": (W.BOOL, [api.P, api.P, api.P]),
    }
    reader = C.WinDLL("advapi32", use_last_error=True)
    for name, (result, arguments) in signatures.items():
        function = getattr(reader, name)
        function.restype, function.argtypes = result, arguments
    return reader


def read_acl(api, reader, path, own, other):
    acl, descriptor = api.P(), api.P()
    error = api.a.GetNamedSecurityInfoW(str(path), 1, 4, None, None,
                                       C.byref(acl), None, C.byref(descriptor))
    assert error == 0, error
    try:
        size = (api.D * 3)()
        assert reader.GetAclInformation(acl, C.byref(size), C.sizeof(size), 2)
        result = {"own": [], "other": [], "unrelated": []}
        for index in range(size[0]):
            ace = api.P()
            assert reader.GetAce(acl, index, C.byref(ace))
            header = C.string_at(ace, 4)
            raw = C.string_at(ace, int.from_bytes(header[2:4], "little"))
            group = "unrelated"
            if header[0] in (0, 1):
                sid = api.P(ace.value + 8)
                if own and api.a.EqualSid(sid, own):
                    group = "own"
                elif other and api.a.EqualSid(sid, other):
                    group = "other"
            result[group].append(raw.hex())
        return result
    finally:
        api.k.LocalFree(descriptor)


@pytest.fixture
def area(tmp_path):
    api = _API()
    reader = declarations(api)
    own, other = api.P(), api.P()
    for pointer in (own, other):
        name = "nexus-cleanup-regression-" + uuid.uuid4().hex
        assert api.u.DeriveAppContainerSidFromAppContainerName(name, C.byref(pointer)) >= 0
    root = tmp_path / "acl-area"
    root.mkdir()
    child = root / "child"
    child.mkdir()
    document = child / "source.txt"
    document.write_bytes(b"synthetic-original\x00\xff\n")
    paths = [root, child, document]
    saved = []
    events = []

    def record(phase, **values):
        events.append({"phase": phase, **values})
        with (tmp_path / "cleanup-evidence.json").open("w", encoding="utf-8") as stream:
            json.dump(events, stream, ensure_ascii=True, indent=2)
            stream.flush()
            os.fsync(stream.fileno())

    for path in paths:
        acl, descriptor = api.P(), api.P()
        assert api.a.GetNamedSecurityInfoW(str(path), 1, 4, None, None,
                                          C.byref(acl), None, C.byref(descriptor)) == 0
        control, revision = C.c_ushort(), api.D()
        assert reader.GetSecurityDescriptorControl(descriptor, C.byref(control), C.byref(revision))
        saved.append((path, acl, descriptor, control.value))
    baseline = {str(p): read_acl(api, reader, p, own, other) for p in paths}
    value = SimpleNamespace(api=api, reader=reader, own=own, other=other,
                            root=root, child=child, document=document, paths=paths,
                            record=record, baseline=baseline)
    record("baseline_saved", paths=len(paths))
    try:
        yield value
    finally:
        # Restore only the backed-up DACL of these three new test paths.
        # Never touch a parent, installed directory, profile or global policy.
        for path, acl, descriptor, control in saved:
            protection = 0x80000000 if control & 0x1000 else 0x20000000
            error = api.a.SetNamedSecurityInfoW(str(path), 1, 4 | protection,
                                               None, None, acl, None)
            assert error == 0, (str(path), error)
        restored = {str(p): read_acl(api, reader, p, value.own, other) for p in paths}
        for path in paths:
            # The baseline has neither synthetic SID; grouping is unchanged even
            # if close has already freed the own SID.
            assert restored[str(path)] == baseline[str(path)]
        assert document.read_bytes() == b"synthetic-original\x00\xff\n"
        assert sorted(p.relative_to(root).as_posix() for p in root.rglob("*")) == [
            "child", "child/source.txt"]
        record("baseline_restored", exact_acls=True, exact_source=True, extra_files=0)
        for _, _, descriptor, _ in saved:
            api.k.LocalFree(descriptor)
        if value.own:
            api.a.FreeSid(value.own)
        api.a.FreeSid(other)


def snapshot(area):
    return {str(path): read_acl(area.api, area.reader, path, area.own, area.other)
            for path in area.paths}


def test_close_removes_own_allow_and_deny_preserves_other_sid_and_source(area):
    api = area.api
    api.acl(area.root, area.other, READ_EXECUTE)
    api.acl(area.root, area.other, 2, mode=3)
    api.acl(area.root, area.own, READ_EXECUTE)
    api.acl(area.root, area.own, 2, mode=3)
    granted = snapshot(area)
    assert all(value["own"] and value["other"] for value in granted.values())
    area.record("allow_and_deny_granted", descendants=len(granted))
    process = ConfinedProcess.__new__(ConfinedProcess)
    process.api, process.sid = api, area.own
    process.job = process.process = None
    process.stdin = process.stdout = process.stderr = None
    process.handles, process.grants = [], [area.root]
    process.shallow_grants = set()
    process.created = process.locked = False
    try:
        process.close()
    finally:
        area.own = process.sid
    area.record("original_close_returned")
    # The freed SID is reconstructed only for reading the surviving ACLs.
    own_bytes = bytes.fromhex(granted[str(area.root)]["own"][0])[8:]
    own_buffer = C.create_string_buffer(own_bytes)
    comparison_sid = C.cast(own_buffer, api.P)
    after = {str(p): read_acl(api, area.reader, p, comparison_sid, area.other) for p in area.paths}
    assert all(not value["own"] for value in after.values())
    assert all(after[p]["other"] == granted[p]["other"] and
               after[p]["unrelated"] == granted[p]["unrelated"] for p in after)
    assert not process.grants and not process.shallow_grants and not process.sid
    process.close()
    repeated = {str(p): read_acl(api, area.reader, p, comparison_sid, area.other) for p in area.paths}
    assert repeated == after
    area.record("cleanup_verified", task_aces=0, other_aces_exact=True, idempotent=True)


@pytest.mark.parametrize("target", ["file", "shallow_directory"])
def test_direct_cleanup_is_idempotent_and_does_not_change_other_paths(area, target):
    api = area.api
    path = area.document if target == "file" else area.root
    api.acl(path, area.other, 2, mode=3, inherit=False)
    api.acl(path, area.own, READ_EXECUTE, inherit=False)
    api.acl(path, area.own, 2, mode=3, inherit=False)
    before = snapshot(area)
    assert before[str(path)]["own"] and before[str(path)]["other"]
    api.acl(path, area.own, 0, mode=4, inherit=False)
    after = snapshot(area)
    assert not after[str(path)]["own"]
    for item in before:
        assert after[item]["other"] == before[item]["other"]
        assert after[item]["unrelated"] == before[item]["unrelated"]
        if item != str(path):
            assert after[item] == before[item]
    api.acl(path, area.own, 0, mode=4, inherit=False)
    assert snapshot(area) == after
    area.record("direct_cleanup_verified", target=target, task_aces=0, idempotent=True)


@pytest.mark.parametrize("failed_api", ["GetAclInformation", "GetAce", "DeleteAce"])
@pytest.mark.parametrize("inherit", [True, False])
def test_native_api_failure_blocks_before_applying_acl(area, monkeypatch, failed_api, inherit):
    api = area.api
    api.acl(area.root, area.own, 2, mode=3, inherit=inherit)
    before = snapshot(area)
    original = api.a
    applied = []

    class Fault:
        def __getattr__(self, name):
            if name == failed_api:
                def fail(*_):
                    C.set_last_error(5)
                    return 0
                return fail
            if name in ("SetNamedSecurityInfoW", "SetSecurityInfo"):
                def apply(*args):
                    applied.append(name)
                    return getattr(original, name)(*args)
                return apply
            return getattr(original, name)

    with monkeypatch.context() as patch:
        patch.setattr(api, "a", Fault())
        with pytest.raises(Blocked, match="erro 5"):
            api.acl(area.root, area.own, 0, mode=4, inherit=inherit)
    assert applied == []
    assert snapshot(area) == before
    area.record("fault_blocked_before_apply", failed_api=failed_api, inherit=inherit,
                acl_unchanged=True, apply_calls=0)


def test_close_failure_requires_reconciliation_without_tool_or_profile(area, monkeypatch):
    api = area.api
    api.acl(area.root, area.own, 2, mode=3)
    before = snapshot(area)
    own_bytes = bytes.fromhex(before[str(area.root)]["own"][0])[8:]
    own_buffer = C.create_string_buffer(own_bytes)
    comparison_sid = C.cast(own_buffer, api.P)
    process = ConfinedProcess.__new__(ConfinedProcess)
    process.api, process.sid = api, area.own
    process.job = process.process = None
    process.stdin = process.stdout = process.stderr = None
    process.handles, process.grants = [], [area.root]
    process.shallow_grants = set()
    process.created = process.locked = False
    original = api.a

    class Fault:
        def __getattr__(self, name):
            if name == "GetAce":
                def fail(*_):
                    C.set_last_error(5)
                    return 0
                return fail
            return getattr(original, name)

    with monkeypatch.context() as patch:
        patch.setattr(api, "a", Fault())
        try:
            with pytest.raises(Blocked, match="reconciliação"):
                process.close()
        finally:
            area.own = process.sid
    still_present = {str(p): read_acl(api, area.reader, p, comparison_sid, area.other)
                     for p in area.paths}
    assert still_present == before
    api.acl(area.root, comparison_sid, 0, mode=4)
    recovered = {str(p): read_acl(api, area.reader, p, comparison_sid, area.other)
                 for p in area.paths}
    assert all(not value["own"] for value in recovered.values())
    area.record("close_failure_reconciled", failure_surfaced=True, task_aces=0,
                launched_processes=0, created_profiles=0)
