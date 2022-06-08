import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from wellets_cli.util import datetime2str

auth_file = Path.home() / ".config" / "wellets_cli" / "token.json"


class UserSession(BaseModel):
    id: str
    email: str
    token: str
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {
            datetime: datetime2str,
        }


def retrieve_auth() -> Optional[UserSession]:
    if auth_file.exists():
        with open(auth_file) as f:
            auth = UserSession(**json.load(f))
    return auth


def persist_auth(data: str) -> Path:
    auth_file.parent.mkdir(parents=True, exist_ok=True)

    with open(auth_file, "w") as f:
        f.write(data)

    return auth_file


def get_auth_token() -> Optional[str]:
    auth = retrieve_auth()

    if auth:
        return auth.token

    return None


def get_email() -> Optional[str]:
    auth = retrieve_auth()

    if auth:
        return auth.email

    return None
