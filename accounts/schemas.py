from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class RegisterSchema(BaseModel):
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(..., min_length=8)
    first_name: str = ""
    last_name: str = ""
    phone_number: str = ""
    default_city: str = "Abidjan"
    default_commune: str = "Cocody"
    default_address: str = ""


class LoginSchema(BaseModel):
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str


class UpdateProfileSchema(BaseModel):
    first_name: str = ""
    last_name: str = ""
    phone_number: str = ""
    default_city: str = "Abidjan"
    default_commune: str = "Cocody"
    default_address: str = ""


class UserOutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    first_name: str
    last_name: str
    phone_number: str
    default_city: str
    default_commune: str
    default_address: str
    is_staff: bool
    date_joined: datetime


class TokenResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    user: UserOutSchema
