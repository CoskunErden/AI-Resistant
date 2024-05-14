from pydantic import BaseModel, field_validator
from fastapi import UploadFile
from typing import Optional, List, Any
from pydantic import Field
from enum import Enum
from services.tool_registry import BaseTool


class User(BaseModel):
    id: str
    fullName: str
    email: str
    
class Role(str, Enum):
    human = "human"
    ai = "ai"
    system = "system"

class MessageType(str, Enum):
    text = "text"
    image = "image"
    video = "video"
    file = "file"

class MessagePayload(BaseModel):
    text: str

class Message(BaseModel):
  role: Role
  type: MessageType
  timestamp: Optional[Any] = None
  payload: MessagePayload
    
class RequestType(str, Enum):
    chat = "chat"
    tool = "tool"

class GenericRequest(BaseModel):
    user: User
    type: RequestType
    tool_data: Optional[BaseTool] = None
    messages: Optional[List[Message]] = None
    
class ChatResponse(BaseModel):
    data: List[Message]

class ToolResponse(BaseModel):
    data: List[Any]
    
class GCS_File(BaseModel):
    filePath: str
    url: Optional[str]
    filename: Optional[str]

class ChatMessage(BaseModel):
    role: str
    type: str
    text: str