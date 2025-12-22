# Sample Test Steps

## TC001: Verify successful login with valid credentials

### Setup Steps
1. Ensure test user account exists in database
2. Clear browser cache and cookies
3. Navigate to application base URL

### Test Steps

**Step 1:**
- **Action:** Navigate to the login page
- **Test Data:** URL: https://example.com/login
- **Expected Result:** Login page is displayed with email and password fields

**Step 2:**
- **Action:** Enter valid email address in the email field
- **Test Data:** Email: testuser@example.com
- **Expected Result:** Email is entered successfully in the field

**Step 3:**
- **Action:** Enter valid password in the password field
- **Test Data:** Password: Test@123456
- **Expected Result:** Password is masked and entered successfully

**Step 4:**
- **Action:** Click the "Login" button
- **Test Data:** N/A
- **Expected Result:** System processes the login request

**Step 5:**
- **Action:** Verify redirection to dashboard
- **Test Data:** N/A
- **Expected Result:** User is redirected to dashboard page (URL: /dashboard)

**Step 6:**
- **Action:** Verify user session is created
- **Test Data:** N/A
- **Expected Result:** Session cookie is present and user name is displayed in header

**Step 7:**
- **Action:** Verify welcome message is displayed
- **Test Data:** N/A
- **Expected Result:** "Welcome back, Test User!" message is shown

### Teardown Steps
1. Log out from the application
2. Clear session data
3. Close browser

---

## TC004: Verify login fails with invalid email

### Setup Steps
1. Clear browser cache and cookies
2. Navigate to application base URL

### Test Steps

**Step 1:**
- **Action:** Navigate to the login page
- **Test Data:** URL: https://example.com/login
- **Expected Result:** Login page is displayed

**Step 2:**
- **Action:** Enter invalid email address
- **Test Data:** Email: invalidemail@notexist.com
- **Expected Result:** Email is entered in the field

**Step 3:**
- **Action:** Enter any password
- **Test Data:** Password: AnyPassword123
- **Expected Result:** Password is masked and entered

**Step 4:**
- **Action:** Click the "Login" button
- **Test Data:** N/A
- **Expected Result:** System attempts to process login

**Step 5:**
- **Action:** Verify error message is displayed
- **Test Data:** N/A
- **Expected Result:** Error message "Invalid email or password" is displayed in red

**Step 6:**
- **Action:** Verify user remains on login page
- **Test Data:** N/A
- **Expected Result:** User is not redirected and stays on login page

**Step 7:**
- **Action:** Verify no session is created
- **Test Data:** N/A
- **Expected Result:** No session cookie is present in browser

**Step 8:**
- **Action:** Verify failed attempt is logged
- **Test Data:** N/A
- **Expected Result:** Failed login attempt is recorded in system logs with timestamp and IP

### Teardown Steps
1. Clear browser data
2. Close browser

---

## TC011: Verify adding item to cart

### Setup Steps
1. User is logged in to the application
2. Navigate to products page
3. Ensure test product is in stock

### Test Steps

**Step 1:**
- **Action:** Navigate to a specific product page
- **Test Data:** Product ID: PROD-12345, Product Name: "Wireless Mouse"
- **Expected Result:** Product page is displayed with product details

**Step 2:**
- **Action:** Verify product availability
- **Test Data:** N/A
- **Expected Result:** "In Stock" label is visible and "Add to Cart" button is enabled

**Step 3:**
- **Action:** Note current cart count
- **Test Data:** N/A
- **Expected Result:** Cart icon shows current number of items (e.g., 0)

**Step 4:**
- **Action:** Click "Add to Cart" button
- **Test Data:** N/A
- **Expected Result:** Button shows loading state briefly

**Step 5:**
- **Action:** Verify success notification
- **Test Data:** N/A
- **Expected Result:** Success message "Item added to cart" is displayed

**Step 6:**
- **Action:** Verify cart count is updated
- **Test Data:** N/A
- **Expected Result:** Cart icon count increases by 1

**Step 7:**
- **Action:** Click on cart icon to view cart
- **Test Data:** N/A
- **Expected Result:** Cart page/modal opens

**Step 8:**
- **Action:** Verify item is present in cart
- **Test Data:** N/A
- **Expected Result:** Product "Wireless Mouse" is listed with quantity 1 and correct price

**Step 9:**
- **Action:** Verify cart total is calculated correctly
- **Test Data:** Product Price: $29.99
- **Expected Result:** Cart subtotal shows $29.99

