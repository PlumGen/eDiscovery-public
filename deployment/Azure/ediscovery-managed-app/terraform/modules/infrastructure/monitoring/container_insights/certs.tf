# modules/infrastructure/monitoring/container_insights/cert.tf
resource "tls_private_key" "arc" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

resource "tls_self_signed_cert" "arc" {
  private_key_pem       = tls_private_key.arc.private_key_pem
  validity_period_hours = 8760 # 1 year
  is_ca_certificate     = false

  subject {
    common_name  = "aks-arc"
    organization = "PlumGen"
  }

  allowed_uses = [
    "key_encipherment",
    "digital_signature",
  ]
}
