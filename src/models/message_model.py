from typing import Optional
from sqlalchemy import Column, Integer, TEXT, Enum
from utils.dal import BaseModel
from pydantic import BaseModel as BaseSchema, Field

# Message schema for receiving request bodies and validation:
class MessageSchema(BaseSchema):
    id: Optional[int] = None
    conversation_id: int = Field(gt=0, alias="conversationId") # Validates that conversation_id is a positive integer
    sender: str = Field(pattern="^(user|assistant)$") # Must be either 'user' or 'assistant'
    content: str = Field(min_length=1)

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True


# Message model mapping to the MySQL database table:
class MessageModel(BaseModel):

    # Database table name:
    __tablename__ = "messages"

    # Table columns tailored exactly to your DB schema:
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column("conversation_id", Integer, nullable=False)
    sender = Column(Enum("user", "assistant"), nullable=False)
    content = Column(TEXT, nullable=False)

    # Convert message object into a dictionary safely
    def to_dict(self):
        return {
            "id": self.id,
            "conversationId": self.conversation_id, # matching front-end expectations
            "sender": str(self.sender),             # explicit string casting for Enum
            "content": self.content
        }