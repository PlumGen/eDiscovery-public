# VPN Gateway
resource "azurerm_virtual_network_gateway" "vpn" {
  name                = "vpn-gateway"
  location            = var.location
  resource_group_name = var.resource_group_name

  type     = "Vpn"
  vpn_type = "RouteBased"
  sku      = "VpnGw1"

  ip_configuration {
    name                          = "vnetGatewayConfig"
    public_ip_address_id          = var.azurerm_public_ip
    private_ip_address_allocation = "Dynamic"
    subnet_id                     = var.azurerm_subnet
  }


  vpn_client_configuration {
    address_space        = ["172.16.0.0/24"]
    vpn_client_protocols = ["OpenVPN"]

    aad_tenant  = "https://login.microsoftonline.com/${var.tenant_id}/"
    aad_audience = var.vpn_server_app_id
    aad_issuer  = "https://sts.windows.net/${var.tenant_id}/"
  }

}

