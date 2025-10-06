terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
    }
    helm = {
      source  = "hashicorp/helm"
    }

  }
}

resource "kubernetes_secret" "oauth2_proxy_client" {
  metadata {
    name      = "oauth2-proxy-client-secret"
    namespace = "default"
  }

  data = {
    client-secret = var.frontend_aad_client_secret
  }
} 

resource "kubernetes_secret" "oauth2_proxy_cookie" {
  metadata {
    name      = "oauth2-proxy"
    namespace = "default"
  }

  data = {
    cookie-secret = var.cookie_secret
  }
}

resource "kubernetes_deployment" "oauth2_proxy" {

  metadata {
    name      = "oauth2-proxy"
    namespace = "default"
    labels = {
      app = "oauth2-proxy"
    }
  }

  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "oauth2-proxy"
      }
    }
    template {
      metadata {
        labels = {
          app = "oauth2-proxy"
        }
      }
      spec {
        service_account_name = "oauth2-proxy"

        container {
          name  = "oauth2-proxy"
          image = "quay.io/oauth2-proxy/oauth2-proxy:v7.7.1"

          args = [
            "--http-address=0.0.0.0:4180",
            "--metrics-address=0.0.0.0:44180",
            "--provider=oidc",
            "--oidc-issuer-url=https://login.microsoftonline.com/${var.tenant_id}/v2.0",
            "--client-id=${var.frontend_aad_client_id}",
            "--oidc-extra-audience=api://AzureADTokenExchange",
            "--redirect-url=https://${var.hostname_path}/oauth2/callback",
            "--insecure-oidc-allow-unverified-email=true",
            "--skip-provider-button=true",
            "--oidc-email-claim=preferred_username",
            "--email-domain=*",
            "--show-debug-on-error=true",
            "--standard-logging=true",
            "--auth-logging=true",
            "--request-logging=true",
            "--extra-jwt-issuers=https://login.microsoftonline.com/${var.tenant_id}/v2.0=${var.frontend_aad_client_id}",
            "--cookie-secure=true",
            "--cookie-domain=${var.hostname}",
            "--whitelist-domain=${var.hostname}"            
          ]

          env {
            name = "OAUTH2_PROXY_COOKIE_SECRET"
            value_from {
              secret_key_ref {
                name = "oauth2-proxy"
                key  = "cookie-secret"
              }
            }
          }
          env {
            name = "OAUTH2_PROXY_CLIENT_SECRET"
            value_from {
              secret_key_ref {
                name = "oauth2-proxy-client-secret"
                key  = "client-secret"
              }
            }
          }

          port {
            name           = "http"
            container_port = 4180
          }
          port {
            name           = "metrics"
            container_port = 44180
          }


        }


      }
    }
  }
}

