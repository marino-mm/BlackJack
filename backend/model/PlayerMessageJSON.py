from typing import Union, Literal
from pydantic import BaseModel, PositiveInt


class PingPongMessage(BaseModel):
    messageType: Literal["PingPong"]
    message: str

class InitialUsernameMessage(BaseModel):
    username: str

class ActionMessage(BaseModel):
    messageType: Literal["Action"]
    message: str

class MoveSlotMessage(BaseModel):
    messageType: Literal["MoveSlot"]
    new_slot_index: PositiveInt

IncomingMessage = Union[PingPongMessage, InitialUsernameMessage, ActionMessage, MoveSlotMessage]