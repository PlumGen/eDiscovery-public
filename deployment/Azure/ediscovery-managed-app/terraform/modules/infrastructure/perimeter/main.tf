############################################
# Route Table: force egress via FW + exceptions
############################################


# Explicit east-west bypass (clarity)
resource "azurerm_route" "aks_to_postgres" {
  name                   = "to-postgres-subnet"
  resource_group_name    = var.resource_group_name
  route_table_name       = var.azurerm_route_table_aks_rt_name
  address_prefix         = var.postgres_subnet_address_prefix
  next_hop_type          = "VnetLocal"
}

resource "azurerm_route" "aks_to_pe" {
  name                   = "to-private-endpoints-subnet"
  resource_group_name    = var.resource_group_name
  route_table_name       = var.azurerm_route_table_aks_rt_name
  address_prefix         = var.pe_subnet_address_prefix
  next_hop_type          = "VnetLocal"
}

resource "azurerm_route" "aks_to_general" {
  name                   = "to-general-subnet"
  resource_group_name    = var.resource_group_name
  route_table_name       = var.azurerm_route_table_aks_rt_name
  address_prefix         = var.general_subnet_address_prefix
  next_hop_type          = "VnetLocal"
}
