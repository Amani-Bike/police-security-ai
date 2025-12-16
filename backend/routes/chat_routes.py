from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from backend.database.db_setup import get_db
from backend.models.user_model import User
from backend.utils.auth_utils import get_current_user
from backend.models.rag_chain import security_assistant

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[int] = None  # Allow specifying an existing session ID

class ChatResponse(BaseModel):
    reply: str
    is_emergency: bool = False
    emergency_type: Optional[str] = None  # Make this optional

@router.post("/send", response_model=ChatResponse)
def send_chat_message(
    chat_message: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        from backend.models.chat_model import ChatSession, ChatMessage as ChatMessageModel
        from sqlalchemy.exc import IntegrityError
        import datetime

        # Determine session ID to use
        session_id = chat_message.session_id

        if session_id is None:
            # If no session ID provided, use the most recent session or create a default one
            existing_session = db.query(ChatSession).filter(
                ChatSession.user_id == current_user.id
            ).order_by(ChatSession.updated_at.desc()).first()

            if not existing_session:
                # Create a default session if none exists
                default_session = ChatSession(
                    user_id=current_user.id,
                    title="Default Session"
                )
                db.add(default_session)
                db.commit()
                db.refresh(default_session)
                session_id = default_session.id
            else:
                session_id = existing_session.id
        else:
            # Validate that the provided session belongs to the user
            user_session = db.query(ChatSession).filter(
                ChatSession.id == session_id,
                ChatSession.user_id == current_user.id
            ).first()

            if not user_session:
                raise HTTPException(status_code=404, detail="Chat session not found or does not belong to user")

        # Save the user's message to the chat history
        user_chat_message = ChatMessageModel(
            session_id=session_id,
            user_id=current_user.id,
            content=chat_message.message,
            role="user"
        )
        db.add(user_chat_message)
        db.commit()
        db.refresh(user_chat_message)

        # Generate response using RAG
        result = security_assistant.generate_response(chat_message.message)

        # Save the assistant's response to the chat history
        assistant_chat_message = ChatMessageModel(
            session_id=session_id,
            user_id=current_user.id,  # The assistant is still associated with the user's session
            content=result["reply"],
            role="assistant"
        )
        db.add(assistant_chat_message)
        db.commit()
        db.refresh(assistant_chat_message)

        # Log the interaction (optional)
        print(f"Chat from user {current_user.username}: {chat_message.message}")
        print(f"Response type: {'EMERGENCY' if result['is_emergency'] else 'General'}")
        if result.get('emergency_type'):
            print(f"Emergency type: {result['emergency_type']}")

        return ChatResponse(
            reply=result["reply"],
            is_emergency=result["is_emergency"],
            emergency_type=result.get("emergency_type")  # Use .get() to handle None
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"Chat error: {e}")
        return ChatResponse(
            reply="I'm experiencing technical difficulties. Please use the emergency reporting feature for urgent matters or contact Malawi emergency services directly: Police 997, Fire 998, Medical 999.",
            is_emergency=False,
            emergency_type=None
        )

@router.get("/test-rag")
def test_rag_system():
    """Test endpoint to verify RAG system is working"""
    try:
        # Get knowledge base stats
        stats = security_assistant.get_knowledge_base_stats()
        
        test_queries = [
            "What are emergency numbers in Malawi?",
            "What should I do in a domestic violence situation?",
            "How to report a crime to police?",
            "What does the Malawi Penal Code say about theft?",
            "I need help, there's been an accident!",
            "What are my rights if stopped by police?"
        ]
        
        results = []
        for query in test_queries:
            result = security_assistant.generate_response(query)
            results.append({
                "query": query,
                "response": result["reply"],
                "is_emergency": result["is_emergency"],
                "emergency_type": result.get("emergency_type")
            })
        
        return {
            "status": "RAG system is working",
            "knowledge_base_stats": stats,
            "test_results": results
        }
    except Exception as e:
        return {"status": "RAG system error", "error": str(e)}

@router.get("/knowledge-stats")
def get_knowledge_stats():
    """Get statistics about the knowledge base"""
    try:
        return security_assistant.get_knowledge_base_stats()
    except Exception as e:
        return {"error": str(e)}