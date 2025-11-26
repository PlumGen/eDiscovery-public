terraform {
  required_providers {
    kubernetes = {
      source = "hashicorp/kubernetes"
    }
    helm = {
      source = "hashicorp/helm"
    }
  }
}


resource "kubernetes_config_map" "frontend_env" {
  metadata {
    name = "ediscovery-common-env"
  }
  immutable = true
  data = {
    DB_HOST              = var.db_fqdn
    CLOUDREGION          = var.location

    DB_USERNAME          = var.db_user
    RUNENV               = "CUBE"
    CLOUDENV             = "AZURE"
    AZURE_CLIENT_ID      = var.managed_identity_client_id
    AZURE_TENANT_ID      = var.tenant_id
    AZURE_TENANT_ID_TEST = "TEST"

    AZURE_BLOB_ACCOUNT_URL = "https://${var.storage_account_name}.blob.core.windows.net/"
    AZURE_SUBSCRIPTION_ID  = var.subscription_id
  }

}


# Secret vars
resource "kubernetes_secret" "app_secrets" {
  metadata { name = "ediscovery-common-secrets" }
  type = "Opaque"
  data = {
    DB_PASSWORD = var.db_password
  }


}



# Coerce static_env to strings (optional if already map(string))
resource "kubernetes_config_map" "static_env" {
  metadata { name = "ediscovery-static-env" }
  immutable = true
  data      = { for k, v in var.static_env_vars : k => tostring(v) }

 
}



# Deployment: use the right ConfigMap names
resource "kubernetes_deployment" "frontend" {



  metadata {
    name   = "ediscovery-frontend"
    labels = { app = "ediscovery-frontend" }
  }

  spec {
    replicas = 1
    selector {
      match_labels = { app = "ediscovery-frontend" }
    }

    template {
      metadata {
        annotations = {
          "azure.workload.identity/use" = "true"
          "terraform-restart-trigger"   = timestamp() # 👈 Forces new pod spec each apply
        }
        labels = {
          app                           = "ediscovery-frontend"
          "azure.workload.identity/use" = "true"
        }
      }
      spec {
        service_account_name            = kubernetes_service_account.frontend_sa.metadata[0].name
        automount_service_account_token = true

        container {
          name              = "frontend"
          image             = "${var.acr_login_server}/ediscovery-frontend-image:${var.frontend_image_tag}"
          image_pull_policy = "Always"


          env {
            name  = "ACR_LOGIN_SERVER"
            value = var.acr_login_server
          }
          

          env_from {
            config_map_ref {
              name = kubernetes_config_map.frontend_env.metadata[0].name
            }
          }
          env_from {
            secret_ref {
              name = kubernetes_secret.app_secrets.metadata[0].name
            }
          }
          env_from {
            config_map_ref {
              name = kubernetes_config_map.static_env.metadata[0].name
            }
          }

          port { container_port = 8080 }

        }
      }
    }
  }


}
