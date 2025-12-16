from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

from backend.database.db_setup import get_db
from backend.models.user_model import User
from backend.models.chat_model import ChatSession, ChatMessage
from backend.schemas.chat_schemas import (
    ChatSessionCreate, ChatSessionUpdate, 
    ChatMessageCreate, ChatSessionResponse, 
    ChatMessageResponse, ChatHistoryResponse
)
from backend.utils.auth_utils import get_current_user

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/sessions", response_model=ChatSessionResponse)
def create_chat_session(
    session: ChatSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new chat session for the current user
    """
    try:
        db_session = ChatSession(
            user_id=current_user.id,
            title=session.title
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        
        logger.info(f"Created new chat session {db_session.id} for user {current_user.id}")
        return db_session
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error creating chat session")
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating chat session: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/sessions", response_model=List[ChatSessionResponse])
def get_user_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all chat sessions for the current user
    """
    try:
        sessions = db.query(ChatSession).filter(
            ChatSession.user_id == current_user.id
        ).order_by(ChatSession.updated_at.desc()).all()
        
        logger.info(f"Retrieved {len(sessions)} chat sessions for user {current_user.id}")
        return sessions
    except Exception as e:
        logger.error(f"Error retrieving chat sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/sessions/{session_id}", response_model=ChatHistoryResponse)
def get_chat_history(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get chat history for a specific session
    """
    try:
        # Verify session belongs to user
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # Get all messages for this session
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.timestamp.asc()).all()
        
        logger.info(f"Retrieved {len(messages)} messages for session {session_id}")
        
        return ChatHistoryResponse(
            session=session,
            messages=messages
        )
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
def add_chat_message(
    session_id: int,
    message: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a message to a chat session
    """
    try:
        # Verify session belongs to user
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # Validate role
        if message.role not in ["user", "assistant"]:
            raise HTTPException(status_code=400, detail="Role must be 'user' or 'assistant'")
        
        # Create the message
        db_message = ChatMessage(
            session_id=session_id,
            user_id=current_user.id,
            content=message.content,
            role=message.role
        )
        
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        
        logger.info(f"Added message to session {session_id}, message ID: {db_message.id}")
        return db_message
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error adding message to chat")
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding message to chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/sessions/{session_id}", response_model=ChatSessionResponse)
def update_chat_session(
    session_id: int,
    session_update: ChatSessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a chat session (e.g., change title)
    """
    try:
        # Find the session
        db_session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        ).first()
        
        if not db_session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # Update fields
        if session_update.title is not None:
            db_session.title = session_update.title
        
        db.commit()
        db.refresh(db_session)
        
        logger.info(f"Updated session {session_id}")
        return db_session
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error updating chat session")
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating chat session: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/sessions/{session_id}")
def delete_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a chat session and all its messages
    """
    try:
        # Find the session
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # Delete all messages in this session
        db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
        
        # Delete the session
        db.delete(session)
        db.commit()
        
        logger.info(f"Deleted session {session_id} and its messages")
        return {"message": "Chat session deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting chat session: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/sessions/{session_id}/messages/{message_id}")
def delete_chat_message(
    session_id: int,
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific message from a chat session
    """
    try:
        # Verify session belongs to user
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # Find and delete the message
        message = db.query(ChatMessage).filter(
            ChatMessage.id == message_id,
            ChatMessage.session_id == session_id
        ).first()
        
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        db.delete(message)
        db.commit()
        
        logger.info(f"Deleted message {message_id} from session {session_id}")
        return {"message": "Message deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting message: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")