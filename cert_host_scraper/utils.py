from urllib.parse import urlsplit


def strip_url(url: str) -> str:
    parts = urlsplit(url if "://" in url else "//" + url)
    netloc = parts.netloc or parts.path.split("/", 1)[0]
    if netloc.lower().startswith("www."):
        netloc = netloc[4:]
    return netloc
