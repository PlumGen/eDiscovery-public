locals {
  acr_data_private_dns_zone = "privatelink.${replace(lower(var.location), " ", "")}.data.azurecr.io"
}

# Private DNS Zones for services
resource "azurerm_private_dns_zone" "postgres" {
  name                = "privatelink.postgres.database.azure.com"
  resource_group_name = var.resource_group_name
}




resource "azurerm_private_dns_zone" "acr" {
  name                = "privatelink.azurecr.io"
  resource_group_name = var.resource_group_name
}

resource "azurerm_private_dns_zone" "acr_data" {
  name                = local.acr_data_private_dns_zone
  resource_group_name = var.resource_group_name
}

resource "azurerm_private_dns_zone" "storage" {
  name                = "privatelink.blob.core.windows.net"
  resource_group_name = var.resource_group_name
}

resource "azurerm_private_dns_zone" "aks" {
  name                = "privatelink.${var.location}.azmk8s.io"
  resource_group_name = var.resource_group_name
}

# Link DNS zones to the VNet
resource "azurerm_private_dns_zone_virtual_network_link" "aks_link" {
  name                  = "aks-link"
  resource_group_name   = var.resource_group_name
  private_dns_zone_name = azurerm_private_dns_zone.aks.name
  virtual_network_id    = var.virtual_network_id
}


resource "azurerm_private_dns_zone_virtual_network_link" "postgres_link" {
  name                  = "postgres-link"
  resource_group_name   = var.resource_group_name
  private_dns_zone_name = azurerm_private_dns_zone.postgres.name
  virtual_network_id    = var.virtual_network_id
}


resource "azurerm_private_dns_zone_virtual_network_link" "acr_link" {
  name                  = "acr-link"
  resource_group_name   = var.resource_group_name
  private_dns_zone_name = azurerm_private_dns_zone.acr.name
  virtual_network_id    = var.virtual_network_id
}

resource "azurerm_private_dns_zone_virtual_network_link" "acr_data_link" {
  name                  = "acr-data-link"
  resource_group_name   = var.resource_group_name
  private_dns_zone_name = azurerm_private_dns_zone.acr_data.name
  virtual_network_id    = var.virtual_network_id
}


resource "azurerm_private_dns_zone_virtual_network_link" "storage_link" {
  name                  = "storage-link"
  resource_group_name   = var.resource_group_name
  private_dns_zone_name = azurerm_private_dns_zone.storage.name
  virtual_network_id    = var.virtual_network_id
}
