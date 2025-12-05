"""
StudyBuddy AI - Chat Routes
============================
AI Study Buddy conversational interface.
"""

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import logging
from datetime import datetime
import uuid
import json

from core.database import get_db
from api.models.user import User
from api.models.course import Course
from api.schemas import ChatMessageRequest, ChatMessageResponse
from api.middleware.auth import get_current_user, decode_access_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["AI Chat"])


# Store active conversations (in production, use Redis)
conversations = {}


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    💬 AI STUDY BUDDY CHAT 💬
    
    Send a message to the AI study buddy.
    
    - **message**: Your question or message
    - **course_id**: Optional course context for more relevant answers
    - **conversation_id**: Optional to continue a conversation
    """
    # Get or create conversation
    conv_id = request.conversation_id or str(uuid.uuid4())
    if conv_id not in conversations:
        conversations[conv_id] = []
    
    # Add user message
    user_msg = ChatMessageResponse(
        id=str(uuid.uuid4()),
        role="user",
        content=request.message,
        sources=[],
        timestamp=datetime.utcnow()
    )
    conversations[conv_id].append(user_msg)
    
    # Get course context if provided
    course_context = None
    if request.course_id:
        result = await db.execute(
            select(Course).where(
                Course.id == request.course_id,
                Course.user_id == current_user.id
            )
        )
        course = result.scalar_one_or_none()
        if course:
            course_context = course.name
    
    # Generate response using RAG + LLM
    try:
        from agents.explanation_builder import ExplanationBuilderAgent
        from core.rag import RAGSystem
        
        # Use RAG to find relevant context
        rag = RAGSystem()
        sources = []
        
        if request.course_id:
            relevant_chunks = await rag.query(
                query=request.message,
                course_id=request.course_id,
                top_k=5
            )
            sources = [
                {"source": chunk.get("source", "Course Material"), "page": chunk.get("page")}
                for chunk in relevant_chunks
            ]
        
        # Generate response
        agent = ExplanationBuilderAgent()
        response_text = await agent.answer_question(
            question=request.message,
            context=relevant_chunks if request.course_id else None,
            conversation_history=conversations[conv_id][-5:]  # Last 5 messages
        )
        
    except Exception as e:
        logger.warning(f"Chat response generation failed: {e}")
        # Fallback response
        if course_context:
            response_text = f"I'd be happy to help you with {course_context}! Could you provide more details about what you'd like to learn? I can explain concepts, help with practice problems, or clarify any confusion."
        else:
            response_text = "Hello! I'm your AI Study Buddy. I can help you understand concepts, prepare for exams, and answer questions about your courses. What would you like to learn about today?"
        sources = []
    
    # Create assistant response
    assistant_msg = ChatMessageResponse(
        id=str(uuid.uuid4()),
        role="assistant",
        content=response_text,
        sources=sources,
        timestamp=datetime.utcnow()
    )
    conversations[conv_id].append(assistant_msg)
    
    return assistant_msg


@router.get("/history/{conversation_id}", response_model=List[ChatMessageResponse])
async def get_conversation_history(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get the conversation history.
    """
    if conversation_id not in conversations:
        return []
    
    return conversations[conversation_id]


@router.delete("/history/{conversation_id}")
async def clear_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Clear a conversation history.
    """
    if conversation_id in conversations:
        del conversations[conversation_id]
    
    return {"message": "Conversation cleared"}


# WebSocket for real-time chat
@router.websocket("/ws/{token}")
async def websocket_chat(
    websocket: WebSocket,
    token: str
):
    """
    WebSocket endpoint for real-time chat.
    
    Connect with: ws://host/api/chat/ws/{jwt_token}
    """
    # Validate token
    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=4001)
        return
    
    user_id = payload.get("sub")
    if not user_id:
        await websocket.close(code=4001)
        return
    
    await websocket.accept()
    
    # Create conversation for this session
    conv_id = str(uuid.uuid4())
    conversations[conv_id] = []
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get("message", "")
            course_id = message_data.get("course_id")
            
            # Add user message
            user_msg = {
                "id": str(uuid.uuid4()),
                "role": "user",
                "content": user_message,
                "timestamp": datetime.utcnow().isoformat()
            }
            conversations[conv_id].append(user_msg)
            
            # Send acknowledgment
            await websocket.send_json({
                "type": "user_message",
                "data": user_msg
            })
            
            # Generate response (simplified for WebSocket)
            try:
                from agents.explanation_builder import ExplanationBuilderAgent
                
                agent = ExplanationBuilderAgent()
                response_text = await agent.answer_question(
                    question=user_message,
                    context=None,
                    conversation_history=conversations[conv_id][-5:]
                )
            except Exception:
                response_text = "I'm here to help! What would you like to learn about?"
            
            # Send response
            assistant_msg = {
                "id": str(uuid.uuid4()),
                "role": "assistant",
                "content": response_text,
                "timestamp": datetime.utcnow().isoformat()
            }
            conversations[conv_id].append(assistant_msg)
            
            await websocket.send_json({
                "type": "assistant_message",
                "data": assistant_msg
            })
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=4000)
    finally:
        # Cleanup conversation after disconnect
        if conv_id in conversations:
            del conversations[conv_id]
