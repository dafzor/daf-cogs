from enum import Enum

class EventReplyStatus(Enum):
    NONE = 0
    YES = 1
    NO = 2
    TENTATIVE = 3

class EventReply:
    user: str
    reply: EventReplyStatus
