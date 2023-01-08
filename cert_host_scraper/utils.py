import re
from typing import Iterable, List


def strip_url(url: str) -> str:
    url = re.sub(r"https?://", "", url)
    url = re.sub(r"www.", "", url)
    return re.sub(r"/.*", "", url)


def divide_chunks(objects: list, size: int) -> Iterable[List[str]]:
    for i in range(0, len(objects), size):
        yield objects[i : i + size]
