from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    id: str
    login: str
    password: str
    project_id: Optional[str] = None
    env: Optional[str] = None
    domain: Optional[str] = None

class UserOut(BaseModel):
    id: str
    login: str
    project_id: Optional[str]
    env: Optional[str]
    domain: Optional[str]
    locktime: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)


class LockUserRequest(BaseModel):
    user_id: str
    locktime: datetime