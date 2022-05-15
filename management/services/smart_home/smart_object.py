from abc import ABC
from typing import Any, Mapping
from requests import Response

from .smart_request import SmartHomeRequest

from .smart_session import smart_home_session


class SmartHomeObject(ABC):
    """Abstract class that provides method for requesting SmartHome data"""

    def __init__(self, request: SmartHomeRequest = None):
        if request is None:
            request = SmartHomeRequest()
        self._request = request

    def _get_data(self, url: str) -> Mapping[str, Any]:
        with smart_home_session(self._request) as http:
            return http.get(url).json()

    def _push_data(self, url: str, data:Mapping[str, Any] = None) -> Response:
        data = data if data is not None else {}
        with smart_home_session(self._request) as http:
            return http.post(url, data=data)

    def _patch_data(self, url: str, data:Mapping[str, Any] = None) -> Response:
        data = data if data is not None else {}
        with smart_home_session(self._request) as http:
            return http.patch(url, data=data)
