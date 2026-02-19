from enum import Enum


class Environment(str, Enum):
    DEV = "dev"
    STAGE = "stage"
    PROD = "prod"


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class OrderDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"
