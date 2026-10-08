import hashlib
from pathlib import Path
import pytest
from cerebro.core import (
    ContractError, Policy, receive_file, validate_input,
    create_operation, create_attachment, quarantine, sha256_file
)

def ingest(path, qdir, max_bytes=20*1024*1024, accept_empty=True):
    r=receive_file(path)
    validate_input(r, Policy(max_input_bytes=max_bytes, accept_empty=accept_empty))
    op=create_operation(r)
    a=create_attachment(op,r)
    q=quarantine(a,qdir)
    h=sha256_file(q)
    return r,q,h

@pytest.mark.parametrize('name,data',[
    ('normal.txt', b'abc\n123'),
    ('vazio.bin', b''),
    ('unicode-ç-漢字.txt', 'Olá — café 漢字'.encode('utf-8')),
    ('binario.bin', bytes(range(256))*8),
])
def test_ingest_preserves_bytes_exactly(tmp_path,name,data):
    src=tmp_path/name; src.write_bytes(data)
    r,q,h=ingest(src,tmp_path/'q')
    assert r.byte_size == len(data)
    assert q.path.read_bytes() == data
    assert src.read_bytes() == data
    assert h.digest == hashlib.sha256(data).hexdigest()

def test_ingest_large_file_preserves_hash_and_bytes(tmp_path):
    data=(bytes(range(256))*32768)
    src=tmp_path/'large.bin'; src.write_bytes(data)
    _,q,h=ingest(src,tmp_path/'q')
    assert q.path.stat().st_size == len(data)
    assert q.path.read_bytes() == data
    assert h.digest == hashlib.sha256(data).hexdigest()

def test_receive_missing_file_fails_explicitly(tmp_path):
    with pytest.raises(ContractError, match='RECEIVE_FAILED'):
        receive_file(tmp_path/'missing.bin')

def test_empty_rejected_when_policy_disallows(tmp_path):
    src=tmp_path/'empty.bin'; src.write_bytes(b'')
    r=receive_file(src)
    with pytest.raises(ContractError, match='empty'):
        validate_input(r, Policy(max_input_bytes=1, accept_empty=False))
