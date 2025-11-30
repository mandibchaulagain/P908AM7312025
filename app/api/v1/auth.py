#auth endpoints
from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from auth.security import create_access_token, create_refresh_token, decode_refresh_token, get_current_user, oauth2_scheme
from auth.utils import add_to_blacklist, is_blacklisted, verify_password
from crud.user import get_user_by_username, create_user
from models.user import AccessTokenResponse, UserCreate, UserInDB, Token, UserLogin, UserPublic
from database.connection import connection_pool

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

@router.post("/login", response_model=AccessTokenResponse)
async def login(credentials: UserLogin, response: Response):
    user = get_user_by_username(credentials.username)
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token({"sub": user["username"]})
    refresh_token = create_refresh_token({"sub": user["username"]})

    # Set HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,   # True only in HTTPS
        samesite="lax",
        path="/"        # very important, cookie must be sent on /refresh
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }




@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    response: Response,
    current_user: UserInDB = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
    refresh_token: str | None = Cookie(None)
):
    add_to_blacklist(token)
    if refresh_token:
        add_to_blacklist(refresh_token)
    
    # Clear the refresh token cookie
    response.delete_cookie(key="refresh_token", path="/")
    
    return {"detail": f"User {current_user.username} has been logged out"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    if get_user_by_username(user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    user_id = create_user(user.username, user.email, user.password, is_admin=False)
    return {"id": user_id, "username": user.username}

@router.delete("/delete-account", status_code=status.HTTP_200_OK)
async def delete_account(
    current_user: UserInDB = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    """
    Deletes the currently authenticated user's account.
    """
    if connection_pool is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection unavailable"
        )

    try:
        # Get a connection from the pool
        conn = connection_pool.get_connection()
        cursor = conn.cursor()

        # Execute DELETE statement
        delete_query = "DELETE FROM users WHERE id = %s"
        cursor.execute(delete_query, (current_user.id,))
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        cursor.close()
        conn.close()

        return {"detail": f"User {current_user.username} has been deleted"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh_token(response: Response, refresh_token: str = Cookie(...)):
    if is_blacklisted(refresh_token):
        raise HTTPException(status_code=401, detail="Refresh token revoked")

    username = decode_refresh_token(refresh_token)

    # Issue new access + refresh
    new_access = create_access_token({"sub": username})
    new_refresh = create_refresh_token({"sub": username})

    # Blacklist old refresh token
    add_to_blacklist(refresh_token)

    # Set new refresh token in HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=False,  # only HTTPS in production
        samesite="lax",
        path="/"    
    )

    # Return new access token in JSON
    return {
        "access_token": new_access,
        "token_type": "bearer"
    }