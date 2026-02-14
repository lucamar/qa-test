1. Acceptance Criteria

Successful Registration

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

2. Manual Test Case

TC01 — Successful Registration

Preconditions: The user is on the Registration page

Steps:
- Enter valid data in all required fields
- Ensure "Terms and Conditions" checkbox is checked
- Click “Create Account”

Expected Result:
- Form submits successfully
- Browser redirects to: https://qa-test-web-app.vercel.app/index.html?registered=true

Actual Result:
- Redirect occurs as expected

Status: Passed

TC02 — Missing Required Fields

Steps:
- Leave all fields empty
- Click “Create Account”

Expected Result:
- Browser prevents form submission
- Native HTML5 tooltip appears on the first empty required field: “Please fill in this field”

Actual Result:
- Browser displays native HTML5 validation tooltip
- No custom validation messages appear in the DOM

Status: Passed

Notes:  
The application relies on HTML5 required‑field validation, not custom JavaScript validation. 
This is acceptable behavior and not a defect.

TC03 - Invalid email format

Steps:
- Enter valid data in all fields
- Insert invalid email (e.g.: invalid@email)
- Click “Create Account”

Expected Result:
- Browser prevents form submission
- A custom validation message should appear on the email field: e.g. “Please insert a valid email”

Actual Result:
- The form submission is accepted
- No custom validation messages appear

Status: Failed

TC04 - Password mismatch


The Password and Confirm Password fields share similar labels, causing strict‑mode ambiguity in Playwright. 
Selectors were updated to use unique placeholders to ensure reliable element targeting.

3. Automation Execution Summary

The automated test uses
```python
with page.expect_navigation(url="**/index.html?registered=true"):
    registration.submit()
```
This ensures Playwright waits for the redirect correctly.

Test Execution Table
Test Case	Description	Result
TC01	Successful registration	Passed
TC02	Missing required fields	Passed
TC03	Invalid email format	Failed (Bug‑001)
TC04	Password mismatch	Failed (Bug-002)
TC05	Terms not checked	Failed (Bug-003)
TC06	Invalid ZIP Code	Failed (Bug‑004)
TC07	Invalid Phone Number	Failed (Bug‑005)
TC08	Newsletter optional	Passed
TC09	Login link navigation	Passed

Execution Details
- Total tests executed: 9
    - Passed: 4
    - Failed: 5
    - Success test: Passed with correct redirect
- Execution time: ~12 seconds
- Browser: Chromium (headless)

4. Conclusion (Updated)

The registration feature correctly redirects users to the success page (index.html?registered=true) when all input data is valid. Automated testing confirms that the success flow works reliably when using proper navigation‑wait handling (expect_navigation).

However, several validation gaps remain (email, ZIP Code, phone number, pasword mismatch, terms not checked), which are documented as defects. The updated automation suite accurately reflects both HTML5 validation behavior and the redirect‑based success flow.
