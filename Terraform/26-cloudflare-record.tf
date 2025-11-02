resource "time_sleep" "wait" {
  depends_on      = [helm_release.aws_lbc]
  create_duration = "180s"
}

resource "cloudflare_dns_record" "rybmw_dns_record" {
  zone_id    = local.cloudflare_zone_id
  name       = "rybmw.space"
  ttl        = 1
  type       = "CNAME"
  comment    = "Domain record for rybmw.space pointing to ALB"
  content    = try(kubernetes_ingress_v1.app_ingress.status[0].load_balancer[0].ingress[0].hostname, "")
  proxied    = true
  depends_on = [time_sleep.wait, kubernetes_ingress_v1.app_ingress]

  lifecycle {
    ignore_changes = [content]
    precondition {
      condition     = try(kubernetes_ingress_v1.app_ingress.status[0].load_balancer[0].ingress[0].hostname, null) != null
      error_message = "Ingress load balancer hostname is not yet available. The ALB is still being provisioned. Run 'terraform apply' again after a few minutes."
    }
  }
}