from urllib.parse import urlparse

from app.config import settings


class WebPolicyError(Exception):
    pass


def allowlist_domains() -> set[str]:
    return {d.strip().lower() for d in settings.web_allowlist_domains.split(',') if d.strip()}


def can_access_url(url: str) -> bool:
    mode = settings.web_access_mode
    if mode == 'offline':
        return False
    if mode == 'open':
        return True

    domain = urlparse(url).netloc.lower()
    allowed = allowlist_domains()
    return any(domain == a or domain.endswith(f'.{a}') for a in allowed)


def enforce_url_access(url: str):
    if not can_access_url(url):
        raise WebPolicyError(f'URL blocked by policy: {url}')
