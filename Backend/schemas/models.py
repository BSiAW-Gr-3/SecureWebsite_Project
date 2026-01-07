"""
DynamoDB Models and Data Access Layer
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from decimal import Decimal
import uuid

class User(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    def to_dynamodb_item(self) -> dict:
        """Convert to DynamoDB item format"""
        return {
            'username': self.username,
            'email': self.email,
            'hashed_password': self.hashed_password,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }

    @classmethod
    def from_dynamodb_item(cls, item: dict) -> 'User':
        """Create User from DynamoDB item"""
        return cls(
            username=item['username'],
            email=item['email'],
            hashed_password=item['hashed_password'],
            created_at=datetime.fromisoformat(item['created_at']),
            is_active=item.get('is_active', True)
        )


class ChatMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    def to_dynamodb_item(self) -> dict:
        """Convert to DynamoDB item format"""
        return {
            'message_id': self.message_id,
            'username': self.username,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'timestamp_sort': Decimal(str(self.timestamp.timestamp()))
        }

    @classmethod
    def from_dynamodb_item(cls, item: dict) -> 'ChatMessage':
        """Create ChatMessage from DynamoDB item"""
        return cls(
            message_id=item['message_id'],
            username=item['username'],
            message=item['message'],
            timestamp=datetime.fromisoformat(item['timestamp'])
        )
