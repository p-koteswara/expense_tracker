from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.user import User
from app.db.models.revoked_token import RevokedToken
from app.schemas.user import UserCreate, UserLogin, UserOut
from app.core.security import hash_password, verify_password
from app.core.jwt import ALGORITHM, SECRET_KEY, create_access_token, get_current_user, oauth2_scheme

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


@router.post("/login")
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db),
):
    db_user = db.query(User).filter(User.email == user_data.email).first()

    if not db_user or not verify_password(user_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": db_user.email},
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserOut.from_orm(db_user)
    }


@router.post("/logout")
def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Revoke the currently presented access token (server-side logout).
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti: str | None = payload.get("jti")
        exp = payload.get("exp")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    if not jti or not exp:
        raise HTTPException(status_code=400, detail="Token cannot be revoked")

    if isinstance(exp, (int, float)):
        expires_at = datetime.utcfromtimestamp(exp)
    elif isinstance(exp, datetime):
        expires_at = exp
    else:
        raise HTTPException(status_code=400, detail="Invalid token expiry")

    existing = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()
    if existing:
        return {"message": "Logged out"}

    db.add(
        RevokedToken(
            jti=jti,
            user_email=getattr(current_user, "email", None),
            expires_at=expires_at,
        )
    )
    db.commit()

    return {"message": "Logged out"}
