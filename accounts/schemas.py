from datetime import datetime
from typing import Any, List, Optional
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


class GoogleAuthSchema(BaseModel):
    credential: str = Field(..., min_length=10)


class TwoFactorVerifyLoginSchema(BaseModel):
    temp_token: str
    code: str = Field(..., min_length=6, max_length=16)


class TwoFactorCodeSchema(BaseModel):
    code: str = Field(..., min_length=6, max_length=16)


class TwoFactorDisableSchema(BaseModel):
    password: str = ""
    code: str = ""


class ChangePasswordSchema(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class UpdateProfileSchema(BaseModel):
    first_name: str = ""
    last_name: str = ""
    phone_number: str = ""
    default_city: str = "Abidjan"
    default_commune: str = "Cocody"
    default_address: str = ""
    job_title: Optional[str] = None


class RoleOutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    description: str
    permissions: List[str]
    is_system: bool
    user_count: int = 0


class RoleWriteSchema(BaseModel):
    code: Optional[str] = None
    name: str = Field(..., min_length=2)
    description: str = ""
    permissions: List[str] = []


class UserOutSchema(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    phone_number: str
    default_city: str
    default_commune: str
    default_address: str
    account_type: str
    role_id: Optional[int] = None
    role_code: Optional[str] = None
    role_name: Optional[str] = None
    permissions: List[str] = []
    extra_permissions: List[str] = []
    job_title: str = ""
    is_2fa_enabled: bool = False
    is_staff: bool
    is_superuser: bool = False
    is_active: bool = True
    date_joined: datetime


class TokenResponseSchema(BaseModel):
    access_token: str = ""
    refresh_token: str = ""
    token_type: str = "Bearer"
    requires_2fa: bool = False
    temp_token: str = ""
    user: UserOutSchema


class AddressWriteSchema(BaseModel):
    label: str = "Maison"
    recipient_name: str = ""
    phone: str = ""
    delivery_zone_type: str = "ABIDJAN"
    city: str = "Abidjan"
    commune: str = "Cocody"
    address_details: str = Field(..., min_length=3)
    landmark: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_default: bool = False


class AddressOutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    label: str
    recipient_name: str
    phone: str
    delivery_zone_type: str
    city: str
    commune: str
    address_details: str
    landmark: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_default: bool
    created_at: datetime


class CollaboratorCreateSchema(BaseModel):
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(..., min_length=8)
    first_name: str = ""
    last_name: str = ""
    phone_number: str = ""
    job_title: str = ""
    role_id: Optional[int] = None
    extra_permissions: List[str] = []


class CollaboratorUpdateSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    job_title: Optional[str] = None
    role_id: Optional[int] = None
    extra_permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None
    new_password: Optional[str] = None


class CustomerSummarySchema(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    phone_number: str
    default_city: str
    default_commune: str
    default_address: str
    is_active: bool
    is_2fa_enabled: bool
    date_joined: datetime
    orders_count: int = 0
    total_spent_fcfa: int = 0
    addresses: List[AddressOutSchema] = []


class AuditLogOutSchema(BaseModel):
    id: int
    actor_email: str
    action: str
    target_type: str
    target_id: str
    summary: str
    metadata: dict[str, Any] = {}
    created_at: datetime


class NotificationOutSchema(BaseModel):
    id: int
    audience: str
    category: str
    title: str
    message: str
    link: str
    is_read: bool
    created_at: datetime


class NotificationListOutSchema(BaseModel):
    unread_count: int
    items: List[NotificationOutSchema]