### Teardown Steps
1. Clear cart
2. Log out from application

---

## TC006: Verify account lockout after failed attempts

### Setup Steps
1. Ensure test user account exists and is not locked
2. Clear browser cache
3. Navigate to login page

### Test Steps

**Step 1:**
- **Action:** Enter valid email address
- **Test Data:** Email: testuser@example.com
- **Expected Result:** Email is entered in the field

**Step 2:**
- **Action:** Enter incorrect password (Attempt 1)
- **Test Data:** Password: WrongPassword1
- **Expected Result:** Password is entered

**Step 3:**
- **Action:** Click Login button
- **Test Data:** N/A
- **Expected Result:** Error message "Invalid email or password" is displayed

**Step 4:**
- **Action:** Enter incorrect password (Attempt 2)
- **Test Data:** Password: WrongPassword2
- **Expected Result:** Password is entered

**Step 5:**
- **Action:** Click Login button
- **Test Data:** N/A
- **Expected Result:** Error message displayed with warning "4 attempts remaining"

**Step 6:**
- **Action:** Repeat with incorrect password (Attempts 3-4)
- **Test Data:** Passwords: WrongPassword3, WrongPassword4
- **Expected Result:** Error messages show decreasing attempt count

**Step 7:**
- **Action:** Enter incorrect password (Attempt 5 - final)
- **Test Data:** Password: WrongPassword5
- **Expected Result:** Password is entered

**Step 8:**
- **Action:** Click Login button
- **Test Data:** N/A
- **Expected Result:** Account lockout message displayed

**Step 9:**
- **Action:** Verify lockout message content
- **Test Data:** N/A
- **Expected Result:** Message states "Account locked due to multiple failed attempts. Please contact support or reset password."

**Step 10:**
- **Action:** Attempt login with correct password
- **Test Data:** Password: Test@123456 (correct password)
- **Expected Result:** Login is denied with account locked message

**Step 11:**
- **Action:** Verify lockout notification email is sent
- **Test Data:** N/A
- **Expected Result:** Email sent to testuser@example.com with subject "Account Security Alert"

**Step 12:**
- **Action:** Check database for account status
- **Test Data:** N/A
- **Expected Result:** User account status is set to "LOCKED" with timestamp

### Teardown Steps
1. Unlock test account via admin panel or database
2. Clear browser data
3. Verify account is unlocked for future tests

---

## TC017: Verify cart persistence across sessions

### Setup Steps
1. User is logged in
2. Cart is empty

### Test Steps

**Step 1:**
- **Action:** Add first item to cart
- **Test Data:** Product: "Laptop", Quantity: 1
- **Expected Result:** Item added successfully

**Step 2:**
- **Action:** Add second item to cart
- **Test Data:** Product: "Mouse", Quantity: 2
- **Expected Result:** Item added successfully

**Step 3:**
- **Action:** Verify cart contents
- **Test Data:** N/A
- **Expected Result:** Cart shows 2 products: Laptop (qty: 1), Mouse (qty: 2)

**Step 4:**
- **Action:** Note cart total amount
- **Test Data:** N/A
- **Expected Result:** Total amount is calculated and displayed (e.g., $1,059.97)

**Step 5:**
- **Action:** Log out from application
- **Test Data:** N/A
- **Expected Result:** User is logged out and redirected to home page

**Step 6:**
- **Action:** Close browser completely
- **Test Data:** N/A
- **Expected Result:** Browser is closed

**Step 7:**
- **Action:** Open browser again and navigate to application
- **Test Data:** URL: https://example.com
- **Expected Result:** Application home page is displayed

**Step 8:**
- **Action:** Log in with same credentials
- **Test Data:** Email: testuser@example.com, Password: Test@123456
- **Expected Result:** User is logged in successfully

**Step 9:**
- **Action:** Check cart icon count
- **Test Data:** N/A
- **Expected Result:** Cart icon shows 3 items (1 laptop + 2 mice)

**Step 10:**
- **Action:** Open cart to view contents
- **Test Data:** N/A
- **Expected Result:** Cart displays same items: Laptop (qty: 1), Mouse (qty: 2)

**Step 11:**
- **Action:** Verify cart total is same as before logout
- **Test Data:** N/A
- **Expected Result:** Total amount matches previous total ($1,059.97)

**Step 12:**
- **Action:** Verify item details are preserved
- **Test Data:** N/A
- **Expected Result:** Product names, prices, quantities, and images are all intact

### Teardown Steps
1. Clear cart
2. Log out
3. Clean up test data
