# --- fastapi-service ---
resource "kubernetes_service" "fastapi_service" {
  metadata {
    name      = "fastapi-service"
    namespace = kubernetes_namespace_v1.rybmw_app.metadata[0].name
  }
  spec {
    selector = {
      app = kubernetes_deployment.fastapi_deployment.metadata[0].labels.app
    }
    port {
      protocol    = "TCP"
      port        = 80
      target_port = 8000
    }
    type = "ClusterIP"
  }
}

# --- nodejs-service ---
resource "kubernetes_service" "nginx_service" {
  metadata {
    name      = "nginx-service"
    namespace = kubernetes_namespace_v1.rybmw_app.metadata[0].name
  }
  spec {
    selector = {
      app = kubernetes_deployment.nginx_deployment.metadata[0].labels.app
    }
    port {
      protocol    = "TCP"
      port        = 80
      target_port = 8080
    }
    type = "ClusterIP"
  }
}

