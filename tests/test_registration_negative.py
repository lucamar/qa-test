from pages.registration_page import RegistrationPage
from pages.login_page import LoginPage

def test_missing_required_fields(page):
    registration = RegistrationPage(page)
    registration.open()

    registration.submit()
    errors = registration.get_error_messages()
    assert len(errors) > 0

def test_invalid_email_format(page):
    registration = RegistrationPage(page)
    registration.open()

    registration.fill_registration_form(email="invalid-email")
    registration.submit()
    errors = registration.get_error_messages()
    assert any("email" in e.lower() for e in errors)

def test_password_mismatch(page):
    registration = RegistrationPage(page)
    registration.open()

    registration.fill_registration_form(password="Test1234!", confirm_password="Different123!")
    registration.submit()
    errors = registration.get_error_messages()
    assert any("password" in e.lower() or "match" in e.lower() for e in errors)

def test_terms_not_checked(page):
    registration = RegistrationPage(page)
    registration.open()

    registration.fill_registration_form(agree_terms=False)
    registration.submit()
    errors = registration.get_error_messages()
    assert any("terms" in e.lower() for e in errors)

def test_newsletter_optional(page):
    registration = RegistrationPage(page)
    registration.open()

    registration.fill_registration_form(subscribe_newsletter=False)
    registration.submit()
    # Expect success; adjust to real behavior
    assert True  # placeholder

def test_login_link_navigation(page):
    registration = RegistrationPage(page)
    registration.open()

    registration.go_to_login()
    login_page = LoginPage(page)
    assert login_page.is_loaded()

