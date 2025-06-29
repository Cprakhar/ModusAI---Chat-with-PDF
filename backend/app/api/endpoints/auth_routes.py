from fastapi import APIRouter, HTTPException
from app.models.user import UserCreate, UserLogin, UserOut, TokenResponse
import sqlite3
import os
import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import uuid

JWT_SECRET = os.environ.get("JWT_SECRET")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM")
JWT_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

auth_router = APIRouter()
router = auth_router

# Use a central db directory for all .db files
DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../db'))
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, 'users.db')

def init_user_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )''')
        conn.commit()

init_user_db()

def get_user_by_email(email: str):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT id, username, email, password_hash FROM users WHERE email = ?', (email,))
        row = c.fetchone()
        if row:
            return {"id": row[0], "username": row[1], "email": row[2], "password_hash": row[3]}
        return None

def get_user_by_username(username: str):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT id, username, email, password_hash FROM users WHERE username = ?', (username,))
        row = c.fetchone()
        if row:
            return {"id": row[0], "username": row[1], "email": row[2], "password_hash": row[3]}
        return None

def create_user(username: str, email: str, password: str):
    password_hash = pwd_context.hash(password)
    user_id = str(uuid.uuid4())
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (id, username, email, password_hash) VALUES (?, ?, ?, ?)', (user_id, username, email, password_hash))
            conn.commit()
            return get_user_by_email(email)
        except sqlite3.IntegrityError:
            return None

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

@auth_router.post("/auth/register", response_model=UserOut)
def register(user: UserCreate):
    if get_user_by_username(user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = create_user(user.username, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=400, detail="Registration failed")
    return UserOut(id=db_user["id"], username=db_user["username"], email=db_user["email"])

@auth_router.post("/auth/login", response_model=TokenResponse)
def login(user: UserLogin):
    db_user = get_user_by_email(user.email)
    if not db_user or not verify_password(user.password, db_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    token = create_access_token({"user_id": db_user["id"], "username": db_user["username"], "email": db_user["email"]})
    return TokenResponse(access_token=token)

@auth_router.post("/auth/logout")
def logout():
    # For JWT, logout is handled client-side (delete token). Optionally, implement token blacklist here.
    return {"message": "Logged out (client should delete token)"}
