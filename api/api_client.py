"""Thin ReqRes API client.

Every outbound request is validated against an expected HTTP status code via
:func:`utils.assertions.assert_status_code` - response-code validation is
mandatory for every call.
"""

from __future__ import annotations

import allure
import requests

from config import settings
from utils.assertions import assert_status_code


class ApiClient:
    def __init__(self, base_url: str = settings.API_BASE_URL, timeout: int = settings.API_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(settings.API_HEADERS)

    @allure.step("{method} {path} (expect {expected})")
    def request(self, method: str, path: str, expected, **kwargs) -> requests.Response:
        url = f"{self.base_url}/{path.lstrip('/')}"
        response = self.session.request(method, url, timeout=self.timeout, **kwargs)
        assert_status_code(response, expected)
        return response

    def get(self, path: str, expected=200, **kwargs) -> requests.Response:
        return self.request("GET", path, expected, **kwargs)

    def post(self, path: str, expected=200, **kwargs) -> requests.Response:
        return self.request("POST", path, expected, **kwargs)

    def put(self, path: str, expected=200, **kwargs) -> requests.Response:
        return self.request("PUT", path, expected, **kwargs)

    def patch(self, path: str, expected=200, **kwargs) -> requests.Response:
        return self.request("PATCH", path, expected, **kwargs)

    def delete(self, path: str, expected=204, **kwargs) -> requests.Response:
        return self.request("DELETE", path, expected, **kwargs)
