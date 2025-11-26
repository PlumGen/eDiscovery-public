locals {
  # Derive a short, valid name from the NSG ID and add a tiny hash to avoid collisions
  nsg_name_raw = element(split("/", var.nsg_id), length(split("/", var.nsg_id)) - 1)
  nsg_name     = replace(local.nsg_name_raw, "/[^0-9A-Za-z._-]/", "_")
  flowlog_hash = substr(md5(var.nsg_id), 0, 6)
  flowlog_name = substr("flowlog-${local.nsg_name}-${local.flowlog_hash}", 0, 80)
}

resource "azurerm_storage_account" "flow" {
  name                     = var.flowlog_sa_name
  resource_group_name      = var.resource_group_name    
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}


resource "azurerm_network_watcher_flow_log" "nsg_flow" {
  name                      = local.flowlog_name

  resource_group_name       = var.network_watcher_rg
  network_watcher_name      = var.network_watcher_name 

  network_security_group_id = var.nsg_id
  storage_account_id        = azurerm_storage_account.flow.id
  enabled                   = true
  version                   = 2

  retention_policy {
    enabled = true
    days    = 30
  }

  traffic_analytics {
    enabled               = true
    workspace_id          = var.workspace_customer_id
    workspace_region      = var.location
    workspace_resource_id = var.workspace_id
    interval_in_minutes   = 10
  }
}
