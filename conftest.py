import pytest
from playwright.sync_api import Page
from pages.register_page import RegisterPage

@pytest.fixture
def register_page(page: Page) -> RegisterPage:
    """
    Provides a RegisterPage instance for tests. Tests should call register_page.goto()
    to navigate to the page before interacting with it.
    """
    return RegisterPage(page)
