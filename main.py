from fastapi import FastAPI, Depends, HTTPException, status
from contextlib import asynccontextmanager
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from typing import List

from database import get_db, engine, Base
from models import User
from schemas import UserCreate, UserOut, LockUserRequest


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Botfarm Microservice",
    version="0.1",
    description="Микросервис для управления ботами в ботоферме",
    lifespan=lifespan
)


@app.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.login == user.login)
    result = await db.execute(stmt)
    
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Login already exists")

    db_user = User(
        id=user.id,
        login=user.login,
        password=user.password,
        project_id=user.project_id,
        env=user.env,
        domain=user.domain,
        locktime=None,
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user


@app.get("/users", response_model=List[UserOut])
async def get_users(db: AsyncSession = Depends(get_db)):
    stmt = select(User)
    result = await db.execute(stmt)
    return result.scalars().all()


@app.post("/users/lock")
async def lock_user(req: LockUserRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.id == req.user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    now = datetime.now(timezone.utc)
    if user.locktime and user.locktime > now:
        raise HTTPException(status_code=409, detail="User already locked")

    user.locktime = req.locktime
    await db.commit()
    
    return {
        "status": "locked",
        "user_id": req.user_id,
        "until": req.locktime
    }


@app.post("/users/free")
async def free_user(user_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.locktime = None
    await db.commit()
    
    return {
        "status": "freed",
        "user_id": user_id
    }


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "botofarma"}


@app.get("/")
async def root():
    return {
        "service": "Botofarma Microservice",
        "version": "0.1",
        "docs": "/docs",
        "health": "/health"
    }