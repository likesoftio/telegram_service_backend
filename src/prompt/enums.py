from enum import Enum


class AIResponseStatus(str, Enum):
    PENDING = "PENDING"
    SAVED = "SAVED"
    ANSWERED = "ANSWERED"
    SENT = "SENT"
    ERROR = "ERROR"