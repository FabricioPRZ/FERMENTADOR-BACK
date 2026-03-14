from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id:         int
    name:       str
    last_name:  str
    email:      str
    password:   str
    role_id:    int
    circuit_id: int | None = None
    role_name:  str | None = None
    created_by: int | None = None
    created_at: datetime | None = None