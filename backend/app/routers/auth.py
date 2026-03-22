from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_admin, get_current_user
from app.models.user import User
from app.schemas.user import TokenResponse, UserCreate, UserResponse
from app.services.auth_service import authenticate_user, create_access_token, get_password_hash

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        username=data.username,
        email=data.email,
        password_hash=get_password_hash(data.password),
        is_admin=data.is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/setup", response_model=UserResponse, status_code=201)
def setup_first_admin(data: UserCreate, db: Session = Depends(get_db)):
    """Create the first admin user. Only works when no users exist."""
    if db.query(User).count() > 0:
        raise HTTPException(status_code=403, detail="Setup already done")
    user = User(
        username=data.username,
        email=data.email,
        password_hash=get_password_hash(data.password),
        is_admin=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
