from pydantic import BaseModel, EmailStr


class CreateUserRequest(BaseModel):
    name:            str
    last_name:       str
    email:           EmailStr
    password:        str
    role:            str
    activation_code: str
