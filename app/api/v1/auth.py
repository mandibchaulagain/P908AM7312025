#auth endpoints
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from auth.security import create_access_token, get_current_user
from auth.utils import verify_password
from crud.user import get_user_by_username, create_user
from models.user import UserCreate, UserInDB, Token, UserLogin, UserPublic

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.get("/protected/profile", response_model=UserPublic)
async def get_user_profile(
    current_user: UserInDB = Depends(get_current_user)
):
    """Get authenticated user's profile"""
    try:
        return current_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/login/json", response_model=Token)
async def login_json(credentials: UserLogin):
    user = get_user_by_username(credentials.username)
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    if get_user_by_username(user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    user_id = create_user(user.username, user.password, user.email)
    return {"id": user_id, "username": user.username}