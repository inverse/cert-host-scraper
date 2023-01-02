import re


def strip_url(url: str) -> str:
    url = re.sub(r"https?://", "", url)
    return re.sub(r"www.", "", url)
