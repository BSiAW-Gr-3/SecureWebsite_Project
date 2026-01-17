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