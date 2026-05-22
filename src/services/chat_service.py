from flask import session
from utils.dal import Dal
from models.message_model import MessageModel
from models.conversation_model import ConversationModel

class ChatService:

    # Ctor
    def __init__(self) -> None:
        self.dal = Dal()
        self.session = self.dal.create_session()
    
    # Create a new conversation record and return its newly generated ID
    def create_conversation(self) -> int:
        # Instantiate a clean conversation object using the ORM model
        conversation = ConversationModel()
        
        # Add to session and commit to generate the auto-increment ID
        self.session.add(conversation)
        self.session.commit()
        
        # Refresh the instance from the database to populate the auto-incremented ID
        self.session.refresh(conversation)
        
        # Return the newly assigned integer primary key (ignoring strict linter type checks)
        return int(conversation.id) # type: ignore

    # Check if a specific conversation record exists in the database
    def conversation_exists(self, conversation_id: int) -> bool:
        # Query the conversations table using the ORM layout
        exists = self.session.query(ConversationModel).filter(ConversationModel.id == conversation_id).first() is not None
        self.session.commit() # Clear transaction state
        return exists

    # Retrieve chronological message history belonging to a specific conversation
    def get_chat_history(self, conversation_id: int):
        # Query messages belonging to the conversation ordered chronologically
        history = self.session.query(MessageModel).filter(MessageModel.conversation_id == conversation_id).order_by(MessageModel.id.asc()).all()
        self.session.commit() # Clear transaction state
        return history

    # Save a new message record inside the database
    def add_message(self, conversation_id: int, sender: str, content: str) -> None:
        message = MessageModel(conversation_id=conversation_id, sender=sender, content=content)
        self.session.add(message)
        self.session.commit() # Save in DB

    # Closing
    def close(self):
        self.session.close()

    # Enable with context management
    def __enter__(self):
       return self
    
    # Exit context management and guarantee session cleanup
    def __exit__(self, exc_type, exc, tb):
        self.session.close()