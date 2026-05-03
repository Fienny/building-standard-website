# Security Recommendations for Standards Platform

## Current Security Status

### ✅ Implemented (Good)
1. **Password Hashing**: Using werkzeug.security (pbkdf2:sha256)
2. **JWT Authentication**: flask-jwt-extended with token expiration
3. **SQL Injection Protection**: SQLAlchemy ORM
4. **CORS**: Configured for specific frontend URL only
5. **Email Normalization**: lowercase + strip
6. **User Account Status**: is_active flag for account deactivation

---

## 🔴 CRITICAL - Must Implement Before Production

### 1. HTTPS/SSL Certificate
**Status**: ❌ Not configured  
**Risk**: Credentials and tokens sent in plain text  
**Solution**:
```nginx
# Nginx configuration
server {
    listen 443 ssl http2;
    ssl_certificate /etc/letsencrypt/live/standards.uz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/standards.uz/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    return 301 https://$host$request_uri;
}
```

### 2. Rate Limiting
**Status**: ❌ Not implemented  
**Risk**: Brute force attacks on login/register  
**Solution**:
```python
# Install: pip install Flask-Limiter
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# In auth.py
@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")  # Max 5 login attempts per minute
def login():
    ...

@auth_bp.route("/register", methods=["POST"])
@limiter.limit("3 per hour")  # Max 3 registrations per hour per IP
def register():
    ...
```

### 3. Email Verification
**Status**: ❌ Not implemented  
**Risk**: Fake accounts, spam  
**Solution**:
```python
# Add to User model
email_verified = db.Column(db.Boolean, default=False)
verification_token = db.Column(db.String(255), nullable=True)

# Send verification email on registration
# Verify before allowing purchases
```

### 4. Strong Password Policy
**Status**: ⚠️ Only 6 characters minimum  
**Risk**: Weak passwords  
**Solution**:
```python
import re

def validate_password(password):
    """
    Password must be:
    - At least 8 characters
    - Contains uppercase and lowercase
    - Contains at least one digit
    - Contains at least one special character
    """
    if len(password) < 8:
        return False, "Пароль должен содержать минимум 8 символов"
    
    if not re.search(r'[A-Z]', password):
        return False, "Пароль должен содержать заглавные буквы"
    
    if not re.search(r'[a-z]', password):
        return False, "Пароль должен содержать строчные буквы"
    
    if not re.search(r'\d', password):
        return False, "Пароль должен содержать цифры"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Пароль должен содержать спецсимволы"
    
    return True, ""

# In register route
is_valid, error_msg = validate_password(password)
if not is_valid:
    return jsonify({"error": error_msg}), 400
```

### 5. JWT Token Refresh
**Status**: ❌ No refresh token  
**Risk**: User logged out frequently  
**Solution**:
```python
# Add refresh token
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return jsonify({"token": access_token})
```

---

## 🟡 MEDIUM Priority

### 6. CSRF Protection for Payment Endpoints
```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# Exempt API endpoints from CSRF (using JWT instead)
app.config['WTF_CSRF_CHECK_DEFAULT'] = False
app.config['WTF_CSRF_ENABLED'] = False  # For API-only backend
```

### 7. Input Sanitization
```python
import bleach

def sanitize_input(text, max_length=500):
    """Remove HTML tags and limit length"""
    clean = bleach.clean(text, tags=[], strip=True)
    return clean[:max_length]

# In routes
name = sanitize_input(data.get("name", ""))
```

### 8. Logging & Monitoring
```python
import logging

# In auth.py
@auth_bp.route("/login", methods=["POST"])
def login():
    # ... existing code ...
    
    if not user or not user.check_password(password):
        app.logger.warning(f"Failed login attempt for {email} from {request.remote_addr}")
        return jsonify({"error": "Неверный email или пароль"}), 401
    
    app.logger.info(f"Successful login: {email}")
```

### 9. Account Lockout After Failed Attempts
```python
# Add to User model
failed_login_attempts = db.Column(db.Integer, default=0)
locked_until = db.Column(db.DateTime, nullable=True)

# In login route
if user.locked_until and user.locked_until > datetime.now(timezone.utc):
    return jsonify({"error": "Аккаунт временно заблокирован"}), 403

if not user.check_password(password):
    user.failed_login_attempts += 1
    if user.failed_login_attempts >= 5:
        user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)
    db.session.commit()
    return jsonify({"error": "Неверный пароль"}), 401

# Reset on successful login
user.failed_login_attempts = 0
user.locked_until = None
```

### 10. Secure JWT Secret Key
```bash
# Generate strong secret
python -c "import secrets; print(secrets.token_hex(32))"

# In .env
JWT_SECRET_KEY=<64-character-hex-string>
SECRET_KEY=<64-character-hex-string>
```

---

## 🟢 LOW Priority (Nice to Have)

11. **Two-Factor Authentication (2FA)**
12. **Security Headers** (X-Frame-Options, Content-Security-Policy)
13. **Session Management** (logout from all devices)
14. **Password Reset Flow** (forgot password)
15. **Audit Log** (who bought what, when)

---

## Implementation Priority

**Phase 1 (Before Launch):**
1. ✅ HTTPS/SSL
2. ✅ Rate Limiting
3. ✅ Strong Password Policy
4. ✅ Secure JWT Secrets

**Phase 2 (Week 1 after launch):**
5. Email Verification
6. Account Lockout
7. Logging

**Phase 3 (Future):**
8. JWT Refresh Tokens
9. 2FA
10. Password Reset

---

## Current Vulnerabilities Summary

| Vulnerability | Severity | Status | ETA Fix |
|--------------|----------|--------|---------|
| No HTTPS | 🔴 Critical | Not implemented | Before production |
| No Rate Limiting | 🔴 Critical | Not implemented | Before production |
| Weak Password Policy | 🟡 Medium | Only 6 chars | Phase 1 |
| No Email Verification | 🟡 Medium | Not implemented | Phase 2 |
| Short JWT Secret | 🟡 Medium | 28 bytes vs 32 | Phase 1 |
| No Account Lockout | 🟡 Medium | Not implemented | Phase 2 |
| No 2FA | 🟢 Low | Not implemented | Phase 3 |

---

**Last Updated**: 2026-05-03
