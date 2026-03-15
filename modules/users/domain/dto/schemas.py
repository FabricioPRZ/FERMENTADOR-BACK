from pydantic import BaseModel, EmailStr
from datetime import datetime


class CreateUserRequest(BaseModel):
    name:            str
    last_name:       str
    email:           EmailStr
    password:        str
    role:            str       # 'profesor' (admin) o 'estudiante' (admin o profesor)
    activation_code: str       # Código del circuito al que se asocia el usuario


class UpdateUserRequest(BaseModel):
    name:      str | None = None
    last_name: str | None = None
    email:     EmailStr | None = None
    password:  str | None = None
    role:      str | None = None


class ActivateCircuitRequest(BaseModel):
    activation_code: str


class ActivateCircuitResponse(BaseModel):
    access_token: str
    token_type:   str
    circuit_id:   int


class UserResponse(BaseModel):
    id:         int
    name:       str
    last_name:  str
    email:      str
    role_id:    int
    role_name:  str | None
    circuit_id: int | None
    created_by: int | None
    created_at: datetime | None