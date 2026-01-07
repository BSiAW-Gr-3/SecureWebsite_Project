"""
Database initialization and connection management for DynamoDB
"""
import boto3
from botocore.exceptions import ClientError
from typing import Optional, List
import asyncio

from config import (
    AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
    DYNAMODB_ENDPOINT_URL, USERS_TABLE, CHAT_MESSAGES_TABLE
)
from schemas.models import User, ChatMessage

class DynamoDBClient:
    def __init__(self):
        session_config = {
            'region_name': AWS_REGION
        }
        
        if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
            session_config['aws_access_key_id'] = AWS_ACCESS_KEY_ID
            session_config['aws_secret_access_key'] = AWS_SECRET_ACCESS_KEY
        
        if DYNAMODB_ENDPOINT_URL:
            session_config['endpoint_url'] = DYNAMODB_ENDPOINT_URL
        
        self.dynamodb = boto3.resource('dynamodb', **session_config)
        self.client = self.dynamodb.meta.client
        self.users_table = self.dynamodb.Table(USERS_TABLE)
        self.messages_table = self.dynamodb.Table(CHAT_MESSAGES_TABLE)
    
    def _create_tables_sync(self):
        """Create DynamoDB tables if they don't exist (synchronous)"""
        # Create Users table
        try:
            self.client.describe_table(TableName=USERS_TABLE)
            print(f"Table {USERS_TABLE} already exists")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                self.client.create_table(
                    TableName=USERS_TABLE,
                    KeySchema=[
                        {'AttributeName': 'username', 'KeyType': 'HASH'}
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'username', 'AttributeType': 'S'},
                        {'AttributeName': 'email', 'AttributeType': 'S'}
                    ],
                    GlobalSecondaryIndexes=[
                        {
                            'IndexName': 'email-index',
                            'KeySchema': [
                                {'AttributeName': 'email', 'KeyType': 'HASH'}
                            ],
                            'Projection': {'ProjectionType': 'ALL'},
                            'ProvisionedThroughput': {
                                'ReadCapacityUnits': 5,
                                'WriteCapacityUnits': 5
                            }
                        }
                    ],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                )
                print(f"Created table {USERS_TABLE}")
                # Wait for table to be active
                waiter = self.client.get_waiter('table_exists')
                waiter.wait(TableName=USERS_TABLE)
        
        # Create ChatMessages table
        try:
            self.client.describe_table(TableName=CHAT_MESSAGES_TABLE)
            print(f"Table {CHAT_MESSAGES_TABLE} already exists")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                self.client.create_table(
                    TableName=CHAT_MESSAGES_TABLE,
                    KeySchema=[
                        {'AttributeName': 'message_id', 'KeyType': 'HASH'}
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'message_id', 'AttributeType': 'S'},
                        {'AttributeName': 'timestamp_sort', 'AttributeType': 'N'}
                    ],
                    GlobalSecondaryIndexes=[
                        {
                            'IndexName': 'timestamp-index',
                            'KeySchema': [
                                {'AttributeName': 'message_id', 'KeyType': 'HASH'},
                                {'AttributeName': 'timestamp_sort', 'KeyType': 'RANGE'}
                            ],
                            'Projection': {'ProjectionType': 'ALL'},
                            'ProvisionedThroughput': {
                                'ReadCapacityUnits': 5,
                                'WriteCapacityUnits': 5
                            }
                        }
                    ],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                )
                print(f"Created table {CHAT_MESSAGES_TABLE}")
                # Wait for table to be active
                waiter = self.client.get_waiter('table_exists')
                waiter.wait(TableName=CHAT_MESSAGES_TABLE)
    
    async def create_tables(self):
        """Create DynamoDB tables if they don't exist (async wrapper)"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._create_tables_sync)
    
    # User operations
    def _create_user_sync(self, user: User) -> User:
        """Create a new user (synchronous)"""
        item = user.to_dynamodb_item()
        print(f"Attempting to create user: {item}")
        try:
            response = self.users_table.put_item(Item=item)
            print(f"DynamoDB put_item response: {response}")
            return user
        except Exception as e:
            print(f"Error creating user: {e}")
            raise
    
    async def create_user(self, user: User) -> User:
        """Create a new user"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._create_user_sync, user)
    
    def _get_user_by_username_sync(self, username: str) -> Optional[User]:
        """Get user by username (synchronous)"""
        try:
            response = self.users_table.get_item(Key={'username': username})
            if 'Item' in response:
                return User.from_dynamodb_item(response['Item'])
            return None
        except ClientError as e:
            print(f"Error getting user by username: {e}")
            return None
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_user_by_username_sync, username)
    
    def _get_user_by_email_sync(self, email: str) -> Optional[User]:
        """Get user by email using GSI (synchronous)"""
        try:
            response = self.users_table.query(
                IndexName='email-index',
                KeyConditionExpression='email = :email',
                ExpressionAttributeValues={':email': email}
            )
            if response['Items']:
                return User.from_dynamodb_item(response['Items'][0])
            return None
        except ClientError as e:
            print(f"Error getting user by email: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email using GSI"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_user_by_email_sync, email)
    
    # Chat message operations
    def _create_message_sync(self, message: ChatMessage) -> ChatMessage:
        """Create a new chat message (synchronous)"""
        item = message.to_dynamodb_item()
        try:
            self.messages_table.put_item(Item=item)
            return message
        except Exception as e:
            print(f"Error creating message: {e}")
            raise
    
    async def create_message(self, message: ChatMessage) -> ChatMessage:
        """Create a new chat message"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._create_message_sync, message)
    
    def _get_recent_messages_sync(self, limit: int = 50) -> List[ChatMessage]:
        """Get recent chat messages (synchronous)"""
        try:
            response = self.messages_table.scan(Limit=limit * 2)  # Get more to sort
            items = response['Items']
            
            # Sort by timestamp (descending)
            items.sort(key=lambda x: float(x['timestamp_sort']), reverse=True)
            items = items[:limit]
            
            # Convert to ChatMessage objects and reverse for chronological order
            messages = [ChatMessage.from_dynamodb_item(item) for item in items]
            messages.reverse()
            return messages
        except ClientError as e:
            print(f"Error getting recent messages: {e}")
            return []
    
    async def get_recent_messages(self, limit: int = 50) -> List[ChatMessage]:
        """Get recent chat messages"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_recent_messages_sync, limit)

# Global database client instance
db_client: Optional[DynamoDBClient] = None

async def init_db():
    """Initialize database connection"""
    global db_client
    db_client = DynamoDBClient()
    await db_client.create_tables()
    print("Database initialized successfully")
    return db_client

def get_db() -> DynamoDBClient:
    """Get database client instance"""
    if db_client is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return db_client