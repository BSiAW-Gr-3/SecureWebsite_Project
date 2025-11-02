"""
Database initialization and connection management for DynamoDB
"""
from botocore.exceptions import ClientError
from typing import Optional, List
import asyncio
import boto3

from schemas.models import User, ChatMessage
from config import (
    AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
    DYNAMODB_ENDPOINT_URL, USERS_TABLE, DEFAULT_CHAT_MESSAGES_TABLE, CHAT_PREFIX
)

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
    

    def _create_users_tables_sync(self):
        """Create Users table and wait until active"""
        try:
            self.client.describe_table(TableName=USERS_TABLE)
            print(f"Table {USERS_TABLE} already exists")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"Creating table {USERS_TABLE}...")
                self.client.create_table(
                    TableName=USERS_TABLE,
                    KeySchema=[{'AttributeName': 'username', 'KeyType': 'HASH'}],
                    AttributeDefinitions=[
                        {'AttributeName': 'username', 'AttributeType': 'S'},
                        {'AttributeName': 'email', 'AttributeType': 'S'}
                    ],
                    GlobalSecondaryIndexes=[
                        {
                            'IndexName': 'email-index',
                            'KeySchema': [{'AttributeName': 'email', 'KeyType': 'HASH'}],
                            'Projection': {'ProjectionType': 'ALL'},
                            'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                        }
                    ],
                    ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                )

                waiter = self.client.get_waiter('table_exists')
                waiter.wait(TableName=USERS_TABLE, WaiterConfig={'Delay': 1, 'MaxAttempts': 20})
                print(f"Table {USERS_TABLE} is now ACTIVE")

    async def create_users_tables(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._create_users_tables_sync)
    

    def _create_chat_tables_sync(self, chat: str):
        """Create a new chat messages table and WAIT until it's ACTIVE"""
        table_name = f"{CHAT_PREFIX}{chat}"
        
        try:
            self.client.describe_table(TableName=table_name)
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"Creating chat table {table_name}...")
                self.client.create_table(
                    TableName=table_name,
                    KeySchema=[{'AttributeName': 'message_id', 'KeyType': 'HASH'}],
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
                            'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                        }
                    ],
                    ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                )

                print(f"Waiting for {table_name} to become active...")
                waiter = self.client.get_waiter('table_exists')
                waiter.wait(TableName=table_name, WaiterConfig={'Delay': 2, 'MaxAttempts': 30})
                print(f"Table {table_name} is now READY.")
                
    async def create_chat_tables(self, chat: str):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._create_chat_tables_sync, chat)


    def _check_table_status_sync(self, chat: str) -> str:
        """
        Checks the status of a chat table and its indexes.
        Returns: 'ACTIVE', 'CREATING', or 'NOT_FOUND'
        """
        table_name = f"{CHAT_PREFIX}{chat}"
        
        try:
            response = self.client.describe_table(TableName=table_name)
            table_data = response['Table']
            
            if table_data['TableStatus'] != 'ACTIVE':
                return table_data['TableStatus']

            gsis = table_data.get('GlobalSecondaryIndexes', [])
            for gsi in gsis:
                if gsi['IndexStatus'] != 'ACTIVE':
                    return "CREATING" 

            return "ACTIVE"
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                return "CREATING"
            raise

    async def check_table_status(self, chat: str) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._check_table_status_sync, chat)


    def _get_chat_tables_sync(self) -> List[str]:
        """
        Retrieves a list of chat tables starting with CHAT_PREFIX.
        """
        try:
            response = self.client.list_tables()
            tables = response.get('TableNames', [])
            return [table for table in tables if table.startswith(CHAT_PREFIX)]
        except ClientError:
            return []
        
    async def get_chat_tables(self) -> List[str]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_chat_tables_sync)


    def _create_user_sync(self, user: User) -> User:
        """Creates a new user in the users table."""
        item = user.to_dynamodb_item()
        self.users_table.put_item(Item=item)
        return user
    
    async def create_user(self, user: User) -> User:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._create_user_sync, user)
    

    def _get_user_by_username_sync(self, username: str) -> Optional[User]:
        """Retrieves a user by their username."""
        response = self.users_table.get_item(Key={'username': username})
        if 'Item' in response:
            return User.from_dynamodb_item(response['Item'])
        return None
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_user_by_username_sync, username)
    

    def _get_user_by_email_sync(self, email: str) -> Optional[User]:
        """Retrieves a user by their email."""
        response = self.users_table.query(
            IndexName='email-index',
            KeyConditionExpression='email = :email',
            ExpressionAttributeValues={':email': email}
        )
        if response['Items']:
            return User.from_dynamodb_item(response['Items'][0])
        return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_user_by_email_sync, email)
    

    def _create_message_sync(self, message: ChatMessage, chat: str) -> ChatMessage:
        """Creates a new chat message in the specified chat table."""
        table_name = f"{CHAT_PREFIX}{chat}"
        table = self.dynamodb.Table(table_name)
        item = message.to_dynamodb_item()
        
        try:
            table.put_item(Item=item)
            return message
        except ClientError as e:
            raise e
    
    async def create_message(self, message: ChatMessage, chat: str) -> ChatMessage:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._create_message_sync, message, chat)
    

    def _get_recent_messages_sync(self, chat: str, limit: int = 50) -> List[ChatMessage]:
        """Retrieves recent messages from a chat table."""
        table_name = f"{CHAT_PREFIX}{chat}"

        try:
            self.client.describe_table(TableName=table_name)
            table = self.dynamodb.Table(table_name)
            response = table.scan(Limit=limit * 2)
            items = response['Items']
            items.sort(key=lambda x: float(x['timestamp_sort']), reverse=True)
            items = items[:limit]
            messages = [ChatMessage.from_dynamodb_item(item) for item in items]
            messages.reverse()
            return messages
        except ClientError:
            return []
    
    async def get_recent_messages(self, chat: str, limit: int = 50) -> List[ChatMessage]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_recent_messages_sync, chat, limit)


db_client: Optional[DynamoDBClient] = None

async def init_db():
    """Initialize the DynamoDB client and create necessary tables."""
    global db_client
    db_client = DynamoDBClient()
    await db_client.create_users_tables()
    await db_client.create_chat_tables(DEFAULT_CHAT_MESSAGES_TABLE)
    return db_client

def get_db() -> DynamoDBClient:
    """Get the initialized DynamoDB client."""
    if db_client is None:
        raise RuntimeError("Database not initialized.")
    return db_client