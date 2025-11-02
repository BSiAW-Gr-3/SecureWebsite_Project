resource "kubernetes_secret" "fastapi_secrets" {
  metadata {
    name      = "fastapi-secrets"
    namespace = kubernetes_namespace_v1.rybmw_app.metadata[0].name
  }

  # NOTE: The values must be Base64 encoded.
  data = {
    # JWT Secret Key
    "SECRET_KEY" = "${local.jwt_secret_key}"

    # AWS Credentials (should ideally be retrieved from a secure source like AWS SSM/Secrets Manager)
    "AWS_ACCESS_KEY_ID"     = "${local.aws_access_key}"
    "AWS_SECRET_ACCESS_KEY" = "${local.aws_secret_key}"
  }
}

resource "kubernetes_config_map" "fastapi_config" {
  metadata {
    name      = "fastapi-config"
    namespace = kubernetes_namespace_v1.rybmw_app.metadata[0].name
  }

  data = {
    # AWS Configuration
    "AWS_REGION"            = "${local.region}"
    "DYNAMODB_ENDPOINT_URL" = "" # Use an empty string if not using local DynamoDB

    # DynamoDB Table Names
    "USERS_TABLE"         = "forum_users"
    "CHAT_MESSAGES_TABLE" = "main"

    # JWT Configuration (non-sensitive parts)
    "ACCESS_TOKEN_EXPIRE_MINUTES" = "30"
  }
}