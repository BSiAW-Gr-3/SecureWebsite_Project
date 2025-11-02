resource "kubernetes_namespace_v1" "rybmw_app" {
  metadata {
    name = "rybmw-app"
    labels = {
      "pod-security.kubernetes.io/enforce" = "restricted"
    }
  }
}

resource "kubernetes_service_account_v1" "default_sa_rybmw_app" {
  metadata {
    name      = "rybmw-app-service-account"
    namespace = kubernetes_namespace_v1.rybmw_app.metadata[0].name
  }
  automount_service_account_token = false

  depends_on = [kubernetes_namespace_v1.rybmw_app]
}