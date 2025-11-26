terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes",
      version = ">= 2.20.0"
    }
    helm = {
      source  = "hashicorp/helm",
      version = ">= 2.10.0" 
    }

  }
}


resource "helm_release" "cert_manager" {

  name       = "cert-manager"
  namespace  = "cert-manager"
  repository = "https://charts.jetstack.io"
  chart      = "cert-manager"
  version    = "v1.14.4"   # ✅ current stable (as of Oct 2025)
  create_namespace = true

  set = [
    {
      name  = "installCRDs"
      value = "true"
    }
  ]


  # Optional but recommended: webhook and startup probes can take time
  timeout = 600
}


resource "kubernetes_service_account" "bootstrap_admin" {
  metadata {
    name      = "bootstrap-admin"
    namespace = "kube-system"
  }
}

resource "kubernetes_cluster_role" "bootstrap_clusterissuer_admin" {
  metadata {
    name = "bootstrap-clusterissuer-admin"
  }

  rule {
    api_groups = ["cert-manager.io"]
    resources  = ["clusterissuers"]
    verbs      = ["get", "list", "create", "update", "patch", "delete"]
  }
}

resource "kubernetes_cluster_role_binding" "bootstrap_clusterissuer_binding" {
  metadata {
    name = "bootstrap-clusterissuer-admin-binding"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = kubernetes_cluster_role.bootstrap_clusterissuer_admin.metadata[0].name
  }

  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account.bootstrap_admin.metadata[0].name
    namespace = "kube-system"
  }
}

resource "kubernetes_job" "bootstrap_clusterissuer" {
  metadata {
    name      = "bootstrap-clusterissuer"
    namespace = "kube-system"
  }

  spec {
    backoff_limit = 2

    template {
      metadata {
        labels = { app = "bootstrap-clusterissuer" }
      }

      spec {
        service_account_name = kubernetes_service_account.bootstrap_admin.metadata[0].name
        restart_policy       = "OnFailure"

        container {
          name    = "apply-clusterissuer"
          image   = "bitnami/kubectl:1.30"
          command = ["/bin/sh", "-c"]

          # ✅ Correct heredoc syntax inside args
args = [
  <<EOT
echo "Waiting for cert-manager..."
kubectl wait --for=condition=available --timeout=300s deployment --all -n cert-manager || exit 1
echo "Applying ClusterIssuer..."
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: sheraz.waise@plumgenai.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
echo "ClusterIssuer applied successfully."
EOT
]

        }
      }
    }
  }

  depends_on = [
    kubernetes_cluster_role_binding.bootstrap_clusterissuer_binding,
    helm_release.cert_manager
  ]

  lifecycle {
    ignore_changes = [spec]
  }
}
