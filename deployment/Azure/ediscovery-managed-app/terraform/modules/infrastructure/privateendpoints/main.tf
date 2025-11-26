
# ACR - registry
resource "azurerm_private_endpoint" "acr_registry" {
  name                = "acr-pe-registry"
  location            = var.location
  resource_group_name = var.resource_group_name
  subnet_id           = var.azurerm_subnet_private_endpoints_id

  private_service_connection {
    name                           = "acr-privatelink-registry"
    private_connection_resource_id = var.private_connection_acr_resource_id
    subresource_names              = ["registry"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name = "acr-dnszonegroup"
    private_dns_zone_ids = [
      var.azurerm_private_dns_zone_acr_id,       # privatelink.azurecr.io
      #var.azurerm_private_dns_zone_acr_data_id
    ]
  }
}

# Storage - blob
resource "azurerm_private_endpoint" "storage_blob" {
  name                = "storage-pe-blob"
  location            = var.location
  resource_group_name = var.resource_group_name
  subnet_id           = var.azurerm_subnet_private_endpoints_id

  private_service_connection {
    name                           = "storage-privatelink-blob"
    private_connection_resource_id = var.private_connection_storage_resource_id
    subresource_names              = ["blob"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "storage-blob-dnszonegroup"
    private_dns_zone_ids = [var.azurerm_private_dns_zone_storage_id] # privatelink.blob.core.windows.net
  }
}


