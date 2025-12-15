resource "aws_dynamodb_table" "users" {
  name           = "forum_users"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5

  hash_key = "username"

  attribute {
    name = "username"
    type = "S" # String
  }
  attribute {
    name = "email"
    type = "S" # String
  }

  global_secondary_index {
    name            = "email-index"
    hash_key        = "email"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }
}

resource "aws_dynamodb_table" "chat_messages" {
  name           = "forum_chat_messages"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5

  hash_key = "message_id"

  attribute {
    name = "message_id"
    type = "S" # String
  }
  attribute {
    name = "timestamp_sort"
    type = "N" # Number
  }

  global_secondary_index {
    hash_key           = "message_id"
    name               = "timestamp-index"
    non_key_attributes = []
    projection_type    = "ALL"
    range_key          = "timestamp_sort"
    read_capacity      = 5
    write_capacity     = 5
  }
}