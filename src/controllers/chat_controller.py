from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from pydantic import ValidationError
from services.gpt_service import gpt_service
from services.chat_service import ChatService
from models.message_model import MessageSchema

chat_blueprint = Blueprint("chat_controller", __name__)

# UI Route to render the main interface layout
@chat_blueprint.get("/home")
def home_page():
    return render_template("pages/home.html")

# API endpoint to initialize a completely new conversation record in MySQL
@chat_blueprint.post("/api/chat/new")
def create_new_conversation():
    try:
        with ChatService() as chat_service:
            # Create an empty conversation row and fetch its newly generated auto-increment ID
            new_id = chat_service.create_conversation()
            
        return jsonify({"status": "success", "conversationId": new_id}), 201
        
    except Exception as err:
        print("DATABASE INITIALIZATION ERROR:", str(err))
        return jsonify({"error": "Failed to initialize conversation session."}), 500

# API endpoint to process chat messages and maintain context
@chat_blueprint.post("/api/chat/<int:conversation_id>")
def handle_chat_message(conversation_id: int):
    try:
        # Prepare data for Pydantic validation
        data = {
            "conversationId": conversation_id,
            "sender": "user",
            "content": request.json.get("content") if request.is_json else request.form.get("content")
        }
        
        # Validate input schema
        schema = MessageSchema(**data) 
        
        # Open database context session
        with ChatService() as chat_service:
            
            # Check if conversation exists in database
            if not chat_service.conversation_exists(conversation_id):
                return jsonify({"error": f"Conversation with ID {conversation_id} does not exist."}), 404
            
            # Save user prompt to MySQL
            chat_service.add_message(schema.conversation_id, schema.sender, schema.content)
            
            # Retrieve chronological history of the current conversation
            db_history = chat_service.get_chat_history(conversation_id)
            
            # Construct the full message payload for OpenAI API context safely using ORM dicts
            openai_messages = [{"role": "system", "content": "You are a helpful AI assistant."}]
            for msg in db_history:
                # Converts the ORM instance into a clean dictionary with pure string values
                msg_data = msg.to_dict()
                
                openai_messages.append({
                    "role": msg_data["sender"],    # Contains the clean 'user' or 'assistant' string
                    "content": msg_data["content"] # Contains the clean message text
                })


            
            # Fetch AI response from the server-side GPT service
            ai_response = gpt_service.get_completion(openai_messages) 
            
            # Save the assistant's response to MySQL
            chat_service.add_message(conversation_id, "assistant", ai_response)
            
        # Return response to client
        return jsonify({"status": "success", "reply": ai_response}), 200

    except ValidationError as err:
        prop = err.errors()[0]["loc"][0]
        msg = err.errors()[0]["msg"]
        return jsonify({"error": f"Invalid {prop}: {msg}"}), 400
        
    except Exception as err:
        print("CRITICAL SERVER ERROR:", str(err))
        return jsonify({"error": "An internal server error occurred. Please try again later."}), 500