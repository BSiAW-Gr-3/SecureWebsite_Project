data "aws_eks_cluster" "cluster" {
  name = "${local.env}-${local.eks_name}"

  depends_on = [aws_eks_cluster.eks]
}

data "aws_eks_cluster_auth" "cluster" {
  name = "${local.env}-${local.eks_name}"

  depends_on = [aws_eks_cluster.eks]
}

provider "kubernetes" {
  host                   = data.aws_eks_cluster.cluster.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.cluster.token
}