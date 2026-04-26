# Test Scenarios: Shopping Cart for Online Bookstore

## POSITIVE CASES - Happy Path

### 1. Add Single Book to Empty Cart
**Given:** User is logged in with empty cart  
**When:** User clicks "Add to Cart" on a book with available stock  
**Then:**  
- Cart count increments to 1
- Book appears in cart with correct title, price, quantity (1)
- Subtotal displays correct amount
- API returns `200 OK` with updated cart object
- Session/cart token updated

### 2. Checkout Complete Flow with Valid Payment
**Given:** Cart contains 3 books, total $45.97  
**When:** User proceeds to checkout, enters valid shipping/billing, completes payment  
**Then:**  
- Order confirmation page displays with order ID
- Inventory decremented for all books
- Cart cleared (count = 0)
- Order status = "Pending Fulfillment"
- Payment gateway returns `201 Created`, order API returns `200 OK`

### 3. Apply Valid Discount Code
**Given:** Cart total is $50, valid coupon "BOOK20" gives 20% off  
**When:** User enters coupon code and clicks Apply  
**Then:**  
- Discount of $10 applied
- New total shows $40
- Coupon marked as used in user's account
- API returns `200 OK` with `discount_applied: true`

---

## NEGATIVE CASES - Invalid Inputs & Errors

### 1. Add Out-of-Stock Book to Cart
**Given:** Book inventory = 0  
**When:** User attempts to add book to cart  
**Then:**  
- Error message: "This book is currently unavailable"
- Cart count unchanged
- API returns `422 Unprocessable Entity` or `409 Conflict`
- No partial state created

### 2. Checkout with Expired/Invalid Payment Card
**Given:** Cart ready for checkout  
**When:** User enters card with expiry date in the past or fails Luhn check  
**Then:**  
- Payment declined message displayed
- Order NOT created
- Cart remains intact with items
- Payment gateway returns `402 Payment Required` or `400 Bad Request`
- No zombie orders in "pending" state

### 3. Apply Invalid/Expired Coupon Code
**Given:** User enters coupon "EXPIRED2023" that ended 6 months ago  
**When:** Coupon validation called  
**Then:**  
- Error: "This coupon code is no longer valid"
- No discount applied
- Original total unchanged
- API returns `404 Not Found` or `422 Unprocessable Entity` with error details

---

## EDGE CASES - Boundaries & Special Conditions

### 1. Add Maximum Quantity of Single Book (Inventory Limit)
**Given:** Book has stock of 5, cart limit per item = 10  
**When:** User sets quantity to 5 (all available stock)  
**Then:**  
- Cart accepts quantity = 5
- "Add to Cart" button disabled or shows "Max quantity reached"
- Attempting quantity = 6 returns `422` with "Insufficient stock (5 available)"
- Concurrent order doesn't cause overselling (race condition check)

### 2. Cart with Single Item Priced at $0.01
**Given:** Special promotional book priced at $0.01  
**When:** User adds to cart and proceeds to checkout  
**Then:**  
- Subtotal = $0.01
- Shipping/tax calculations still apply correctly
- Payment processing handles minimum transaction amount
- No divide-by-zero errors in discount percentage calculations

### 3. Session Timeout with Items in Cart
**Given:** User added 3 books to cart 2 hours ago, session timeout = 1 hour  
**When:** User returns and session is expired  
**Then:**  
- User prompted to log in again
- Cart contents either: (a) restored from persistent storage, or (b) cleared with warning
- No "ghost" cart items charged to wrong user
- API returns `401 Unauthorized` until re-authenticated

---

## SECURITY SCENARIOS - Authentication, Authorization, Injection

### 1. Price Manipulation via Tampered API Request
**Given:** Book costs $29.99 in database  
**When:** Attacker intercepts checkout API and modifies payload: `{"book_id": 123, "price": 0.01}`  
**Then:**  
- Server REJECTS tampered price
- Recalculates total using authoritative price from database
- Returns `403 Forbidden` or `422 Unprocessable Entity`
- Logs anomaly for fraud detection
- **CRITICAL:** Never trust client-side pricing

### 2. Cart Access Without Authentication (Broken Object Level Authorization)
**Given:** User A's cart ID is `cart_12345`  
**When:** Unauthenticated user or User B attempts `GET /api/cart/12345`  
**Then:**  
- API returns `401 Unauthorized` (if not logged in)
- API returns `403 Forbidden` (if logged in as different user)
- No cart contents leaked
- Cart ID should use UUID, not sequential integers

### 3. SQL Injection in Coupon Code Field
**Given:** Attacker enters coupon: `' OR '1'='1' --`  
**When:** Coupon validation executes  
**Then:**  
- Input properly sanitized via parameterized queries/ORM
- Returns `404 Not Found` (coupon doesn't exist)
- **NO** database error messages exposed
- **NO** unauthorized discount applied
- Logs potential injection attempt

---

## 🚩 Additional Security Red Flags to Test

- **Race Conditions:** Two users buying last copy simultaneously → check inventory locking
- **Cart Hijacking:** Ensure cart tokens are tied to user session, not guessable
- **CSRF Protection:** Cart modification endpoints require CSRF tokens
- **Coupon Brute Force:** Rate limit coupon validation attempts