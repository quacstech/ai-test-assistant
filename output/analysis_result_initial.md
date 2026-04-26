# Login API with JWT Authentication - Test Analysis

## API Assumptions
```
POST /api/v1/auth/login
Content-Type: application/json

Request Body:
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

Success Response (200):
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "user"
  }
}
```

---

## POSITIVE CASES

### PC-01: Successful login with valid credentials
- **Given**: Registered user with email "user@example.com" and correct password
- **When**: POST request with valid credentials
- **Then**: 
  - Status: **200 OK**
  - Response contains valid JWT access_token and refresh_token
  - Token can be decoded and contains user_id, email, role claims
  - `expires_in` matches token's exp claim
  - User object returned with correct details

### PC-02: Case-insensitive email login
- **Given**: User registered as "User@Example.com"
- **When**: Login with "user@example.com" (lowercase)
- **Then**: 
  - Status: **200 OK**
  - Login successful, tokens issued

### PC-03: Login after password reset
- **Given**: User has recently reset password
- **When**: Login with new password
- **Then**: 
  - Status: **200 OK**
  - Tokens issued successfully
  - Old sessions/tokens should be invalidated

### PC-04: Login with different user roles
- **Test each role**: admin, manager, user, guest
- **When**: Valid credentials for each role type
- **Then**: 
  - Status: **200 OK**
  - JWT contains correct role claim
  - Permissions align with role

---

## NEGATIVE CASES

