
output "aks_subnet_address_prefix" {
  value = azurerm_subnet.aks_subnet.address_prefixes[0]
}

output "aks_subnet_address_prefix_list" {
  value = azurerm_subnet.aks_subnet.address_prefixes
}

output "pe_subnet_address_prefix" {
  value = azurerm_subnet.private_endpoints.address_prefixes[0]
}

output "postgres_subnet_address_prefix" {
  value = azurerm_subnet.postgres_subnet.address_prefixes[0]

}


output "pe_subnet_address_id" {
  value = azurerm_subnet.private_endpoints.id
}

output "azurerm_route_table_aks_rt_name" {
  value = azurerm_route_table.aks_rt.name
}




output "azurerm_subnet_firewall_id" {
  value = azurerm_subnet.firewall.id
}

output "gateway_subnet_id" {
  value = azurerm_subnet.gateway_subnet.id
}

output "gateway_public_ip_id" {
  value = azurerm_public_ip.vpn_gw.id
}

output "gateway_public_ip" {
  value = azurerm_public_ip.vpn_gw.ip_address
}

output "aks_subnet_id" {
  value = azurerm_subnet.aks_subnet.id
}

output "postgres_subnet_id" {
  value = azurerm_subnet.postgres_subnet.id
}

output "azurerm_firewall_policy_aks_policy_id" {
  value = azurerm_firewall_policy.aks_policy.id

}

output "aks_subnet_name" {
  value = azurerm_subnet.aks_subnet.name
}

#####
output "general_subnet_address_prefix" {
  value = local.subnet_general_prefix #azurerm_subnet.general_subnet.address_prefixes[0]
}

output "general_subnet_address_prefix_list" {
  value = local.subnet_general_prefix_list #azurerm_subnet.general_subnet.address_prefixes
}

output "general_subnet_name" {
  value = local.subnet_general_name #subnet_general_name #azurerm_subnet.general_subnet.name
}

output "general_subnet_id" {
  value = local.subnet_general_id #subnet_general_id #azurerm_subnet.general_subnet.id
}

#####

output "virtual_network_name" {
  value = local.vnet_existing_name #azurerm_virtual_network.vnet.name
}

output "virtual_network_id" {
  value = local.vnet_existing_id #azurerm_virtual_network.vnet.id
}

output "virtual_network_address_space" {
  value = local.vnet_existing_prefix
}




# NSG used for workload subnets
output "workload_nsg_id" { value = azurerm_network_security_group.workload.id }
output "workload_nsg_name" { value = azurerm_network_security_group.workload.name }

# If you create these, expose them; otherwise leave commented
# output "appgw_id"      { value = azurerm_application_gateway.appgw.id }
# output "firewall_id"   { value = azurerm_firewall.azfw.id }


output "azurerm_firewall_aks_fw_ip" {
  value = azurerm_firewall.aks_fw.ip_configuration[0].private_ip_address

}

output "azurerm_public_ip_fw_pip_id" {
  value = azurerm_public_ip.fw_pip.id

}

output "azurerm_public_ip_fw_pip_id_address" {
  value = azurerm_public_ip.fw_pip.ip_address

}