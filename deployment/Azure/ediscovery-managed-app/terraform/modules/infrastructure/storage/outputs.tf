# modules/infrastructure/storage/outputs.tf
output "storage_account_name" {
  value = azurerm_storage_account.storage.name
}

output "storage_account_blob_url" {
  value = "https://${azurerm_storage_account.storage.name}.blob.core.windows.net/"
}

output "storage_id" {
  value = azurerm_storage_account.storage.id
}
output "storage_name" {
  value = azurerm_storage_account.storage.name
}
 