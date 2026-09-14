import enum
import socket

import requests
from requests.exceptions import SSLError


class ProbeStatus(str, enum.Enum):
    """Outcome of probing a URL's availability.

    Values are the JSON representation, so this doubles as the wire schema and
    stays enum-like in Python (membership testing, exhaustive match, repr).
    """

    DNS_ERROR = "dns"
    TLS_ERROR = "tls"
    CONNECTION_REFUSED = "refused"
    TIMEOUT = "timeout"
    OTHER = "other"


def _probe_error(status: requests.RequestException) -> ProbeStatus | None:
    """Map a probe failure to a :class:`ProbeStatus` without losing detail.

    ``requests`` reports every transport-level failure as one exception, so
    we unwrap its ``args`` down to the underlying ``urllib3`` exception to
    determine which link actually broke.
    """
    # `SSLError` is a `ConnectionError`: check before walking the cause chain.
    if isinstance(status, SSLError):
        return ProbeStatus.TLS_ERROR

    # `ConnectTimeout` subclasses `ConnectionError`, so classify before the
    # more general `Timeout` check. All three timeout variants are one verdict.
    if isinstance(
        status, (requests.ConnectTimeout, requests.ReadTimeout, requests.Timeout)
    ):
        return ProbeStatus.TIMEOUT

    current: BaseException | None = status
    while current is not None:
        current = current.__cause__ or current.__context__

        if isinstance(current, socket.gaierror):
            return ProbeStatus.DNS_ERROR
        if isinstance(current, ConnectionRefusedError):
            return ProbeStatus.CONNECTION_REFUSED
        if isinstance(current, TimeoutError):
            return ProbeStatus.TIMEOUT

    return ProbeStatus.OTHER


def probe_status(exc: requests.RequestException) -> ProbeStatus:
    """Public entry point for callers who already hold the exception."""
    return _probe_error(exc) or ProbeStatus.OTHER


__all__ = ["ProbeStatus", "probe_status"]
