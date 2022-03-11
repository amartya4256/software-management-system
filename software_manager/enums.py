from enum import Enum

class Status(str, Enum):
    CREATED = "created"
    DOWNLOADED = "downloaded"
    ACTIVE = "active"