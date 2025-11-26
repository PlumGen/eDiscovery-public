output "aks_kube_config" {
  value     = module.aks.kube_config
  sensitive = true
}

output "aks_kubelet_identity" {
  value = module.aks.kubelet_identity
}

output "acr_login_server" {
  value = module.acr.login_server
}

output "postgresql_fqdn" {
  value = module.postgresql.db_fqdn
}

output "storage_account_name" {
  value = module.storage.storage_account_name
}

output "frontend_identity_client_id" {
  value = azurerm_user_assigned_identity.frontend_identity.client_id
}

output "subscription_id" {
  value = var.subscription_id
}


output "User_Interface" {
  value = data.kubernetes_service.ingress_service.status[0].load_balancer[0].ingress[0].ip
}

output "ingress_ilb_ip" {
  value = data.kubernetes_service.ingress_service.status[0].load_balancer[0].ingress[0].ip
}

output "FIREWALL_IP" {
  value = module.networking.azurerm_public_ip_fw_pip_id_address
}

output "VPN_IP" {
  value = module.networking.gateway_public_ip
}

