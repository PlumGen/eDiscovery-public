output "private_dns_zone_postgres_id" {
  value = azurerm_private_dns_zone.postgres.id
}

output "private_dns_zone_acr_id" {
  value = azurerm_private_dns_zone.acr.id
}

output "private_dns_zone_acr_data_id" {
  value = azurerm_private_dns_zone.acr_data.id
}

output "private_dns_zone_storage_id" {
  value = azurerm_private_dns_zone.storage.id
}


output "azurerm_private_dns_zone_acr_name" {
  value = azurerm_private_dns_zone.acr.name
}

output "azurerm_private_dns_zone_acr_data_name" {
  value = azurerm_private_dns_zone.acr_data.name
}

output "azurerm_private_dns_zone_storage_name" {
  value = azurerm_private_dns_zone.storage.name
}

output "private_dns_zone_aks_id" {
  value = azurerm_private_dns_zone.aks.id
}

output "private_dns_zone_aks_name" {
  value = azurerm_private_dns_zone.aks.name
}
