resource "kubernetes_service_account" "oauth2_proxy" {
  metadata {
    name      = "oauth2-proxy"
    namespace = "default"

    labels = {
      "app.kubernetes.io/managed-by" = "Helm"
    }

    annotations = {
      "azure.workload.identity/client-id" = var.frontend_aad_client_id
      "meta.helm.sh/release-name"         = "oauth2-proxy"
      "meta.helm.sh/release-namespace"    = "default"
    }
  }
}

resource "kubernetes_service_account" "frontend_sa" {
  metadata {
    name      = "frontend-sa"
    namespace = "default"
    annotations = {
      "azure.workload.identity/client-id"                        = var.managed_identity_client_id
      "azure.workload.identity/tenant-id"                        = var.tenant_id
      "azure.workload.identity/service-account-token-expiration" = "86400" # 24 hours
    }


  }


}

resource "kubernetes_cluster_role" "frontend_node_reader" {
  metadata {
    name = "frontend-node-reader"
  }

  rule {
    api_groups = [""]
    resources  = ["nodes"]
    verbs      = ["get", "list", "watch"]
  }
}

resource "kubernetes_cluster_role_binding" "frontend_node_reader_bind" {
  metadata {
    name = "frontend-node-reader-binding"
  }

  role_ref {
    kind      = "ClusterRole"
    name      = kubernetes_cluster_role.frontend_node_reader.metadata[0].name
    api_group = "rbac.authorization.k8s.io"
  }

  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account.frontend_sa.metadata[0].name
    namespace = "default"
  }
}

resource "kubernetes_role" "frontend_job_creator" {
  metadata {
    name      = "job-creator"
    namespace = "default"
  }

  rule {
    api_groups = ["batch"]
    resources  = ["jobs", "jobs/status"]
    verbs      = ["create", "get", "list", "watch"]
  }

  rule {
    api_groups = [""]
    resources  = ["pods", "pods/status"]
    verbs      = ["get", "list", "watch"]
  }


}

resource "kubernetes_role_binding" "frontend_bind" {
  metadata {
    name      = "frontend-job-binding"
    namespace = "default"
  }

  role_ref {
    kind      = "Role"
    name      = kubernetes_role.frontend_job_creator.metadata[0].name
    api_group = "rbac.authorization.k8s.io"
  }

  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account.frontend_sa.metadata[0].name
    namespace = "default"
  }


}
