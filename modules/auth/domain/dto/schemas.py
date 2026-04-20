from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


class RegisterRequest(BaseModel):
    name:      str
    last_name: str
    email:     EmailStr
    password:  str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id:            int
    name:          str
    last_name:     str
    email:         str
    role:          str
    profile_image: str | None = None


class TokenResponse(BaseModel):
    access_token:  str
    refresh_token: str
    token_type:    str
    user:          UserResponse


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type:   str


class RegisterResponse(BaseModel):
    id:        int
    name:      str
    last_name: str
    email:     str
    role:      str