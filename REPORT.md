# Report

This document reports the outcome of manual and automated tests of the registration form at the URL:
- [https://qa-test-web-app.vercel.app/register.html](https://qa-test-web-app.vercel.app/register.html)

## Successful Registration

A user should be successfully registered when:
- All required fields are filled with valid data
- First Name and Last name contain letters only (not numbers)
- Email format is valid
- Password and Confirm Password match
- The "Terms and Conditions" checkbox is checked
- The form submits without HTML5 validation errors

Expected Behavior:  
After submission, the browser navigates to the success page with the query parameter `registered=true`: 
the application redirects to the page `index.html?registered=true`.

### Manual Tests

TC10 — Successful Registration

Preconditions: The user is on the Registration page

Steps:
- Enter valid data in all required fields
- Ensure "Terms and Conditions" checkbox is checked
- Click “Create Account”

Expected Result:
- Form submits successfully
- Browser redirects to [https://qa-test-web-app.vercel.app/index.html?registered=true](https://qa-test-web-app.vercel.app/index.html?registered=true)

Actual Result:
- Redirect occurs as expected

Status: Passed

--- 

TC11 — Missing Required Fields

Steps:
- Leave all fields empty
- Click “Create Account”

Expected Result:
- Browser prevents form submission
- An error message should appear: e.g. “Please fill in this field”

Actual Result:
- Browser displays native HTML5 validation tooltip
- No custom validation messages appear in the DOM

Status: Passed

Notes: The application relies on HTML5 required‑field validation, not custom JavaScript validation. 
This is an acceptable behaviour and not a defect.

---

TC12 — Duplicate email

Steps:
- Enter valid data in all required fields
- Fill in email with one already used
- Click “Create Account”

Expected Result:
- Browser prevents form submission
- Native HTML5 error appears on screen

Actual Result:
- Browser displays the error message: "User with this email already exists"

Status: Passed

---

TC01 - Invalid First Name format

Steps:
- Enter valid data in all fields
- Insert invalid First Name (e.g.: 'John123')
- Click “Create Account”

Expected Result:
- Browser prevents form submission
- An error message should appear: e.g. “Please insert a valid First Name”

Actual Result:
- The form submission is accepted
- No error message appears

Status: Failed

---

TC02 - Invalid Last Name format

Steps:
- Enter valid data in all fields
- Insert invalid Last Name (e.g.: 'Doe99$')
- Click “Create Account”

Expected Result:
- Browser prevents form submission
- An error message should appear: e.g. “Please insert a valid Last Name”

Actual Result:
- The form submission is accepted
- No error message appears

Status: Failed

---

TC03 - Invalid email format

Steps:
- Enter valid data in all fields
- Insert invalid email (e.g.: '<random>@email')
- Click “Create Account”

Expected Result:
- Browser prevents form submission
- An error message should appear: e.g. “Please insert a valid email”

Actual Result:
- The form submission is accepted
- No error message appears

Status: Failed

---

TC04 - Invalid phone number

Steps:
- Enter valid data in all fields
- Insert invalid phone number (e.g.: 'abcd-efg')
- Click “Create Account”

Expected Result:
- Browser prevents form submission
- An error message appears: e.g. “Please insert a valid phone number”

Actual Result:
- The form submission is accepted
- No error message appears

Status: Failed

---

TC05 - Invalid ZIP code

Steps:
- Enter valid data in all fields
- Insert invalid ZIP code (e.g.: '12ab')
- Click “Create Account”

Expected Result:
- Browser prevents form submission
- An error message should appear: e.g. “Please insert a valid ZIP code”

Actual Result:
- The form submission is accepted
- No errror message appears

Status: Failed

---

TC06 - Password mismatch

Steps:
- Enter valid data in all fields
- Insert mismatching strings in "Password" and "Confirm Password" 
- Click “Create Account”

Expected Result:
- Browser prevents form submission
- An error message should appear: e.g. “Passwords do not match”

Actual Result:
- The form submission is accepted
- No error message appears

Note: The Password and Confirm Password fields share similar labels, causing strict‑mode ambiguity in Playwright. 
Selectors were updated to use unique placeholders to ensure reliable element targeting.

---

TC08 - Subscribe to newsletter is optional

Steps:
- Enter valid data in all fields
- Leave checkbox "Subscribe to newsletter" unchecked
- Click “Create Account”

Expected Result:
- Form submits successfully
- Browser redirects to [https://qa-test-web-app.vercel.app/index.html?registered=true](https://qa-test-web-app.vercel.app/index.html?registered=true)

Actual Result:
- Redirect occurs as expected

Status: Passed

---

TC09 - Login link navigation

Steps:
- Click “Already have an account? Login”

Expected Result:
- Browser redirects to [https://qa-test-web-app.vercel.app/index.html](https://qa-test-web-app.vercel.app/index.html)

Actual Result:
- Redirect occurs as expected

Status: Passed

---

### Automated Tests

The automated tests use
```python
with rp.page.expect_navigation(timeout=3000, url=target_url):
```
This ensures Playwright waits for the redirect correctly.

### Test Execution

Test Case| Description | Results
--- | --- | ---
TC01|Invalid First Name format|Failed (Bug-1)
TC02|Invalid Last Name format|Failed (Bug-2)
TC03|Invalid email format|Failed (Bug‑3)
TC04|Invalid Phone Number|Failed (Bug‑4)
TC05|Invalid ZIP Code|Failed (Bug‑5)
TC06|Password mismatch|Failed (Bug-6)
TC07|Terms not checked|Failed (Bug-7)
TC08|Newsletter optional|Passed
TC09|Login link navigation|Passed
TC10|Successful registration|Passed
TC11|Missing required fields|Passed
TC12|Duplicate email detected|Passed

Execution Details
- Total tests executed: 12
    - Passed: 5
    - Failed: 7
    - Success test: Passed with correct redirect
- Execution time: ~ 40 seconds
- Browser: Chromium (headless)

The HTML report created by `pytest` is saved as artifact in the project and it can be inspected under the folder [reports](reports/).

### Conclusion

The registration feature correctly redirects users to the success page (index.html?registered=true) when all input data is valid. Automated testing confirms that the success flow works reliably when using proper navigation‑wait handling (expect_navigation).

However, several validation gaps remain:
- First and Last Name, email, ZIP Code, phone number are not checked
- Pasword mismatch is not detected on the form
- Terms and Conditions not checked is accepted

The issues above are documented as bugs from 1 to 7 in the table with the test cases. 
The automation suite accurately reflects both HTML5 validation behavior and the redirect‑based success flow.
