from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from app.database import authenticate_user, get_user_by_id, list_users, create_user

router = APIRouter(prefix="", tags=["Authentication & RBAC"])


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str
    role: str = "operator"
    phone: Optional[str] = ""


class LoginResponse(BaseModel):
    success: bool
    token: str
    user: dict
    message: str


@router.post("/auth/login", response_model=LoginResponse)
@router.post("/api/auth/login", response_model=LoginResponse)
async def login_endpoint(payload: LoginRequest):
    """
    Authenticates Admin or Operator.
    - Admin: admin@ecoroute.city / admin123
    - Operator: operator@ecoroute.city / operator123
    """
    user = authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = f"ecoroute_token_{user['id']}_{user['role']}"
    return {
        "success": True,
        "token": token,
        "user": user,
        "message": f"Welcome back, {user['full_name']}! Signed in as {user['role'].upper()}."
    }


@router.post("/auth/register", response_model=LoginResponse)
@router.post("/api/auth/register", response_model=LoginResponse)
async def register_endpoint(payload: RegisterRequest):
    """
    Registers a new municipal staff user (Operator or Admin).
    """
    if len(payload.password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters long.")

    try:
        user = create_user(
            email=payload.email,
            password_plain=payload.password,
            full_name=payload.full_name,
            role=payload.role,
            phone=payload.phone or ""
        )
        token = f"ecoroute_token_{user['id']}_{user['role']}"
        return {
            "success": True,
            "token": token,
            "user": user,
            "message": f"Account created! Welcome, {user['full_name']} ({user['role'].upper()})."
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {e}")


@router.get("/auth/me")
@router.get("/api/auth/me")
async def get_current_user(authorization: Optional[str] = Header(None)):
    """Validates authorization token or returns default admin session."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        # Token format: ecoroute_token_<user_id>_<role>
        parts = token.split("_")
        if len(parts) >= 3:
            uid = parts[2]
            user = get_user_by_id(uid)
            if user:
                return {"authenticated": True, "user": user}

    # Fallback default logged-in profile: Admin Chethan (CS)
    user = get_user_by_id("usr-admin-01")
    return {"authenticated": True, "user": user}


@router.get("/auth/users")
@router.get("/api/auth/users")
async def get_all_users():
    """Lists registered staff users and roles."""
    return list_users()


@router.post("/auth/logout")
@router.post("/api/auth/logout")
async def logout():
    return {"success": True, "message": "Signed out successfully."}
