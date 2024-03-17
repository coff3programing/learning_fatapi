from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from jose import jwt, JWTError
from passlib.context import CryptContext


ALGORITHM = 'HS256'
ACCESS_TOKEN_DURATION = 2
SECRET = "4af27be66a5399eff026251125e629291e0067a30f6f8dd603645599278fd1a2"

app = FastAPI()

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

crypt = CryptContext(schemes=["bcrypt"])


class User(BaseModel):
    username: str
    full_name: str
    email: str
    disabled: bool


class UserDB(User):
    password: str


users_db = {
    "marco": {
        "username": "marco",
        "full_name": "Marco Dias",
        "email": "marco@gmail.com",
        "disabled": False,
        "password":
        "$2a$10$rsgwENASp964ZO7EbFhW5.1JJmjeG4U6KdUwKUVEl7jF3g0Gj/Dw6",
        #marco123
    },
    "santiago": {
        "username": "santiago",
        "full_name": "Santiago C",
        "email": "santi@gmail.com",
        "disabled": True,
        "password":
        "$2a$10$a17tFfM7E2kc2x5DEQy18.9tWgACQonT9ScJE1DPJw3yk0ZJQ/AsO",
        # santiago456
    }
}


def search_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])


def search_user(username: str):
    if username in users_db:
        return User(**users_db[username])


async def auth_user(token: str = Depends(oauth2)):
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        username = jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get("sub")
        if username is None:
            raise exception

    except JWTError:
        raise exception

    return search_user(username)


async def current_user(user: User = Depends(auth_user)):
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is disabled"
        )

    return user


@app.post('/login', tags=["Login"], status_code=200)
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_db = users_db.get(form.username)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username"
        )

    user = search_user_db(form.username)

    if not crypt.verify(form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    expiration = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)

    access_token = {"sub": user.username, "exp": expiration}

    return {
        "access_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM),
        "token_type": "bearer"
    }


@app.get('/movies/me', tags=['Login'], status_code=200)
async def me(user: User = Depends(current_user)):
    return user