### NC-01: Invalid password
- **When**: POST with correct email but wrong password
- **Then**: 
  - Status: **401 Unauthorized**
  - Error: `{"error": "Invalid credentials"}`
  - No token issued
  - Generic error message (doesn't reveal if email exists)

### NC-02: Non-existent email
- **When**: POST with unregistered email
- **Then**: 
  - Status: **401 Unauthorized**
  - Same error as NC-01 (security best practice)
  - Response time should be similar to invalid password (prevent enumeration)

### NC-03: Missing email field
- **When**: POST with only password `{"password": "test"}`
- **Then**: 
  - Status: **422 Unprocessable Entity** or **400 Bad Request**
  - Error: `{"error": "email is required"}`

### NC-04: Missing password field
- **When**: POST with only email `{"email": "user@example.com"}`
- **Then**: 
  - Status: **422 Unprocessable Entity**
  - Error: `{"error": "password is required"}`

### NC-05: Empty request body
- **When**: POST with `{}`
- **Then**: 
  - Status: **422 Unprocessable Entity**
  - Error lists all required fields

### NC-06: Invalid email format
- **When**: POST with malformed email "notanemail"
- **Then**: 
  - Status: **422 Unprocessable Entity**
  - Error: `{"error": "Invalid email format"}`

### NC-07: Account locked/disabled
- **Given**: User account is locked after multiple failed attempts
- **When**: POST with valid credentials
- **Then**: 
  - Status: **403 Forbidden**
  - Error: `{"error": "Account is locked. Try again in X minutes"}`

### NC-08: Unverified email account
- **Given**: User registered but hasn't verified email
- **When**: Login attempt
- **Then**: 
  - Status: **403 Forbidden**
  - Error: `{"error": "Please verify your email before logging in"}`

---

## EDGE CASES

### EC-01: Extremely long email (>255 chars)
- **When**: POST with 1000 character email
- **Then**: 
  - Status: **422 Unprocessable Entity**
  - Error: `{"error": "Email exceeds maximum length"}`
  - No server crash or timeout

### EC-02: Extremely long password (>1000 chars)
- **When**: POST with 5000 character password
- **Then**: 
  - Status: **422 Unprocessable Entity** or **413 Payload Too Large**
  - Request rejected before authentication processing

### EC-03: Special characters in email
- **Test**: `user+test@example.com`, `user.name@example.co.uk`
- **Then**: Should handle valid RFC 5322 email formats correctly

### EC-04: Unicode/emoji in password
- **When**: Password contains emoji or Chinese characters "Pass🔒词123"
- **Then**: 
  - If user registered with it: **200 OK**
  - Should support UTF-8 encoding

### EC-05: Whitespace handling
- **Test cases**:
  - Leading/trailing spaces in email: `" user@example.com "`
  - Spaces in password: `"Pass word123"`
- **Then**: 
  - Email should be trimmed automatically → **200 OK** if valid
  - Password must match exactly (spaces are significant) → **401** if mismatch

### EC-06: Null values
- **When**: `{"email": null, "password": null}`
- **Then**: 
  - Status: **422 Unprocessable Entity**
  - Proper error handling, no null pointer exceptions

### EC-07: Wrong Content-Type
- **When**: POST with `Content-Type: text/plain`
- **Then**: 
  - Status: **415 Unsupported Media Type**
  - Error: `{"error": "Content-Type must be application/json"}`

### EC-08: JWT expiry boundary
- **When**: Generate token and wait until 1 second before expiry
- **Then**: Token should still be valid
- **When**: Wait until 1 second after expiry
- **Then**: Token should be rejected (401) on protected endpoints

### EC-09: Concurrent login sessions
- **Given**: User logs in from 2 devices simultaneously
- **Then**: 
  - Both should receive valid tokens (unless business rule prevents)
  - Test if system allows multiple active sessions

### EC-10: Request rate limiting
- **When**: 100 rapid login requests from same IP
- **Then**: 
  - Status: **429 Too Many Requests** (after threshold)
  - Error: `{"error": "Rate limit exceeded. Try again in X seconds"}`
  - Legitimate requests should not be blocked

---

## SECURITY SCENARIOS

### SS-01: SQL Injection attempts
- **Test inputs**:
  - Email: `admin'--`
  - Email: `' OR '1'='1`
  - Password: `' OR '1'='1'--`
- **Then**: 
  - Status: **401 Unauthorized** (not 500 Internal Server Error)
  - No database error messages leaked
  - Parameterized queries should prevent injection

### SS-02: NoSQL Injection (if using MongoDB/similar)
- **Test**: `{"email": {"$ne": null}, "password": {"$ne": null}}`
- **Then**: 
  - Status: **422 Unprocessable Entity**
  - Proper input validation prevents object injection

### SS-03: JWT token tampering
- **When**: Modify payload of issued JWT (change user_id or role)
- **Then**: 
  - Signature validation fails
  - Status: **401 Unauthorized** when using tampered token

### SS-04: JWT "none" algorithm attack
- **When**: Submit JWT with `"alg": "none"` in header
- **Then**: 
  - Token rejected
  - Server enforces specific algorithms (RS256/HS256)

### SS-05: Password in URL/logs
- **Check**: Ensure password never appears in:
  - Server logs
  - Error messages
  - URL parameters
  - Browser history

### SS-06: Timing attack prevention
- **Test**: Measure response time for:
  - Valid email + wrong password
  - Invalid email + any password
- **Then**: Response times should be similar (prevent user enumeration)

### SS-07: Brute force protection
- **When**: 10+ failed login attempts for same account
- **Then**: 
  - Account temporarily locked
  - Status: **403 Forbidden** with lockout message
  - Consider CAPTCHA or MFA trigger

### SS-08: Credential stuffing detection
- **When**: Multiple accounts accessed from same IP with failed attempts
- **Then**: 
  - IP-based rate limiting triggered
  - Status: **429 Too Many Requests**

### SS-09: Token storage security
- **Verify**:
  - Tokens sent over HTTPS only
  - Refresh token has longer expiry than access token
  - `Secure` and `HttpOnly` flags set if using cookies
  - No tokens in local storage (XSS risk)

### SS-10: CORS validation
- **When**: Login request from unauthorized origin
- **Then**: 
  - CORS policy blocks request
  - Only whitelisted domains allowed

### SS-11: Replay attack prevention
- **When**: Intercept login request and replay it
- **Then**: 
  - Consider implementing nonce/timestamp validation
  - Each login should generate unique tokens

### SS-12: Session fixation
- **When**: Attacker sets session ID before user logs in
- **Then**: 
  - New JWT issued after successful login
  - Old session identifiers invalidated

### SS-13: Information disclosure
- **When**: Any error occurs
- **Then**: 
  - No stack traces in response
  - No database structure revealed
  - No version information leaked
  - Generic error messages only

### SS-14: HTTPS enforcement
- **When**: Attempt HTTP request (not HTTPS)
- **Then**: 
  - Request redirected to HTTPS or rejected
  - Credentials never transmitted over plain HTTP

### SS-15: Token revocation
- **When**: User logs out or changes password
- **Then**: 
  - Issued tokens should be invalidated
  - Blacklist or database check for revoked tokens
  - Old tokens rejected with **401 Unauthorized**

### SS-16: JWT secret strength
- **Verify**:
  - HS256 uses cryptographically strong secret (256+ bits)
  - RS256 uses proper key length (2048+ bits)
  - Secrets not hardcoded or in version control

---

## Additional Test Considerations

### Performance Testing
- Measure login response time under normal load (<500ms target)
- Test concurrent logins (1000+ simultaneous users)
- Monitor token generation performance

### Monitoring & Logging
- Failed login attempts logged (for security monitoring)
- Successful logins logged with IP, timestamp, user agent
- No sensitive data (passwords) in logs

### Token Claims Validation
- Verify JWT contains: `sub` (user_id), `iat`, `exp`, `role`
- Check token signature algorithm is secure
- Validate `exp` claim matches `expires_in` field

### Business Logic
- Test account lockout duration
- Verify session timeout behavior
- Check refresh token rotation logic

---

## 🚩 RED FLAGS to Watch For

1. **Password returned in response** (major security risk)
2. **Different error messages for invalid email vs password** (enumeration risk)
3. **No rate limiting** (brute force vulnerability)
4. **Weak JWT secret** (token can be forged)
5. **No HTTPS enforcement** (credential interception risk)
6. **SQL errors in response** (injection vulnerability)
7. **No account lockout** (unlimited brute force attempts)
8. **Timing differences** revealing valid emails

---

Would you like me to generate automated test scripts (Playwright/Postman/RestAssured) for any of these scenarios?