# Standard Library
from typing import Optional

# Third Party Libraries
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    expires_at: Optional[int] = None


class TokenData(BaseModel):
    username: Optional[str] = None
