data "http" "my_ip" {
  url = "https://ipv4.icanhazip.com"
}

locals {
  # AWS Credentials and Region
  region         = "eu-north-1"
  aws_access_key = ""
  aws_secret_key = ""

  # Environment and EKS settings
  env         = "dev"
  zone1       = "eu-north-1a"
  zone2       = "eu-north-1b"
  eks_name    = "rybmw"
  eks_version = "1.34"

  # JWT Secret Key
  jwt_secret_key = ""

  # Cloudflare API Token
  cloudflare_zone_id   = ""
  cloudflare_api_token = ""

  # Your local CIDR block
  cidr_block = "${chomp(data.http.my_ip.body)}/32"
}
