import socket
from unittest import TestCase

import requests
from requests.exceptions import SSLError

from cert_host_scraper.prober_error import ProbeStatus, probe_status


def _from_inner(inner: BaseException) -> requests.ConnectionError:
    """Build the exception chain `requests` constructs around a socket error."""
    try:
        try:
            raise inner
        except Exception:
            raise requests.ConnectionError("outer") from inner
    except requests.ConnectionError as exc:
        return exc


class TestProbeStatus(TestCase):
    def test_ssl_error(self):
        self.assertEqual(ProbeStatus.TLS_ERROR, probe_status(SSLError("bad cert")))

    def test_dns_error(self):
        exc = _from_inner(socket.gaierror(-2, "Name or service not known"))
        self.assertEqual(ProbeStatus.DNS_ERROR, probe_status(exc))

    def test_connection_refused(self):
        exc = _from_inner(ConnectionRefusedError(111, "Connection refused"))
        self.assertEqual(ProbeStatus.CONNECTION_REFUSED, probe_status(exc))

    def test_timeout_from_requires_timeout(self):
        self.assertEqual(ProbeStatus.TIMEOUT, probe_status(requests.Timeout()))

    def test_connect_timeout(self):
        self.assertEqual(ProbeStatus.TIMEOUT, probe_status(requests.ConnectTimeout()))

    def test_read_timeout(self):
        self.assertEqual(ProbeStatus.TIMEOUT, probe_status(requests.ReadTimeout()))

    def test_other(self):
        self.assertEqual(ProbeStatus.OTHER, probe_status(requests.RequestException()))

    def test_tls_error_wraps_timeout(self):
        """A TLS attempt timing out mid-handshake still reports timeout."""
        exc = _from_inner(TimeoutError("handshake timed out"))
        self.assertEqual(ProbeStatus.TIMEOUT, probe_status(exc))
