import re


def strip_url(url: str) -> str:
    url = re.sub(r"https?://", "", url)
    url = re.sub(r"www.", "", url)
    return re.sub(r"/.*", "", url)
