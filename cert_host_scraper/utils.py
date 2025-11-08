import re
from collections.abc import Iterable


def strip_url(url: str) -> str:
    url = re.sub(r"https?://", "", url)
    url = re.sub(r"www.", "", url)
    return re.sub(r"/.*", "", url)


def divide_chunks(objects: list, size: int) -> Iterable[list[str]]:
    for i in range(0, len(objects), size):
        yield objects[i : i + size]
