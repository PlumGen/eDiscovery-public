

# modules/infrastructure/aks/outputs.tf
output "kubelet_identity" {
  value = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
}

output "kube_config" {
  value     = azurerm_kubernetes_cluster.aks.kube_config_raw
  sensitive = true
}

output "aks_host" {
  value = azurerm_kubernetes_cluster.aks.kube_config.0.host
}

output "aks_client_certificate" {
  value = azurerm_kubernetes_cluster.aks.kube_config.0.client_certificate
}

output "aks_client_key" {
  value = azurerm_kubernetes_cluster.aks.kube_config.0.client_key
}

output "aks_cluster_ca_certificate" {
  value = azurerm_kubernetes_cluster.aks.kube_config.0.cluster_ca_certificate
}

output "oidc_issuer_url" {
  value = azurerm_kubernetes_cluster.aks.oidc_issuer_url
}

output "principal_id" {
  value = azurerm_kubernetes_cluster.aks.identity[0].principal_id
}

output "cluster_id" { value = azurerm_kubernetes_cluster.aks.id }


output "aks_location" { value = azurerm_kubernetes_cluster.aks.location }
output "aks_name" { value = azurerm_kubernetes_cluster.aks.name }

output "aks_node_resource_group" {
  value = azurerm_kubernetes_cluster.aks.node_resource_group
}