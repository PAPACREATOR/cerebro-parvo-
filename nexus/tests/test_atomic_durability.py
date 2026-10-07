"""Durability contract for atomic writes. Uses real filesystem operations; no I/O mocks."""
import inspect
import os

import pytest

import nexus.store as store_module


def test_atomic_preserves_exact_bytes_and_removes_pending_file(tmp_path):
    target = tmp_path / "state.bin"
    target.write_bytes(b"old")
    payload = bytes(range(256)) * 32

    store_module.atomic(target, payload)

    assert target.read_bytes() == payload
    assert list(tmp_path.glob(".pending-*")) == []


def test_atomic_routes_replacement_through_durable_boundary():
    source = inspect.getsource(store_module.atomic)
    assert "_durable_replace" in source, (
        "atomic() replaces the file but has no explicit durable replacement boundary "
        "for parent-directory persistence"
    )


@pytest.mark.skipif(os.name == "nt", reason="POSIX directory fsync contract")
def test_posix_parent_directory_fsync_is_real_filesystem_operation(tmp_path):
    sync = getattr(store_module, "_fsync_directory", None)
    assert sync is not None, "parent-directory fsync helper is missing"

    target = tmp_path / "value.bin"
    target.write_bytes(b"durable")
    sync(tmp_path)

    assert target.read_bytes() == b"durable"


@pytest.mark.skipif(os.name != "nt", reason="Windows write-through replacement contract")
def test_windows_write_through_replace_uses_real_filesystem(tmp_path):
    replace = getattr(store_module, "_windows_replace_write_through", None)
    assert replace is not None, "Windows write-through replacement helper is missing"

    source = tmp_path / "pending.bin"
    target = tmp_path / "final.bin"
    source.write_bytes(b"new")
    target.write_bytes(b"old")

    replace(source, target)

    assert not source.exists()
    assert target.read_bytes() == b"new"
    implementation = inspect.getsource(replace)
    assert "MOVEFILE_WRITE_THROUGH" in implementation
    assert "MOVEFILE_REPLACE_EXISTING" in implementation
