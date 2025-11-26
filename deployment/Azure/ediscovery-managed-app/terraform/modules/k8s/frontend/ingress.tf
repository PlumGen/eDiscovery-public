resource "kubernetes_ingress_v1" "frontend" {
  metadata {
    name = "ediscovery-ingress"
    annotations = merge(
      {
        "nginx.ingress.kubernetes.io/force-ssl-redirect"     = "true"
        "nginx.ingress.kubernetes.io/ssl-redirect"           = "true"
        "nginx.ingress.kubernetes.io/whitelist-source-range" = var.allowed_ip_ranges
      },
      var.frontend_authonly ? {
        # Protect with oauth2-proxy
        "nginx.ingress.kubernetes.io/auth-url"    = "http://oauth2-proxy.default.svc.cluster.local/oauth2/auth"
        "nginx.ingress.kubernetes.io/auth-signin" = "https://$host/oauth2/start?rd=/IntroPage"
        "nginx.ingress.kubernetes.io/auth-response-headers" = "X-Auth-Request-Email,X-Auth-Request-Preferred-Username"
      } : {}
    )
  }

  spec {
    ingress_class_name = "nginx"

    dynamic "tls" {
      for_each = var.hostname != "" ? [1] : []
      content {
        hosts       = [var.hostname]
        secret_name = "tls-secret"
      }
    }

    rule {
      host = var.hostname != "" ? var.hostname : null

      http {
        path {
          path      = "/"
          path_type = "Prefix"
          backend {
            service {
              name = var.service_name
              port {
                number = var.service_port
              }
            }
          }
          
        }
      }
    }
  }
}
