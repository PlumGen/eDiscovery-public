# modules/infrastructure/postgresql/outputs.tf
output "db_fqdn" { value = azurerm_postgresql_flexible_server.db.fqdn }
output "db_name" { value = azurerm_postgresql_flexible_server_database.app_db.name }
output "db_user" { value = azurerm_postgresql_flexible_server.db.administrator_login }
output "db_password" { value = var.admin_password }

output "server_id" { value = azurerm_postgresql_flexible_server.db.id }



