resource "azurerm_postgresql_flexible_server_configuration" "shared_preload" {
  name      = "shared_preload_libraries"
  server_id = var.postgres_server_id
  value     = "pgaudit"
}

resource "azurerm_postgresql_flexible_server_configuration" "pgaudit_log" {
  name      = "pgaudit.log"
  server_id = var.postgres_server_id
  value     = "WRITE,READ,ROLE,DDL"
}

resource "azurerm_postgresql_flexible_server_configuration" "log_connections" {
  name      = "log_connections"
  server_id = var.postgres_server_id
  value     = "on"
}

resource "azurerm_postgresql_flexible_server_configuration" "log_disconnections" {
  name      = "log_disconnections"
  server_id = var.postgres_server_id
  value     = "on"
}
