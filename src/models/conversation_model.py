from sqlalchemy import Column, Integer, TIMESTAMP, text
from utils.dal import BaseModel

# Conversation model mapping to the MySQL database table
class ConversationModel(BaseModel):

    # Database table name matching your MySQL schema
    __tablename__ = "conversations"

    # Table columns tailored exactly to your DB schema
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    # Convert conversation object into a dictionary
    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None # type: ignore
        }