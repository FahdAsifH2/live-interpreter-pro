import enum


class UserRole(str, enum.Enum):
    """User role enum"""
    USER = "user"
    ADMIN = "admin"

