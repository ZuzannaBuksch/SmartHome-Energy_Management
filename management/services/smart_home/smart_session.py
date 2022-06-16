from contextlib import contextmanager
from urllib.parse import urljoin

import requests
from requests_cache import CachedSession
from starlette.exceptions import HTTPException

from management.settings import SMART_HOME_URL

from .smart_request import SmartHomeRequest


def check_for_errors(response, *args, **kwargs):
    # return
    return response.raise_for_status()


@contextmanager
def smart_home_session(request: SmartHomeRequest = None) -> requests.Session:
    """
    Requests Session for Smart Home API - Context Manager.
    Provides prepared setting for Smart Home Requests Session.
    """
    try:
        headers = {"Authorization": f"token {request.token}"}
    except AttributeError:
        headers = {}
    finally:
        headers["Content-Type"] = "application/json"

    try:
        date_format = "%Y-%m-%d %H:%M:%S"
        params = {
            "start_date": request.start_date.strftime(date_format),
            "end_date": request.end_date.strftime(date_format),
        }
    except AttributeError:
        params = {}

    http = requests.Session()
    http.base_url = SMART_HOME_URL

    http.get = lambda *args, **kwargs: requests.Session.get(
        http,
        urljoin(http.base_url, args[0]),
        *args[1:],
        **kwargs,
        headers=headers,
        params=params,
    )
    http.post = lambda *args, **kwargs: requests.Session.post(
        http,
        urljoin(http.base_url, args[0]),
        *args[1:],
        **kwargs,
        headers=headers,
        params=params,
    )

    http.patch = lambda *args, **kwargs: CachedSession.patch(
        http,
        urljoin(http.base_url, args[0]),
        *args[1:],
        **kwargs,
        headers=headers,
        params=params,
    )

    # http.hooks["response"] = [check_for_errors]

    try:
        yield http
    except requests.exceptions.HTTPError as e:
        return HTTPException(
            status_code=e.response.status_code, detail=e.response.json()
        )
    finally:
        http.close()
