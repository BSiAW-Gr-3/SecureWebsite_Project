"""
CloudWatch logger handler for asynchronous logging
"""
from botocore.exceptions import ClientError
from typing import Optional
from functools import wraps
import asyncio
import boto3
import time

from config import (
    AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, 
    CLOUDWATCH_LOG_GROUP, CLOUDWATCH_LOG_STREAM, CLOUDWATCH_ENDPOINT_URL
)

def async_wrap(func):
    """Decorator to run sync functions in executor for async compatibility"""
    @wraps(func)
    async def run(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    return run


class CloudWatchClient():
    def __init__(self):
        session_config = {
            'region_name': AWS_REGION
        }
        
        if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
            session_config['aws_access_key_id'] = AWS_ACCESS_KEY_ID
            session_config['aws_secret_access_key'] = AWS_SECRET_ACCESS_KEY
        
        if CLOUDWATCH_ENDPOINT_URL: 
            session_config['endpoint_url'] = CLOUDWATCH_ENDPOINT_URL

        self.logs_client = boto3.client('logs', **session_config)
        self.log_group_name = CLOUDWATCH_LOG_GROUP
        self.log_stream_name = CLOUDWATCH_LOG_STREAM

    @async_wrap
    def initialize_logs(self):
        """Create log group and stream if they don't exist"""
        try:
            self.logs_client.create_log_group(logGroupName=self.log_group_name)
            print(f"Created log group: {self.log_group_name}")
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                raise

        try:
            self.logs_client.create_log_stream(
                logGroupName=self.log_group_name, 
                logStreamName=self.log_stream_name
            )
            print(f"Created log stream: {self.log_stream_name}")
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                raise

    @async_wrap
    def send_log(self, message: str):
        """Send a single log event to CloudWatch"""
        try:
            self.logs_client.put_log_events(
                logGroupName=self.log_group_name,
                logStreamName=self.log_stream_name,
                logEvents=[
                    {
                        'timestamp': int(round(time.time() * 1000)),
                        'message': message
                    }
                ]
            )
        except ClientError as e:
            print(f"Failed to send log to CloudWatch: {e}")


cloudwatch_client: Optional[CloudWatchClient] = CloudWatchClient()

async def init_logger():
    """Initialize CloudWatch logger"""
    if cloudwatch_client is None:
        raise Exception("CloudWatch client is not initialized")
    
    await cloudwatch_client.initialize_logs()
    
async def log_message(message: str):
    """Log a message to CloudWatch"""
    if cloudwatch_client is None:
        raise Exception("CloudWatch client is not initialized")
    
    await cloudwatch_client.send_log(message)
