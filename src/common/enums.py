# enums.py
from enum import Enum

class UserRole(Enum):
    EVERYONE = "everyone"
    USER = "user"
    ADMIN = "admin"
