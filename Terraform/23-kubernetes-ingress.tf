# --- app-ingress ---
resource "kubernetes_ingress_v1" "app_ingress" {
  metadata {
    name      = "app-ingress"
    namespace = kubernetes_namespace_v1.rybmw_app.metadata[0].name
    annotations = {
      "kubernetes.io/ingress.class"                        = "alb"
      "alb.ingress.kubernetes.io/scheme"                   = "internet-facing"
      "alb.ingress.kubernetes.io/healthcheck-path"         = "/"
      "alb.ingress.kubernetes.io/certificate-arn"          = "arn:aws:acm:eu-north-1:004932907795:certificate/dc4789d8-4c73-43c6-a646-41ff6a60c23b"
      "alb.ingress.kubernetes.io/listen-ports"             = "[{\"HTTP\": 80}, {\"HTTPS\": 443}]"
      "alb.ingress.kubernetes.io/actions.ssl-redirect"     = "{\"Type\": \"redirect\", \"RedirectConfig\": { \"Protocol\": \"HTTPS\", \"Port\": \"443\", \"StatusCode\": \"HTTP_301\"}}"
      "alb.ingress.kubernetes.io/actions.default-redirect" = "{\"Type\": \"redirect\", \"RedirectConfig\": { \"Protocol\": \"HTTPS\", \"Port\": \"443\", \"StatusCode\": \"HTTP_301\"}}"
      "alb.ingress.kubernetes.io/target-type"              = "ip"
    }
  }

  spec {
    ingress_class_name = "alb"
    rule {
      host = "rybmw.space"
      http {
        path {
          path      = "/api/"
          path_type = "Prefix"
          backend {
            service {
              name = kubernetes_service.fastapi_service.metadata[0].name
              port {
                number = kubernetes_service.fastapi_service.spec[0].port[0].port # targets 80 on service
              }
            }
          }
        }
        path {
          path      = "/"
          path_type = "Prefix"
          backend {
            service {
              name = kubernetes_service.nginx_service.metadata[0].name
              port {
                number = kubernetes_service.nginx_service.spec[0].port[0].port # targets 80 on service
              }
            }
          }
        }
      }
    }
  }

  depends_on = [helm_release.aws_lbc]
}