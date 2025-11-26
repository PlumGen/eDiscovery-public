resource "kubernetes_service" "frontend" {
  metadata {
    name = "ediscovery-frontend"
  }

  spec {
    selector = {
      app = "ediscovery-frontend"
    }

    port {
      port        = 80
      target_port = 8080
      protocol    = "TCP"
    }

    type = "ClusterIP"
  }


}
