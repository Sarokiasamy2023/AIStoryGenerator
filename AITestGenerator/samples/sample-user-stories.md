# Sample User Stories

## 1. User Login Feature

**Title:** User Login Feature

**User Story:**
As a registered user, I want to log in to my account so that I can access my personalized dashboard and saved preferences.

**Acceptance Criteria:**
- User can log in with valid email and password
- System displays error message for invalid credentials
- Account locks after 5 failed login attempts
- User can reset password via email link
- Session expires after 30 minutes of inactivity
- Remember me option keeps user logged in for 30 days

---

## 2. Shopping Cart

**Title:** Shopping Cart Feature

**User Story:**
As a customer, I want to add items to my shopping cart so that I can purchase multiple items at once and review my order before checkout.

**Acceptance Criteria:**
- User can add items to cart from product page
- Cart displays total price and item count
- User can update item quantities
- User can remove items from cart
- Cart persists across browser sessions
- Maximum 10 items per product allowed
- Out of stock items cannot be added

---

## 3. Search Functionality

**Title:** Product Search Feature

**User Story:**
As a customer, I want to search for products by name or category so that I can quickly find what I'm looking for.

**Acceptance Criteria:**
- Search bar is visible on all pages
- Search returns results within 2 seconds
- Results are sorted by relevance
- User can filter results by price, rating, category
- Search suggests products as user types
- No results page shows helpful alternatives
- Search history is saved for logged-in users

---

## 4. Payment Processing

**Title:** Payment Processing Feature

**User Story:**
As a customer, I want to securely pay for my order using my credit card so that I can complete my purchase.

**Acceptance Criteria:**
- System accepts Visa, MasterCard, and American Express
- Payment information is encrypted
- User receives confirmation email after successful payment
- Failed payments display clear error messages
- User can save payment methods for future use
- 3D Secure authentication for international cards
- Payment timeout after 5 minutes of inactivity

---

## 5. User Registration

**Title:** User Registration Feature

**User Story:**
As a new visitor, I want to create an account so that I can save my preferences and track my orders.

**Acceptance Criteria:**
- Registration form requires email, password, and name
- Email must be unique and valid format
- Password must be at least 8 characters with 1 uppercase, 1 number
- User receives verification email
- Account is activated after email verification
- Social media login options available (Google, Facebook)
- Terms and conditions must be accepted

---

## 6. Order Tracking

**Title:** Order Tracking Feature

**User Story:**
As a customer, I want to track my order status so that I know when to expect delivery.

**Acceptance Criteria:**
- User can view order status on order history page
- Real-time tracking updates displayed
- Email notifications sent for status changes
- Estimated delivery date shown
- Tracking number provided for shipped orders
- User can view order details and items
- Support contact available for order issues

---

## 7. Product Reviews

**Title:** Product Review Feature

**User Story:**
As a customer, I want to read and write product reviews so that I can make informed purchase decisions and share my experience.

**Acceptance Criteria:**
- Only verified purchasers can write reviews
- Reviews include star rating (1-5) and text comment
- Reviews can include photos
- Users can edit/delete their own reviews
- Reviews are moderated before publishing
- Helpful/not helpful voting on reviews
- Sort reviews by date, rating, or helpfulness

---

## 8. Wishlist

**Title:** Wishlist Feature

**User Story:**
As a customer, I want to save items to a wishlist so that I can purchase them later.

**Acceptance Criteria:**
- User can add/remove items from wishlist
- Wishlist accessible from user account
- Email notification when wishlist item goes on sale
- User can move items from wishlist to cart
- Wishlist can be shared via link
- Maximum 50 items in wishlist
- Wishlist syncs across devices

---

## 9. Password Reset

**Title:** Password Reset Feature

**User Story:**
As a user who forgot my password, I want to reset it via email so that I can regain access to my account.

**Acceptance Criteria:**
- User can request password reset from login page
- Reset link sent to registered email
- Reset link expires after 1 hour
- New password must meet security requirements
- User receives confirmation email after reset
- Old password cannot be reused
- Account locked after 3 failed reset attempts

---

## 10. Notification Preferences

**Title:** Notification Preferences Feature

**User Story:**
As a user, I want to manage my notification preferences so that I only receive communications I'm interested in.

**Acceptance Criteria:**
- User can opt in/out of email notifications
- Separate controls for marketing, order updates, and account alerts
- SMS notification option available
- Push notification settings for mobile app
- Changes take effect immediately
- Unsubscribe link in all marketing emails
- Preference center accessible from account settings
