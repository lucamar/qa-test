from playwright.sync_api import Page
from .base_page import BasePage

class RegistrationPage(BasePage):
    URL = "https://qa-test-web-app.vercel.app/register.html"

    def __init__(self, page: Page):
        super().__init__(page)
        self.first_name_input = page.get_by_label("First Name")
        self.last_name_input = page.get_by_label("Last Name")
        self.email_input = page.get_by_label("Email Address")
        self.phone_input = page.get_by_label("Phone Number")
        self.street_input = page.get_by_label("Street Address")
        self.city_input = page.get_by_label("City")
        self.zip_input = page.get_by_label("ZIP Code")
        self.password_input = page.get_by_label("Password")
        self.confirm_password_input = page.get_by_label("Confirm Password")
        self.terms_checkbox = page.get_by_label("I agree to the Terms and Conditions")
        self.newsletter_checkbox = page.get_by_label("Subscribe to newsletter")
        self.register_button = page.get_by_role("button", name="Create Account")
        self.login_link = page.get_by_role("link", name="Already have an account? Login")

    def open(self):
        self.goto(self.URL)

    def fill_registration_form(
        self,
        first_name: str = "Hans",
        last_name: str = "Muster",
        email: str = "hans.muster@example.com",
        phone: str = "+385911234567",
        street: str = "Test Street 1",
        city: str = "Zagreb",
        zip_code: str = "10000",
        password: str = "Test1234!",
        confirm_password: str = "Test1234!",
        agree_terms: bool = True,
        subscribe_newsletter: bool = False,
    ):
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.email_input.fill(email)
        self.phone_input.fill(phone)
        self.street_input.fill(street)
        self.city_input.fill(city)
        self.zip_input.fill(zip_code)
        self.password_input.fill(password)
        self.confirm_password_input.fill(confirm_password)

        if agree_terms:
            self.terms_checkbox.check()
        else:
            self.terms_checkbox.uncheck()

        if subscribe_newsletter:
            self.newsletter_checkbox.check()
        else:
            self.newsletter_checkbox.uncheck()

    def submit(self):
        self.register_button.click()

    def go_to_login(self):
        self.login_link.click()

    def get_error_messages(self):
        # Adjust selector to match how errors are rendered
        return self.page.locator(".error, .validation-error").all_inner_texts()

    def get_success_message(self):
        # Adjust selector to match success UI
        return self.page.locator(".success, .alert-success").inner_text()
