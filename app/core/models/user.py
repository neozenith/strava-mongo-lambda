# Standard Library
from typing import Any, Dict, Optional

# Third Party Libraries
from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str
    stava_token: Optional[Dict[str, Any]] = None
