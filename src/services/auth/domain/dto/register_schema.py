from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    name:      str
    last_name: str
    email:     EmailStr
    password:  str


class RegisterResponse(BaseModel):
    id:        int
    name:      str
    last_name: str
    email:     str
    role:      str
