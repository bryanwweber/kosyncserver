from typing import Annotated

import aiosqlite
from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .database import get_db

router = APIRouter()


class User(BaseModel):
    username: str
    password: str


@router.post(
    "/users/create",
    status_code=status.HTTP_201_CREATED,
)
async def create_user(user: User, db: Annotated[aiosqlite.Connection, Depends(get_db)]):
    if not user.username or not user.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required",
        )
    result = await db.execute(
        "INSERT INTO users (username, password) VALUES (:username, :password)",
        {"username": user.username, "password": user.password},
    )
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )
    await db.commit()
    return JSONResponse(content={"username": user.username})


def user_to_user(cursor: aiosqlite.Cursor, row: tuple) -> User:
    fields = [c[0] for c in cursor.description]
    return User(**dict(zip(fields, row)))


async def get_user(
    x_auth_user: Annotated[str, Header()],
    x_auth_key: Annotated[str, Header()],
    db: Annotated[aiosqlite.Connection, Depends(get_db)],
) -> User | None:
    db.row_factory = user_to_user
    result = await db.execute(
        "SELECT * FROM users WHERE username = :username",
        {"username": x_auth_user},
    )
    user = await result.fetchone()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username"
        )
    if user.password != x_auth_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )
    return user


@router.get("/users/auth", status_code=status.HTTP_200_OK)
async def auth_user(_: Annotated[None, Depends(get_user)]):
    return JSONResponse(content={"authorized": "OK"})
