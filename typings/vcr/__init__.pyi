from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any, TypeVar

_F = TypeVar("_F", bound=Callable[..., Any])

class CassetteContextDecorator(AbstractContextManager[CassetteContextDecorator]):
    def __enter__(self) -> CassetteContextDecorator: ...
    def __exit__(self, *args: Any) -> None: ...
    def __call__(self, func: _F) -> _F: ...

class VCR:
    def __init__(self, **kwargs: Any) -> None: ...
    def use_cassette(
        self, path: str | None = None, **kwargs: Any
    ) -> CassetteContextDecorator: ...

def use_cassette(
    path: str | None = None, **kwargs: Any
) -> CassetteContextDecorator: ...
