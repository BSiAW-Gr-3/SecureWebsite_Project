# 🚘 ryBMW Forum Application

This repository contains the source code and infrastructure definitions for a real-time chat application, built using FastAPI and React, and deployed to Amazon EKS.

## 🌟 Tech Stack and Architecture

The application follows a standard microservice architecture deployed via Kubernetes (EKS):

| Component       | Technology              | Role                                                                                                              |
| :-------------- | :---------------------- | :---------------------------------------------------------------------------------------------------------------- |
| **Frontend**    | **React (Vite)**, Nginx | Single-Page Application (SPA) served by Nginx.                                                                    |
| **Backend API** | **FastAPI (Python)**    | Provides REST endpoints for authentication (JWT) and a secure WebSocket (`/api/ws/chat`) for real-time messaging. |
| **Database**    | **AWS DynamoDB**        | Stores user data (`forum_users`) and chat messages (`forum_chat_messages`).                                       |
| **Networking**  | **AWS ALB Ingress**     | Routes traffic for the domain `rybmw.space`.                                                                      |

---

## ☁️ EKS Deployment (Terraform)

The infrastructure is defined in the `Terraform/` directory. The cluster name is configured as **`dev-rybmw`**.

### Prerequisites

1.  **AWS Credentials:** Set your `local.aws_access_key` and `local.aws_secret_key` in `Terraform/0-locals.tf` in 0-locals.tf.
2.  **Container Images:** Ensure the images are built and pushed to the specified ECR path (e.g., `004932907795.dkr.ecr.eu-north-1.amazonaws.com/rybmw/api:latest`).

### Deployment Steps

Navigate to the `Terraform/` directory:

1.  **Initialize Terraform:**
    ```bash
    terraform init
    ```
2.  **Apply Changes:**

    ```bash
    terraform apply
    ```

3.  **Configure DNS**
    ```
    In our case go to NameCheap and add ALIAS record for ALB (printed in output of terraform)
    ```

---

## 🔥 Critical Infrastructure Destruction Procedure

Destroying an EKS cluster requires precise ordering to avoid dependency lock errors (especially with the AWS Load Balancer Controller). Follow these steps exactly to ensure a clean teardown.

### Phase 1: Manual Kubernetes Cleanup

You must manually delete the Ingress resource and wait for the Application Load Balancer (ALB) to de-provision before Terraform can destroy the VPC components.

1.  **Ensure `kubectl` is configured** for the `dev-rybmw` cluster.
2.  **Delete the Ingress** (triggers ALB deletion):

    ```bash
    kubectl delete -n rybmw-app ingress app-ingress

    # Optional: Delete other resources to prevent issues
    kubectl delete -n rybmw-app deployment fastapi-deployment nginx-deployment
    kubectl delete -n rybmw-app service fastapi-service nginx-service
    kubectl delete -n rybmw-app hpa fastapi-hpa nginx-hpa
    ```

3.  **WAIT 5 MINUTES.** The ALB deletion is asynchronous and mandatory before continuing.

### Phase 2: Targeted Terraform Destroy (Kubernetes Components)

Run this targeted command from the `Terraform/` directory to force the destruction of Helm releases, IAM associations, and Access Entries, which often block the main EKS cluster deletion.

```bash
# This command targets EKS-dependent components in a safe order.
terraform destroy -target="helm_release.aws_lbc" \
                  -target="aws_eks_pod_identity_association.aws_lbc" \
                  -target="helm_release.cluster_autoscaler" \
                  -target="aws_eks_pod_identity_association.cluster_autoscaler" \
                  -target="helm_release.metrics_server" \
                  -target="aws_eks_access_entry.developer" \
                  -target="aws_eks_access_entry.manager" \
                  -target="aws_iam_openid_connect_provider.eks" \
                  -target="aws_eks_node_group.general"
```

_Confirm with `yes`._

### Phase 3: Final Infrastructure Teardown

Once the Kubernetes dependencies are cleared, run the final full destroy command.

1.  **Run Full Destroy:**
    ```bash
    terraform destroy
    ```
    _Confirm with `yes`._ This will remove the EKS cluster, DynamoDB tables, VPC, and all remaining resources.
