from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from dependencies.auth import get_current_user, blacklist
from utils.security import create_access_token, get_password_hash, verify_password

router = APIRouter()


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# Assuming a User model exists, but not implemented for brevity
# def get_user_by_username(db: Session, username: str):
#     return db.query(User).filter(User.username == username).first()


@router.post("/register", response_model=dict)
async def register(user: UserCreate):
    """
    Register a new user.
    In a real implementation, check if user exists and save to database.
    """
    # hashed_password = get_password_hash(user.password)
    # db_user = User(username=user.username, hashed_password=hashed_password)
    # db.add(db_user)
    # db.commit()
    return {"message": "User registered successfully"}


@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    """
    Authenticate user and return JWT token.
    In a real implementation, verify against database.
    """
    # db_user = get_user_by_username(db, user.username)
    # if not db_user or not verify_password(user.password, db_user.hashed_password):
    #     raise HTTPException(status_code=400, detail="Incorrect username or password")
    # access_token = create_access_token(data={"sub": db_user.id})
    # return {"access_token": access_token, "token_type": "bearer"}

    # For demo purposes, assume login succeeds with user_id based on username
    user_id = 1 if user.username == "testuser" else 2
    access_token = create_access_token(data={"sub": user_id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout the current user by blacklisting their token.
    """
    token = current_user["token"]
    blacklist.add_token(token)
    return {"message": "Successfully logged out"}