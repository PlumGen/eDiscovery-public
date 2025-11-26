# modules/infrastructure/storage/main.tf
resource "azurerm_storage_account" "storage" {
  name                     = "ediscoverystorage${var.storage_suffix}"
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  tags = {
    "${var.tagkey}" = var.tagvalue
  }  
  public_network_access_enabled = false
  
}

# Storage Blob permissions
resource "azurerm_role_assignment" "blob_contributor" {
  principal_id         = var.managed_identity_principal_id
  role_definition_name = "Storage Blob Data Contributor"
  scope                = azurerm_storage_account.storage.id


}



