from typing import Dict, Optional
import re
from playwright.sync_api import Page, Locator, expect

TARGET_URL = "https://qa-test-web-app.vercel.app/register.html"


class RegisterPage:
    """
    Page Object Model for the registration page.
    Provides stable-id based locators and high-level actions/assertions.
    """

    def __init__(self, page: Page):
        self.page = page
        # form
        self.form: Locator = page.locator("form#registerForm")
        # inputs (stable IDs from provided HTML)
        self.locators = {
            "first_name": page.locator("#firstName"),
            "last_name": page.locator("#lastName"),
            "email": page.locator("#email"),
            "phone": page.locator("#phone"),
            "address": page.locator("#address"),
            "city": page.locator("#city"),
            "zip": page.locator("#zipCode"),
            "password": page.locator("#password"),
            "confirm_password": page.locator("#confirmPassword"),
            # checkboxes
            "terms": page.locator("#terms"),
            "newsletter": page.locator("#newsletter"),
            # CTA and messages
            "create_button": page.locator("button:has-text('Create Account')"),
            "login_link": page.locator("a:has-text('Already have an account? Login')"),
            "message": page.locator("#registerMessage"),
        }

        # placeholders and required expectations taken from provided HTML
        self.placeholders = {
            "first_name": "Enter your first name",
            "last_name": "Enter your last name",
            "email": "Enter your email",
            "phone": "Enter your phone number",
            "address": "Enter your street address",
            "city": "Enter your city",
            "zip": "Enter your ZIP code",
            "password": "Create a password",
            "confirm_password": "Confirm your password",
        }

        self.required_fields = {
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "city",
            "zip",
            "password",
            "confirm_password",
        }

    def goto(self) -> None:
        self.page.goto(TARGET_URL)
        expect(self.form).to_be_visible()

    def _one(self, key: str) -> Locator:
        """
        Ensure the locator resolves to exactly one element and return the first locator.
        """
        loc = self.locators[key]
        count = loc.count()
        assert count == 1, f"Locator for '{key}' resolved to {count} elements; expected exactly 1"
        return loc.first

    def assert_fields_present(self) -> None:
        """
        Assert all expected fields are present, visible, have expected placeholder/type/required attributes.
        """
        # ensure form visible
        expect(self.form).to_be_visible()

        # Check input fields
        for key, loc in self.locators.items():
            if key in ("create_button", "login_link", "message"):
                continue
            # Use _one to assert uniqueness
            single = self._one(key)
            expect(single).to_be_visible()

            # placeholders
            if key in self.placeholders:
                expected_ph = self.placeholders[key]
                actual_ph = single.get_attribute("placeholder") or ""
                assert (
                    actual_ph == expected_ph
                ), f"Placeholder for '{key}' expected '{expected_ph}' but found '{actual_ph}'"

            # required
            if key in self.required_fields:
                is_required = single.evaluate("el => !!el.required")
                assert is_required, f"Field '{key}' should be required"

        # Specific type assertions
        pw = self._one("password")
        cpw = self._one("confirm_password")
        assert (pw.get_attribute("type") or "").lower() == "password", "Password must be type='password'"
        assert (cpw.get_attribute("type") or "").lower() == "password", "Confirm Password must be type='password'"

        # Note: email & phone are type="text" in provided HTML
        email = self._one("email")
        assert (email.get_attribute("type") or "").lower() == "text", "Email expected to be type='text' per HTML"
        phone = self._one("phone")
        assert (phone.get_attribute("type") or "").lower() == "text", "Phone expected to be type='text' per HTML"

        # Check checkboxes are actually checkboxes
        terms = self._one("terms")
        newsletter = self._one("newsletter")
        assert (terms.get_attribute("type") or "").lower() == "checkbox", "Terms must be a checkbox"
        assert (newsletter.get_attribute("type") or "").lower() == "checkbox", "Newsletter must be a checkbox"

        # CTA and link presence
        create_btn = self._one("create_button")
        expect(create_btn).to_be_visible()
        login_link = self._one("login_link")
        expect(login_link).to_be_visible()

    def fill_field(self, key: str, value: str) -> None:
        loc = self._one(key)
        loc.fill(value)

    def fill_form(self, payload: Dict[str, str]) -> None:
        for key, value in payload.items():
            assert key in self.locators, f"Unknown field key '{key}'"
            # don't attempt to fill checkboxes or button keys
            if key in ("terms", "newsletter", "create_button", "login_link", "message"):
                continue
            self.fill_field(key, value)

    def check_terms(self) -> None:
        terms = self._one("terms")
        if not terms.is_checked():
            terms.check()

    def submit(self, timeout: int = 3000) -> Optional[object]:
        """
        Click Create Account and attempt to wait for navigation. Returns navigation info if navigation happened,
        otherwise returns None. Caller may inspect register message separately.
        """
        create_btn = self._one("create_button")
        try:
            with self.page.expect_navigation(timeout=timeout):
                create_btn.click()
            return True
        except Exception:
            # no navigation observed
            return None

    def get_message_text(self) -> str:
        msg = self._one("message")
        return (msg.text_content() or "").strip()

    def wait_for_message_non_empty(self, timeout: int = 5000) -> str:
        """
        Wait until #registerMessage has non-empty text and return it.
        Raises if timeout reached without content.
        """
        msg = self._one("message")
        expect(msg).to_have_text(re.compile(r"\S+"), timeout=timeout)
        return self.get_message_text()

    def form_is_valid(self) -> bool:
        return self.page.evaluate(
            """() => {
                const form = document.querySelector('#registerForm');
                return form ? form.checkValidity() : false;
            }"""
        )
