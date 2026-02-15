# Introduction

QA Test of the URL: https://qa-test-web-app.vercel.app/index.html

- Manual test of the existing fields on the registration form
- Confirm if the validations appear correctly
- Report what happens on successful registration
- Indicate if any bugs have already been noticed

The preferred automation language is Python with Playwright.

The registration form is available at the URL https://qa-test-web-app.vercel.app/register.html

The following fields are available in the form:
- First Name
- Last Name
- Email Address
- Phone Number
- Street Address
- City
- ZIP Code
- Password
- Confirm Password

Then two check boxes are present :
- I agree to the Terms and Conditions
- Subscribe to newsletter

Finally, there is the button "Create Account" and the link "Already have an account? Login"

## Test Coverage

Positive Scenario
- Successful registration with valid data
- Verified via redirect to index.html?registered=true

Negative Scenario
- Missing required fields
- Invalid First and Last Name format
- Invalid ZIP and phone number
- Invalid email format
- Password mismatch
- Terms & Conditions not checked
- Newsletter checkbox optional
- Navigation to Login page

Notes
- The test suite is designed to be stable, fast, and easy to extend.
- HTML5 validation behavior is intentionally respected and tested.

# Test Plan

The scope of testing covers the user registration process at the URL https://qa-test-web-app.vercel.app/register.html

This includes:
- Form field validation
- UI/UX behavior
- Error handling
- Successful account creation
- Links and checkboxes

Testing Types
- Functional testing
- Negative testing
- Usability checks
- Cross-browser testing (Chrome, Firefox, ...)
- Automated testing using Playwright

Test Environment
- Browser: Chrome (latest), Firefox (latest)
- OS: Ubuntu (Linux)
- Network: Standard broadband
- Tools: Playwright (Python), pytest, GitHub

Please check the [REPORT](REPORT.md) to view the outcome of the tests.
