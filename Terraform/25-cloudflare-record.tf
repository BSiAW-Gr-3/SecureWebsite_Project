resource "time_sleep" "wait_60_seconds" {
  depends_on = [ helm_release.aws_lbc ]
  create_duration = "60s"
}

resource "cloudflare_dns_record" "rybmw_dns_record" {
  zone_id = "${local.cloudflare_zone_id}"
  name = "rybmw.space"
  ttl = 1
  type = "CNAME"
  comment = "Domain record for rybmw.space pointing to ALB"
  content = "${kubernetes_ingress_v1.app_ingress.status[0].load_balancer[0].ingress[0].hostname}"
  proxied = false
  depends_on = [ time_sleep.wait_60_seconds ]
}