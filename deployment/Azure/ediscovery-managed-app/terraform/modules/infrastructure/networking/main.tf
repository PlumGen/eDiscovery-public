############################################
# VNet (Azure DNS via 168.63.129.16 kept)
############################################
#resource "azurerm_virtual_network" "vnet" {
#  name                = "ediscovery-vnet"
#  location            = var.location
#  resource_group_name = var.resource_group_name
#  address_space       = ["10.240.0.0/16"]

#  dns_servers = [] # keep Azure-provided DNS

#  tags = {
#    "${var.tagkey}" = var.tagvalue
#  }
#}
## look up existing VNet and general subnet
# Lookup an existing VNet
data "azurerm_virtual_network" "existing" {
  name                = "ediscovery-vnet"
  resource_group_name = var.resource_group_name
}

# Lookup a subnet within it (optional)
data "azurerm_subnet" "existing" {
  name                 = "general-subnet"
  virtual_network_name = data.azurerm_virtual_network.existing.name
  resource_group_name  = var.resource_group_name
}


locals {
vnet_existing_id        = data.azurerm_virtual_network.existing.id
vnet_existing_name      = data.azurerm_virtual_network.existing.name
vnet_existing_location  = data.azurerm_virtual_network.existing.location
vnet_existing_prefix = data.azurerm_virtual_network.existing.address_space[0]
vnet_existing_prefix_list = data.azurerm_virtual_network.existing.address_space

subnet_general_id       = data.azurerm_subnet.existing.id
subnet_general_name     = data.azurerm_subnet.existing.name
subnet_general_prefix   = data.azurerm_subnet.existing.address_prefixes[0]
subnet_general_prefix_list = data.azurerm_subnet.existing.address_prefixes
}


# ── Subnets ──────────────────────────────

resource "azurerm_subnet" "aks_subnet" {
  name                 = "aks-subnet"
  resource_group_name  = var.resource_group_name
  virtual_network_name = local.vnet_existing_name #azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.240.1.0/20"]



}

resource "azurerm_subnet" "postgres_subnet" {
  name                 = "postgres-subnet"
  resource_group_name  = var.resource_group_name
  virtual_network_name = local.vnet_existing_name #azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.240.2.0/24"]

  delegation {
    name = "fsdelegation"
    service_delegation {
      name    = "Microsoft.DBforPostgreSQL/flexibleServers"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action"]
    }
  }
}

#resource "azurerm_subnet" "general_subnet" {
#  name                 = "general-subnet"
#  resource_group_name  = var.resource_group_name
#  virtual_network_name = local.vnet_existing_name #azurerm_virtual_network.vnet.name
#  address_prefixes     = ["10.240.6.0/24"]
#}

resource "azurerm_subnet" "firewall" {
  name                 = "AzureFirewallSubnet"
  resource_group_name  = var.resource_group_name
  virtual_network_name = local.vnet_existing_name #azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.240.3.0/26"]
}

resource "azurerm_subnet" "private_endpoints" {
  name                 = "private-endpoints-subnet"
  resource_group_name  = var.resource_group_name
  virtual_network_name = local.vnet_existing_name #azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.240.4.0/24"]

  # Required for Private Endpoints
  #private_endpoint_network_policies_enabled = false
  private_endpoint_network_policies = "Disabled"        # azurerm >= v4

}

### VPN IP and Subnet
# Public IP for VPN Gateway
resource "azurerm_public_ip" "vpn_gw" {
  name                = "vpn-gateway-pip"
  location            = var.location
  resource_group_name = var.resource_group_name
  allocation_method   = "Static"
  sku                 = "Standard" #"Standard"
}

# Ensure you have a GatewaySubnet in your VNet
resource "azurerm_subnet" "gateway_subnet" {
  name                 = "GatewaySubnet"
  resource_group_name  = var.resource_group_name
  virtual_network_name = local.vnet_existing_name #azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.240.5.0/27"] # adjust to fit your address space
}

############################################
# NSG for AKS Subnet
############################################
resource "azurerm_network_security_group" "workload" {
  name                = "ediscovery-aks-nsg"
  location            = var.location
  resource_group_name = var.resource_group_name

  tags = {
    "${var.tagkey}" = var.tagvalue
  }
}

resource "azurerm_subnet_network_security_group_association" "aks_subnet_nsg" {
  subnet_id                 = azurerm_subnet.aks_subnet.id
  network_security_group_id = azurerm_network_security_group.workload.id
}

resource "azurerm_route_table" "aks_rt" {
  name                = "aks-route-table"
  location            = var.location
  resource_group_name = var.resource_group_name
}

resource "azurerm_subnet_route_table_association" "aks_subnet_assoc" {
  subnet_id      = azurerm_subnet.aks_subnet.id
  route_table_id = azurerm_route_table.aks_rt.id
}


############################################
# Azure Firewall + Policy (DNS proxy on)
############################################
resource "azurerm_public_ip" "fw_pip" {
  name                = "aks-fw-pip"
  location            = var.location
  resource_group_name = var.resource_group_name
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_firewall_policy" "aks_policy" {
  name                = "aks-fw-policy"
  resource_group_name = var.resource_group_name
  location            = var.location

  dns {
    proxy_enabled = true
  }
}

resource "azurerm_firewall" "aks_fw" {
  depends_on          = [azurerm_firewall_policy.aks_policy]
  name                = "aks-firewall"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku_name            = "AZFW_VNet"
  sku_tier            = "Standard"

  ip_configuration {
    name                 = "configuration"
    subnet_id            = azurerm_subnet.firewall.id
    public_ip_address_id = azurerm_public_ip.fw_pip.id
  }

  firewall_policy_id = azurerm_firewall_policy.aks_policy.id

}

# Default: everything to Firewall
resource "azurerm_route" "aks_default" {
  name                   = "default-0-0-0-0"
  resource_group_name    = var.resource_group_name
  route_table_name       = azurerm_route_table.aks_rt.name
  address_prefix         = "0.0.0.0/0"
  next_hop_type          = "VirtualAppliance"
  next_hop_in_ip_address = azurerm_firewall.aks_fw.ip_configuration[0].private_ip_address
}
 
resource "azurerm_firewall_policy_rule_collection_group" "allow_all_network" {
  name               = "allow-all-network"
  firewall_policy_id = azurerm_firewall_policy.aks_policy.id
  priority           = 5000

  network_rule_collection {
    name     = "allow-any"
    action   = "Allow"
    priority = 100

    rule {
      name                  = "any-to-any"
      source_addresses      = ["*"]
      destination_addresses = ["*"]
      destination_ports     = ["*"]
      protocols             = ["Any"]
    }
  }
}



