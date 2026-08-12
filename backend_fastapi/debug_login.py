import traceback
from app.core.database import SessionLocal
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services import auth_service
from fastapi import HTTPException

db = SessionLocal()

# Test register
print("=== Testing register ===")
try:
    req = RegisterRequest(email="debug@test.com", password="test123", fullName="Debug User")
    result = auth_service.register(db, req)
    print("Register OK:", result)
except HTTPException as e:
    print("HTTPException:", e.status_code, e.detail)
except Exception:
    traceback.print_exc()

# Test login
print("\n=== Testing login ===")
try:
    req = LoginRequest(email="debug@test.com", password="test123")
    result = auth_service.login(db, req)
    print("Login OK:", result)
except HTTPException as e:
    print("HTTPException:", e.status_code, e.detail)
except Exception:
    traceback.print_exc()

db.close()
print("\nDone.")
