from pydantic import BaseModel, EmailStr


class UpdateUserRequest(BaseModel):
    name:          str | None = None
    last_name:     str | None = None
    email:         EmailStr | None = None
    password:      str | None = None
    role:          str | None = None
    profile_image: str | None = None
