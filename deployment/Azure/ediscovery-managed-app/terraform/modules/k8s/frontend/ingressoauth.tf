
resource "kubernetes_ingress_v1" "oauth2_proxy" {

  count = var.frontend_authonly ? 1 : 0

  metadata {
    name = "oauth2-proxy-ingress"
    annotations = {
      "nginx.ingress.kubernetes.io/force-ssl-redirect"     = "true"
      "nginx.ingress.kubernetes.io/ssl-redirect"           = "true"
      "nginx.ingress.kubernetes.io/whitelist-source-range" = var.allowed_ip_ranges
      "nginx.ingress.kubernetes.io/proxy-buffer-size"      = "128k" 
      "nginx.ingress.kubernetes.io/proxy-buffers-number"   = "4"
      "nginx.ingress.kubernetes.io/auth-snippet" = <<-EOT
        if ($request_uri ~ "^/oauth2/") {
          return 200;
        }
      EOT
    }
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
          path      = "/oauth2"
          path_type = "Prefix"
          backend {
            service {
              name = "oauth2-proxy"
              port {
                number = 80   # default oauth2-proxy service port
              }
            }
          }
        }
      }
    }
  }
}
