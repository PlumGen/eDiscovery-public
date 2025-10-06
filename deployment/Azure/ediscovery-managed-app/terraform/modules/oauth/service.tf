resource "kubernetes_service" "oauth2_proxy" {
  metadata {
    name      = "oauth2-proxy"
    namespace = "default"
    labels = {
      app = "oauth2-proxy"
    }
  }

  spec {
    selector = {
      app = "oauth2-proxy"
    }

    port {
      name        = "http"
      port        = 80        # ingress points here
      target_port = 4180      # pod’s http port
    }

    port {
      name        = "metrics"
      port        = 44180
      target_port = 44180
    }
  }
}
