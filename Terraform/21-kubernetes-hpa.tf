# --- fastapi-hpa ---
resource "kubernetes_horizontal_pod_autoscaler_v2" "fastapi_hpa" {
  metadata {
    name      = "fastapi-hpa"
    namespace = kubernetes_namespace_v1.rybmw_app.metadata[0].name
  }

  spec {
    scale_target_ref {
      api_version = "apps/v1"
      kind        = "Deployment"
      name        = kubernetes_deployment.fastapi_deployment.metadata[0].name
    }
    min_replicas = 1
    max_replicas = 5
    metric {
      type = "Resource"
      resource {
        name = "cpu"
        target {
          type                = "Utilization"
          average_utilization = 50
        }
      }
    }
  }
}

# --- nodejs-hpa ---
resource "kubernetes_horizontal_pod_autoscaler_v2" "nginx_hpa" {
  metadata {
    name      = "nginx-hpa"
    namespace = kubernetes_namespace_v1.rybmw_app.metadata[0].name
  }

  spec {
    scale_target_ref {
      api_version = "apps/v1"
      kind        = "Deployment"
      name        = kubernetes_deployment.nginx_deployment.metadata[0].name
    }
    min_replicas = 2
    max_replicas = 10
    metric {
      type = "Resource"
      resource {
        name = "cpu"
        target {
          type                = "Utilization"
          average_utilization = 80
        }
      }
    }
  }
}
