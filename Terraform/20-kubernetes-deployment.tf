# --- fastapi-deployment ---
resource "kubernetes_deployment" "fastapi_deployment" {
  metadata {
    name = "fastapi-deployment"
    labels = {
      app = "fastapi-app"
    }
  }

  spec {
    replicas = 2
    selector {
      match_labels = {
        app = "fastapi-app"
      }
    }
    template {
      metadata {
        labels = {
          app = "fastapi-app"
        }
      }
      spec {
        container {
          name  = "fastapi-container"
          image = "004932907795.dkr.ecr.eu-north-1.amazonaws.com/rybmw/api:latest"

          port {
            container_port = 8000
          }

          env {
            # --- FROM CONFIGMAP (fastapi-config) ---
            name = "AWS_REGION"
            value_from {
              config_map_key_ref {
                name = kubernetes_config_map.fastapi_config.metadata[0].name
                key  = "AWS_REGION"
              }
            }
          }
          env {
            name = "USERS_TABLE"
            value_from {
              config_map_key_ref {
                name = kubernetes_config_map.fastapi_config.metadata[0].name
                key  = "USERS_TABLE"
              }
            }
          }
          # ... (Add other ConfigMap variables: DYNAMODB_ENDPOINT_URL, CHAT_MESSAGES_TABLE, ACCESS_TOKEN_EXPIRE_MINUTES)
          env {
            name = "DYNAMODB_ENDPOINT_URL"
            value_from {
              config_map_key_ref {
                name = kubernetes_config_map.fastapi_config.metadata[0].name
                key  = "DYNAMODB_ENDPOINT_URL"
              }
            }
          }
          env {
            name = "CHAT_MESSAGES_TABLE"
            value_from {
              config_map_key_ref {
                name = kubernetes_config_map.fastapi_config.metadata[0].name
                key  = "CHAT_MESSAGES_TABLE"
              }
            }
          }
          env {
            name = "ACCESS_TOKEN_EXPIRE_MINUTES"
            value_from {
              config_map_key_ref {
                name = kubernetes_config_map.fastapi_config.metadata[0].name
                key  = "ACCESS_TOKEN_EXPIRE_MINUTES"
              }
            }
          }

          # --- FROM SECRET (fastapi-secrets) ---
          env {
            name = "SECRET_KEY"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.fastapi_secrets.metadata[0].name
                key  = "SECRET_KEY"
              }
            }
          }
          # ... (Add other Secret variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
          env {
            name = "AWS_ACCESS_KEY_ID"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.fastapi_secrets.metadata[0].name
                key  = "AWS_ACCESS_KEY_ID"
              }
            }
          }
          env {
            name = "AWS_SECRET_ACCESS_KEY"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.fastapi_secrets.metadata[0].name
                key  = "AWS_SECRET_ACCESS_KEY"
              }
            }
          }

          resources {
            requests = {
              cpu    = "100m"
              memory = "128Mi"
            }
            limits = {
              cpu    = "250m"
              memory = "512Mi"
            }
          }
        }
      }
    }
  }
}

# --- nodejs-deployment ---
resource "kubernetes_deployment" "nginx_deployment" {
  metadata {
    name = "nginx-deployment"
    labels = {
      app = "nginx-app"
    }
  }

  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "nginx-app"
      }
    }
    template {
      metadata {
        labels = {
          app = "nginx-app"
        }
      }
      spec {
        container {
          name  = "nginx-container"
          image = "004932907795.dkr.ecr.eu-north-1.amazonaws.com/rybmw/front:latest"

          port {
            container_port = 8080
          }

          resources {
            requests = {
              cpu    = "100m"
              memory = "128Mi"
            }
            limits = {
              cpu    = "300m"
              memory = "256Mi"
            }
          }
        }
      }
    }
  }
}