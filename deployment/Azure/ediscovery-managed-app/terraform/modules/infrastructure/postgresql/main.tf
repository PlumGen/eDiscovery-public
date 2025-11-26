# modules/infrastructure/postgresql/main.tf
resource "azurerm_postgresql_flexible_server" "db" {
  name                   = var.db_name
  resource_group_name    = var.resource_group_name
  location               = var.location
  administrator_login    = var.admin_login
  administrator_password = var.admin_password
  version                = "13"
  storage_mb             = 32768
  sku_name               = "GP_Standard_D2s_v3"
  zone                   = "1"



  delegated_subnet_id    = var.private_endpoints_subnet_id   # place server inside your private subnet
  private_dns_zone_id    = var.private_dns_zone_postgres_id  # link to privatelink.postgres.database.azure.com

  # explicitly disable public network access
  public_network_access_enabled = false


  tags = {
    "${var.tagkey}" = var.tagvalue
  }  
}

resource "azurerm_postgresql_flexible_server_database" "app_db" {
  name      = var.db_name
  server_id = azurerm_postgresql_flexible_server.db.id
  charset   = "UTF8"
  collation = "en_US.utf8"


}

locals {
  aks_subnet_start_ip = cidrhost(var.subnet_cidr, 0)
  aks_subnet_end_ip   = cidrhost(var.subnet_cidr, 255)
}


#resource "azurerm_postgresql_flexible_server_firewall_rule" "allow_aks_subnet" {
#  name             = "allow-aks-subnet"
#  server_id        = azurerm_postgresql_flexible_server.db.id
#  start_ip_address = "0.0.0.0"         #local.aks_subnet_start_ip
#  end_ip_address   = "255.255.255.255" #local.aks_subnet_end_ip
#}

# PostgreSQL permissions
resource "azurerm_role_assignment" "postgres_admin" {
  principal_id         = var.managed_identity_principal_id
  role_definition_name = "Contributor"
  scope                = azurerm_postgresql_flexible_server.db.id


}

there needs to be a role assigned to the postgres and it should have acces to the network to contribute DNS