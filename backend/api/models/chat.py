from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index
from core.database import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True)
    conversation_id = Column(String, index=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    course_id = Column(String, ForeignKey("courses.id"), nullable=True)  # Optional context
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Index for fast history retrieval
    __table_args__ = (
        Index('idx_chat_history', 'conversation_id', 'created_at'),
    )
