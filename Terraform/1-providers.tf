provider "aws" {
  region     = local.region
  access_key = local.aws_access_key
  secret_key = local.aws_secret_key
}

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.53"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 5"
    }
  }
}
