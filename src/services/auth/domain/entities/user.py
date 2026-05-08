from dataclasses import dataclass
from src.services.auth.domain.entities.role import Role


@dataclass
class User:
    id:         int
    name:       str
    last_name:  str
    email:      str
    password:   str
    role_id:    int
    circuit_id:    int | None = None
    role:          Role | None = None
    created_by:    int | None = None
    profile_image: str | None = None
