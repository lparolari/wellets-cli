import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

auth_file = Path.home() / ".config" / "wellets_cli" / "token.json"


class Auth(BaseModel):
    id: str
    email: str
    token: str
    created_at: datetime
    updated_at: datetime


def retrieve_auth() -> Optional[Auth]:
    if auth_file.exists():
        with open(auth_file) as f:
            auth = Auth(**json.load(f))
    return auth


def persist_auth(data: str) -> Path:
    auth_file.parent.mkdir(parents=True, exist_ok=True)

    with open(auth_file, "w") as f:
        json.dump(data, f)

    return auth_file


def get_auth_token() -> Optional[str]:
    auth = retrieve_auth()

    if auth:
        return auth.token

    return None
