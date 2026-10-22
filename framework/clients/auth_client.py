from playwright.sync_api import APIResponse

from framework.clients.base_client import BaseClient


class AuthClient(BaseClient):
    def login(self, email: str, password: str) -> APIResponse:
        """POST /users/login. Returns a TokenResponse on success."""
        return self.post("users/login", data={"email": email, "password": password})
