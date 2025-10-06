resource "azurerm_storage_account" "archive" {
  name                            = var.account_name
  resource_group_name             = var.resource_group_name
  location                        = var.location
  account_tier                    = "Standard"
  account_replication_type        = "ZRS"
  allow_nested_items_to_be_public = false
}

resource "azurerm_storage_container" "archive" {
  name                  = var.container_name
  storage_account_id    = azurerm_storage_account.archive.id
  container_access_type = "private"
}

resource "azurerm_storage_container_immutability_policy" "archive" {
  storage_container_resource_manager_id = azurerm_storage_container.archive.id
  immutability_period_in_days           = var.immutability_days
  protected_append_writes_enabled       = true
  # allow_protected_append_writes_all        = false # mutually exclusive with the above
}

resource "azurerm_log_analytics_data_export_rule" "export" {
  name                    = "la-export"
  resource_group_name     = var.resource_group_name
  workspace_resource_id   = var.workspace_id
  destination_resource_id = azurerm_storage_account.archive.id
  table_names             = var.table_names # omit to export all supported tables
  enabled                 = true
}

data "azurerm_log_analytics_workspace" "law" {
  id = var.workspace_id
}

resource "azurerm_role_assignment" "la_export_storage" {
  scope                = azurerm_storage_account.archive.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = data.azurerm_log_analytics_workspace.law.identity[0].principal_id
}
