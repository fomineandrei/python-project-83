import requests


def get_request(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
        return r.status_code
    except Exception:
        return None
