"""A synthetic peer must never share a listening Windows service's port."""
import os

import pytest

from nexus.tests.test_open_notebook_kernel_e2e import (
    OpenNotebookHandler, ReusableHTTPServer,
)


@pytest.mark.skipif(os.name != "nt", reason="Windows socket reuse semantics")
def test_peer_refuses_an_already_listening_port():
    first = ReusableHTTPServer(("127.0.0.1", 0), OpenNotebookHandler)
    try:
        with pytest.raises(OSError):
            second = ReusableHTTPServer(first.server_address, OpenNotebookHandler)
            second.server_close()
    finally:
        first.server_close()
