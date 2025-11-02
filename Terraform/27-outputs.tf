output "alb_dns_name" {
  description = "The DNS name of the ALB Ingress - Paste it into DNS Alias Record in Domain Name Provider"
  value       = try(kubernetes_ingress_v1.app_ingress.status[0].load_balancer[0].ingress[0].hostname, "ALB not yet provisioned - run terraform apply again")

  depends_on = [time_sleep.wait]
}

output "kubeconfig_command" {
  description = "Accessing Kubernetes Cluster"
  value       = "aws eks update-kubeconfig --region ${local.region} --name ${local.env}-${local.eks_name}"
}

output "login_ecr_command" {
  description = "Command to login into ECR"
  value       = "aws ecr get-login-password --region ${local.region} | docker login --username AWS --password-stdin 004932907795.dkr.ecr.${local.region}.amazonaws.com"
}

output "ecr_repository_frontend_url" {
  description = "ECR Repository URL - Frontend"
  value       = "004932907795.dkr.ecr.eu-north-1.amazonaws.com/rybmw/front:latest"
}
output "ecr_repository_backend_url" {
  description = "ECR Repository URL - Backend"
  value       = "004932907795.dkr.ecr.eu-north-1.amazonaws.com/rybmw/api:latest"
}

output "update_image" {
  description = "Command to update image in ECR"
  value       = "docker buildx build --platform linux/amd64,linux/arm64 -t {REPO} --push ."
}

output "check_website" {
  description = "Check access to the website without DNS"
  value       = try(kubernetes_ingress_v1.app_ingress.status[0].load_balancer[0].ingress[0].hostname, null) != null ? "curl -i --header \"Host: rybmw.space\" ${kubernetes_ingress_v1.app_ingress.status[0].load_balancer[0].ingress[0].hostname}" : "ALB not yet provisioned - run terraform apply again"

  depends_on = [time_sleep.wait]
}

output "check_dns" {
  description = "Check if DNS is properly configured"
  value       = "dig rybmw.space @8.8.8.8"
} 