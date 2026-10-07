import pytest
from cerebro.persistence import RecoverableMarkdownWriter, PersistenceError, RecoveryRequired

def W(tmp_path): return RecoverableMarkdownWriter(tmp_path/"state"/"cerebro.sqlite3",tmp_path/"vault")

def test_write_creative(tmp_path):
    w=W(tmp_path); r=w.write("op1","CREATIVE","project/a.md","# A\n")
    assert r.state=="COMMITTED"
    assert (tmp_path/"vault"/"creative"/"project"/"a.md").read_text()=="# A\n"
    assert w.reconcile("op1")=="COMMITTED"

def test_idempotent(tmp_path):
    w=W(tmp_path); a=w.write("op1","CREATIVE","a.md","same"); b=w.write("op1","CREATIVE","a.md","same")
    assert a.expected_hash==b.expected_hash and b.state=="COMMITTED"

def test_operation_reuse_diff_payload_rejected(tmp_path):
    w=W(tmp_path); w.write("op1","CREATIVE","a.md","one")
    with pytest.raises(RecoveryRequired): w.write("op1","CREATIVE","a.md","two")

def test_existing_different_target_rejected(tmp_path):
    w=W(tmp_path); p=tmp_path/"vault"/"creative"/"a.md"; p.parent.mkdir(parents=True); p.write_text("old")
    with pytest.raises(RecoveryRequired): w.write("op1","CREATIVE","a.md","new")

def test_crash_after_prepared_resume(tmp_path):
    w=W(tmp_path)
    with pytest.raises(RuntimeError): w.write("op1","CREATIVE","a.md","payload",failpoint="after_prepared")
    assert w.reconcile("op1")=="NOT_COMMITTED"
    assert w.resume("op1").state=="COMMITTED"
    assert (tmp_path/"vault"/"creative"/"a.md").read_text()=="payload"

def test_crash_after_replace_reconcile(tmp_path):
    w=W(tmp_path)
    with pytest.raises(RuntimeError): w.write("op1","CREATIVE","a.md","payload",failpoint="after_replace")
    assert w.reconcile("op1")=="COMMITTED"

def test_committed_missing_requires_recovery(tmp_path):
    w=W(tmp_path); w.write("op1","CREATIVE","a.md","payload"); (tmp_path/"vault"/"creative"/"a.md").unlink()
    assert w.reconcile("op1")=="RECOVERY_REQUIRED"
    with pytest.raises(RecoveryRequired): w.resume("op1")

def test_prepared_divergent_requires_recovery(tmp_path):
    w=W(tmp_path)
    with pytest.raises(RuntimeError): w.write("op1","CREATIVE","a.md","payload",failpoint="after_prepared")
    p=tmp_path/"vault"/"creative"/"a.md"; p.parent.mkdir(parents=True); p.write_text("evil")
    assert w.reconcile("op1")=="RECOVERY_REQUIRED"

def test_canonical_same_writer_separate_domain(tmp_path):
    w=W(tmp_path); w.write("op-c","CANONICAL","x.md","approved")
    assert (tmp_path/"vault"/"canonical"/"x.md").read_text()=="approved"
    assert not (tmp_path/"vault"/"creative"/"x.md").exists()

@pytest.mark.parametrize("path",["../escape.md","x/../../escape.md"])
def test_escape_rejected(tmp_path,path):
    w=W(tmp_path)
    with pytest.raises(PersistenceError): w.write("op","CREATIVE",path,"x")

import subprocess, sys
from pathlib import Path

def _run_hard_crash(tmp_path, point):
    script = f"""
from pathlib import Path
from cerebro.persistence import RecoverableMarkdownWriter
root=Path({str(tmp_path)!r})
w=RecoverableMarkdownWriter(root/'state'/'cerebro.sqlite3', root/'vault')
w.write('op-hard','CREATIVE','a.md','payload',hard_crashpoint={point!r})
"""
    return subprocess.run([sys.executable, '-c', script], cwd=str(Path(__file__).parents[1]))

