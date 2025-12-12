from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict
import json
import logging
import uuid
from datetime import datetime

from core.database import get_db
from api.models.user import User
from api.models.course import Course
from api.models.chat import ChatMessage
from api.schemas import ChatMessageRequest, ChatMessageResponse
from api.middleware.auth import get_current_user, decode_access_token

# Import Agent and VectorStore safely
from agents.explanation_builder import ExplanationBuilderAgent
from core.vector_store import get_vector_store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])

# WebSocket connection manager (simplified)
conversations: Dict[str, List[dict]] = {}

@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message to the AI and get a response.
    """
    # 1. Get or Create Conversation ID
    conv_id = request.conversation_id or str(uuid.uuid4())
    
    # 2. Save User Message
    user_msg_entry = ChatMessage(
        id=str(uuid.uuid4()),
        conversation_id=conv_id,
        user_id=current_user.id,
        course_id=request.course_id,
        role="user",
        content=request.message,
        created_at=datetime.utcnow()
    )
    db.add(user_msg_entry)
    await db.commit()
    
    # 3. Get History for Context
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conv_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(10)
    )
    history_msgs = result.scalars().all()
    
    history_dicts = [
        {"role": m.role, "content": m.content} for m in history_msgs
    ]
    
    # 4. Generate AI Response
    response_text = ""
    sources = []
    
    try:
        agent = ExplanationBuilderAgent()
        vector_store = get_vector_store()
        
        # RAG Search - ONLY within user's own courses
        relevant_chunks = []
        
        if request.course_id:
            # Course-specific search - verify user owns this course first
            course_check = await db.execute(
                select(Course).where(
                    Course.id == request.course_id,
                    Course.user_id == current_user.id
                )
            )
            if course_check.scalar_one_or_none():
                relevant_chunks = vector_store.search(
                    course_id=request.course_id,
                    query=request.message,
                    top_k=3
                )
        else:
            # Global search - but ONLY user's courses
            user_courses = await db.execute(
                select(Course.id).where(Course.user_id == current_user.id)
            )
            user_course_ids = [c[0] for c in user_courses.fetchall()]
            
            # Search each user's course and combine results
            all_results = []
            for course_id in user_course_ids:
                course_results = vector_store.search(
                    course_id=course_id,
                    query=request.message,
                    top_k=3
                )
                all_results.extend(course_results)
            
            # Sort by score and take top results
            all_results.sort(key=lambda x: x.get("score", 0), reverse=True)
            relevant_chunks = all_results[:3]
        
        # Format retrieval context
        context_str_list = [c.get('text', '') for c in relevant_chunks]
        
        response_text = await agent.answer_question(
            question=request.message,
            context=context_str_list,
            conversation_history=history_dicts
        )
        
        # Format sources for UI
        sources = [
            {"title": c.get("source", "Material"), "preview": c.get("text", "")[:50] + "..."}
            for c in relevant_chunks
        ]
        
    except Exception as e:
        import traceback
        logger.error(f"AI Generation Failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        response_text = f"I'm having trouble connecting to my brain right now. Error: {str(e)[:100]}"
    
    # 5. Save AI Message
    ai_msg_entry = ChatMessage(
        id=str(uuid.uuid4()),
        conversation_id=conv_id,
        user_id=current_user.id,
        course_id=request.course_id,
        role="assistant",
        content=response_text,
        created_at=datetime.utcnow()
    )
    db.add(ai_msg_entry)
    await db.commit()
    
    return ChatMessageResponse(
        id=ai_msg_entry.id,
        role="assistant",
        content=response_text,
        sources=sources,
        timestamp=ai_msg_entry.created_at,
        conversation_id=conv_id
    )

@router.get("/history", response_model=List[ChatMessageResponse])
async def get_chat_history(
    course_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get chat history for a user (optionally filtered by course).
    """
    query = select(ChatMessage).where(ChatMessage.user_id == current_user.id)
    if course_id:
        query = query.where(ChatMessage.course_id == course_id)
        
    query = query.order_by(ChatMessage.created_at.desc()).limit(50)
    
    result = await db.execute(query)
    messages = result.scalars().all()
    
    # Reverse to chronological order
    messages = list(reversed(messages))
    
    return [
        ChatMessageResponse(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            sources=[], 
            timestamp=msg.created_at,
            conversation_id=msg.conversation_id
        )
        for msg in messages
    ]

# WebSocket endpoint (Optional, keeping for compatibility if frontend uses it)
@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    await websocket.close(code=1000, reason="Use REST API instead")
