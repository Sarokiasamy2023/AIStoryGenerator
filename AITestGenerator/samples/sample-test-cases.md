# Sample Test Cases

## User Login Feature

### Positive Test Cases

**TC001: Verify successful login with valid credentials**
- **Type:** Positive
- **Priority:** High
- **Description:** Verify that a user can successfully log in with valid email and password
- **Preconditions:**
  - User account exists in the system
  - User is on the login page
- **Expected Result:** User is redirected to dashboard and session is created

**TC002: Verify "Remember Me" functionality**
- **Type:** Positive
- **Priority:** Medium
- **Description:** Verify that selecting "Remember Me" keeps user logged in across sessions
- **Preconditions:**
  - User has valid credentials
  - "Remember Me" checkbox is available
- **Expected Result:** User remains logged in after closing and reopening browser

**TC003: Verify successful password reset**
- **Type:** Positive
- **Priority:** High
- **Description:** Verify that user can reset password using email link
- **Preconditions:**
  - User account exists
  - Email service is functional
- **Expected Result:** User receives reset email and can set new password

### Negative Test Cases

**TC004: Verify login fails with invalid email**
- **Type:** Negative
- **Priority:** High
- **Description:** Verify that login fails when invalid email is provided
- **Preconditions:**
  - User is on login page
- **Expected Result:** Error message "Invalid email or password" is displayed

**TC005: Verify login fails with incorrect password**
- **Type:** Negative
- **Priority:** High
- **Description:** Verify that login fails when incorrect password is provided
- **Preconditions:**
  - Valid email is entered
  - Incorrect password is entered
- **Expected Result:** Error message displayed and login attempt is logged

**TC006: Verify account lockout after failed attempts**
- **Type:** Negative
- **Priority:** High
- **Description:** Verify that account is locked after 5 consecutive failed login attempts
- **Preconditions:**
  - Valid user account exists
- **Expected Result:** Account is locked and user receives notification email

**TC007: Verify login with empty credentials**
- **Type:** Negative
- **Priority:** Medium
- **Description:** Verify that login fails when email or password fields are empty
- **Preconditions:**
  - User is on login page
- **Expected Result:** Validation error messages displayed for empty fields

### Edge Cases

**TC008: Verify session timeout after inactivity**
- **Type:** Edge
- **Priority:** Medium
- **Description:** Verify that user session expires after 30 minutes of inactivity
- **Preconditions:**
  - User is logged in
  - No activity for 30 minutes
- **Expected Result:** User is logged out and redirected to login page

**TC009: Verify login with special characters in password**
- **Type:** Edge
- **Priority:** Low
- **Description:** Verify that passwords with special characters are handled correctly
- **Preconditions:**
  - User password contains special characters (!@#$%^&*)
- **Expected Result:** Login succeeds with correct special character password

**TC010: Verify concurrent login sessions**
- **Type:** Edge
- **Priority:** Medium
- **Description:** Verify behavior when user logs in from multiple devices simultaneously
- **Preconditions:**
  - User has valid credentials
  - Multiple devices available
- **Expected Result:** System handles concurrent sessions according to business rules

---

## Shopping Cart Feature

### Positive Test Cases

**TC011: Verify adding item to cart**
- **Type:** Positive
- **Priority:** High
- **Description:** Verify that user can successfully add an item to shopping cart
- **Preconditions:**
  - User is on product page
  - Product is in stock
- **Expected Result:** Item is added to cart and cart count increases

**TC012: Verify updating item quantity in cart**
- **Type:** Positive
- **Priority:** High
- **Description:** Verify that user can update quantity of items in cart
- **Preconditions:**
  - Cart contains at least one item
- **Expected Result:** Quantity is updated and total price recalculated

**TC013: Verify removing item from cart**
- **Type:** Positive
- **Priority:** High
- **Description:** Verify that user can remove items from cart
- **Preconditions:**
  - Cart contains items
- **Expected Result:** Item is removed and cart total is updated

### Negative Test Cases

**TC014: Verify adding out of stock item to cart**
- **Type:** Negative
- **Priority:** High
- **Description:** Verify that out of stock items cannot be added to cart
- **Preconditions:**
  - Product is marked as out of stock
- **Expected Result:** Error message displayed and item not added to cart

**TC015: Verify exceeding maximum quantity limit**
- **Type:** Negative
- **Priority:** Medium
- **Description:** Verify that user cannot add more than 10 items of same product
- **Preconditions:**
  - Cart already has 10 items of a product
- **Expected Result:** Error message displayed and quantity not increased

**TC016: Verify cart with invalid product ID**
- **Type:** Negative
- **Priority:** Low
- **Description:** Verify system handles invalid product IDs gracefully
- **Preconditions:**
  - Attempt to add non-existent product
- **Expected Result:** Error message displayed and cart remains unchanged

### Edge Cases

**TC017: Verify cart persistence across sessions**
- **Type:** Edge
- **Priority:** Medium
- **Description:** Verify that cart items persist when user logs out and logs back in
- **Preconditions:**
  - User has items in cart
  - User logs out and logs back in
- **Expected Result:** Cart items are preserved

**TC018: Verify cart with price changes**
- **Type:** Edge
- **Priority:** High
- **Description:** Verify that cart reflects price changes made after items were added
- **Preconditions:**
  - Items in cart
  - Product price is changed by admin
- **Expected Result:** Cart shows updated price with notification to user

**TC019: Verify empty cart behavior**
- **Type:** Edge
- **Priority:** Low
- **Description:** Verify that empty cart displays appropriate message
- **Preconditions:**
  - Cart has no items
- **Expected Result:** "Your cart is empty" message displayed with link to continue shopping