def test_real_process_crash_after_prepared_is_recoverable(tmp_path):
    r=_run_hard_crash(tmp_path, 'after_prepared')
    assert r.returncode == 97
    w=W(tmp_path)
    assert w.reconcile('op-hard') == 'NOT_COMMITTED'
    assert w.resume('op-hard').state == 'COMMITTED'

def test_real_process_crash_after_replace_reconciles(tmp_path):
    r=_run_hard_crash(tmp_path, 'after_replace')
    assert r.returncode == 98
    w=W(tmp_path)
    assert w.reconcile('op-hard') == 'COMMITTED'


def test_symlink_escape_is_blocked_without_writing_outside(tmp_path):
    outside=tmp_path/"outside"
    outside.mkdir()
    link=tmp_path/"vault"/"creative"/"link"
    link.parent.mkdir(parents=True,exist_ok=True)
    try:
        link.symlink_to(outside,target_is_directory=True)
    except OSError as error:
        pytest.skip(f"symlink unavailable in this environment: {error}")
    w=W(tmp_path)
    with pytest.raises(PersistenceError,match="path escapes domain root"):
        w.write("op-symlink","CREATIVE","link/escape.md","payload")
    assert list(outside.iterdir()) == []


def test_same_operation_concurrent_processes_remain_idempotent(tmp_path):
    worker = """
from pathlib import Path
import sys
from cerebro.persistence import RecoverableMarkdownWriter
root=Path(sys.argv[1])
w=RecoverableMarkdownWriter(root/'state'/'cerebro.sqlite3',root/'vault')
receipt=w.write('op-concurrent','CREATIVE','same.md','payload')
assert receipt.state == 'COMMITTED'
"""
    processes=[
        subprocess.Popen(
            [sys.executable,"-c",worker,str(tmp_path)],
            cwd=str(Path(__file__).parents[1]),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for _ in range(8)
    ]
    results=[process.communicate(timeout=30) + (process.returncode,) for process in processes]
    failures=[result for result in results if result[2] != 0]
    assert failures == []
    w=W(tmp_path)
    assert w.reconcile("op-concurrent") == "COMMITTED"
    assert (tmp_path/"vault"/"creative"/"same.md").read_text() == "payload"


def test_after_replace_crash_leaves_prepared_until_reconcile(tmp_path):
    r=_run_hard_crash(tmp_path,"after_replace")
    assert r.returncode == 98
    import sqlite3
    con=sqlite3.connect(tmp_path/"state"/"cerebro.sqlite3")
    try:
        row=con.execute(
            "SELECT state FROM materializations WHERE operation_id=?",
            ("op-hard",),
        ).fetchone()
    finally:
        con.close()
    assert row == ("PREPARED",)
    assert (tmp_path/"vault"/"creative"/"a.md").read_bytes() == b"payload"
    w=W(tmp_path)
    assert w.reconcile("op-hard") == "COMMITTED"


def test_committed_tamper_requires_recovery(tmp_path):
    w=W(tmp_path)
    w.write("op-tamper","CREATIVE","a.md","original")
    target=tmp_path/"vault"/"creative"/"a.md"
    target.write_text("alterado",encoding="utf-8")
    assert w.reconcile("op-tamper") == "RECOVERY_REQUIRED"
    with pytest.raises(RecoveryRequired):
        w.resume("op-tamper")


def test_real_permission_denial_does_not_commit(tmp_path):
    import os
    if os.name == "nt":
        pytest.skip("POSIX chmod test; Windows ACL proof is a separate physical gate")
    w=W(tmp_path)
    parent=tmp_path/"vault"/"creative"
    parent.mkdir(parents=True,exist_ok=True)
    parent.chmod(0o500)
    try:
        with pytest.raises(PermissionError):
            w.write("op-denied","CREATIVE","denied.md","payload")
    finally:
        parent.chmod(0o700)
    assert w.reconcile("op-denied") == "NOT_COMMITTED"
    assert not (parent/"denied.md").exists()
