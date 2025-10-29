#auth endpoints
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from auth.security import create_access_token, get_current_user, oauth2_scheme
from auth.utils import add_to_blacklist, verify_password
from crud.user import get_user_by_username, create_user
from models.user import UserCreate, UserInDB, Token, UserLogin, UserPublic
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

@router.post("/login", response_model=Token)
async def login_json(credentials: UserLogin):
    user = get_user_by_username(credentials.username)
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(current_user: UserInDB = Depends(get_current_user), token: str = Depends(oauth2_scheme)):
    """
    Logs out the current user by blacklisting their JWT.
    """
    add_to_blacklist(token)
    return {"detail": f"User {current_user.username} has been logged out"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    if get_user_by_username(user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    user_id = create_user(user.username, user.password, user.email)
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