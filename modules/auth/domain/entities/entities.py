from dataclasses import dataclass


@dataclass
class Role:
    id:          int
    name:        str
    description: str | None = None


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