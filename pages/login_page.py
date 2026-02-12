from playwright.sync_api import Page
from .base_page import BasePage

class LoginPage(BasePage):
    URL = "https://qa-test-web-app.vercel.app/login.html"

    def __init__(self, page: Page):
        super().__init__(page)

    def is_loaded(self) -> bool:
        # Adjust selector to something unique on login page
        return self.page.get_by_role("heading", name="Login").is_visible()
