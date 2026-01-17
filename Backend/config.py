"""
Configuration settings from environment variables
"""
import os

# AWS Credentials Configuration
AWS_REGION = os.getenv("AWS_REGION", "eu-north-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")

# DynamoDB Configuration
DYNAMODB_ENDPOINT_URL = os.getenv("DYNAMODB_ENDPOINT_URL", None)  # For local DynamoDB
USERS_TABLE = os.getenv("USERS_TABLE", "forum_users")
DEFAULT_CHAT_MESSAGES_TABLE = os.getenv("CHAT_MESSAGES_TABLE", "main")
CHAT_PREFIX = os.getenv("CHAT_PREFIX", "chat_")

# CloudWatch Configuration
CLOUDWATCH_ENDPOINT_URL = os.getenv("CLOUDWATCH_ENDPOINT_URL", None)
CLOUDWATCH_LOG_GROUP = os.getenv("CLOUDWATCH_LOG_GROUP", "API-Logs")
CLOUDWATCH_LOG_STREAM = os.getenv("CLOUDWATCH_LOG_STREAM", "API-Access-Stream")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
