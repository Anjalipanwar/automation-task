"""Thin wrapper around Playwright's APIRequestContext shared by all resource clients."""

from typing import Any

from playwright.sync_api import APIRequestContext, APIResponse

Headers = dict[str, str] | None


class BaseClient:
    def __init__(self, request: APIRequestContext) -> None:
        self._request = request

    @staticmethod
    def bearer(token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    def get(
        self, path: str, params: dict[str, Any] | None = None, headers: Headers = None
    ) -> APIResponse:
        return self._request.get(path, params=params, headers=headers)

    def post(self, path: str, data: Any = None, headers: Headers = None) -> APIResponse:
        return self._request.post(path, data=data, headers=headers)

    def put(self, path: str, data: Any = None, headers: Headers = None) -> APIResponse:
        return self._request.put(path, data=data, headers=headers)

    def patch(self, path: str, data: Any = None, headers: Headers = None) -> APIResponse:
        return self._request.patch(path, data=data, headers=headers)

    def delete(self, path: str, headers: Headers = None) -> APIResponse:
        return self._request.delete(path, headers=headers)
