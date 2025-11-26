# Allow Azure Load Balancer health probes
resource "azurerm_network_security_rule" "allow_lb_in" {
  name                        = "allow-azure-lb-in"
  priority                    = 100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "*"
  source_address_prefix       = "AzureLoadBalancer"
  destination_address_prefix  = "*"
  source_port_range           = "*"
  destination_port_range      = "*"
  resource_group_name         = var.resource_group_name
  network_security_group_name = var.workload_nsg_name
}

# NSG: allow web+NTP to Internet (place before deny-all)
resource "azurerm_network_security_rule" "allow_internet_web_ntp_out" {
  name                        = "allow-internet-web-ntp-out"
  priority                    = 105
  direction                   = "Outbound"
  access                      = "Allow"
  protocol                    = "*"
  source_address_prefix       = var.aks_subnet_address_prefix
  destination_address_prefix  = "Internet"
  source_port_range           = "*"
  destination_port_ranges     = ["80","443","123"]
  resource_group_name         = var.resource_group_name
  network_security_group_name = var.workload_nsg_name
}

# Allow intra-VNet
resource "azurerm_network_security_rule" "allow_vnet_in" {
  name                        = "allow-vnet-in"
  priority                    = 110
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "*"
  source_address_prefix       = "VirtualNetwork"
  destination_address_prefix  = "VirtualNetwork"
  source_port_range           = "*"
  destination_port_range      = "*"
  resource_group_name         = var.resource_group_name
  network_security_group_name = var.workload_nsg_name
}

# Allow intra-VNet
resource "azurerm_network_security_rule" "allow_kubelet_private" {
  name                        = "Allow-AKS-ControlPlane-10250"
  priority                    = 111
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "*"
  source_address_prefix       = var.aks_subnet_address_prefix
  destination_address_prefix  = "*"
  source_port_range           = "*"
  destination_port_range      = "10250"
  resource_group_name         = var.resource_group_name
  network_security_group_name = var.workload_nsg_name
}

# Outbound: Azure control plane
resource "azurerm_network_security_rule" "allow_azurecloud_out" {
  name                        = "allow-azurecloud-out"
  priority                    = 100
  direction                   = "Outbound"
  access                      = "Allow"
  protocol                    = "*"
  source_address_prefix       = "*"
  destination_address_prefix  = "AzureCloud"
  source_port_range           = "*"
  destination_port_range      = "*"
  resource_group_name         = var.resource_group_name
  network_security_group_name = var.workload_nsg_name
}

# Outbound: MCR & ACR
resource "azurerm_network_security_rule" "allow_mcr_out" {
  name                        = "allow-mcr-out"
  priority                    = 110
  direction                   = "Outbound"
  access                      = "Allow"
  protocol                    = "*"
  source_address_prefix       = "*"
  destination_address_prefix  = "MicrosoftContainerRegistry"
  source_port_range           = "*"
  destination_port_range      = "*"
  resource_group_name         = var.resource_group_name
  network_security_group_name = var.workload_nsg_name
}



# Outbound: Azure Monitor/Defender
resource "azurerm_network_security_rule" "allow_monitor_out" {
  name                        = "allow-monitor-out"
  priority                    = 120
  direction                   = "Outbound"
  access                      = "Allow"
  protocol                    = "*"
  source_address_prefix       = "*"
  destination_address_prefix  = "AzureMonitor"
  source_port_range           = "*"
  destination_port_range      = "*"
  resource_group_name         = var.resource_group_name
  network_security_group_name = var.workload_nsg_name
}

# Outbound: DNS (both UDP/TCP 53) to Azure DNS IP
resource "azurerm_network_security_rule" "allow_azure_dns_out" {
  name                        = "allow-azure-dns-out"
  priority                    = 130
  direction                   = "Outbound"
  access                      = "Allow"
  protocol                    = "*"
  source_address_prefix       = var.address_space
  destination_address_prefix  = "168.63.129.16"
  source_port_range           = "*"
  destination_port_range      = "53"
  resource_group_name         = var.resource_group_name
  network_security_group_name = var.workload_nsg_name
}

# Outbound: IMDS
resource "azurerm_network_security_rule" "allow_imds_out" {
  name                        = "allow-imds-out"
  priority                    = 125
  direction                   = "Outbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_address_prefix       = var.aks_subnet_address_prefix
  destination_address_prefix  = "169.254.169.254"
  source_port_range           = "*"
  destination_port_range      = "80"
  resource_group_name         = var.resource_group_name
  network_security_group_name = var.workload_nsg_name
}

# Outbound: Private Endpoints subnet (443)
resource "azurerm_network_security_rule" "allow_storage_acr_pe_out" {
  name                        = "allow-pe-443"
  priority                    = 200
  direction                   = "Outbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_address_prefix       = var.aks_subnet_address_prefix
  destination_address_prefix  = var.pe_subnet_address_prefix
  source_port_range           = "*"
  destination_port_range      = "443"
  resource_group_name         = var.resource_group_name
  network_security_group_name = var.workload_nsg_name
}




# Outbound: Postgres Flexible Server (5432)
resource "azurerm_network_security_rule" "allow_postgres_out" {
  name                        = "allow-postgres-5432"
  priority                    = 220
  direction                   = "Outbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_address_prefix       = var.aks_subnet_address_prefix
  destination_address_prefix  = var.postgres_subnet_address_prefix
  source_port_range           = "*"
  destination_port_range      = "5432"
  resource_group_name         = var.resource_group_name
  network_security_group_name = var.workload_nsg_name
}


# App + Network rules (no unsupported service tags in AFW network rules)
resource "azurerm_firewall_policy_rule_collection_group" "aks_rules" {
  name               = "aks-fqdn-rules"
  firewall_policy_id = var.azurerm_firewall_policy_aks_policy_id
  priority           = 100

  # ── Application Rules ──
  application_rule_collection {
    name     = "aks-outbound-core"
    priority = 200
    action   = "Allow"

    rule {
      name             = "ubuntu-repos-and-docker"
      source_addresses = var.aks_subnet_address_prefix_list
      destination_fqdns = [
        "archive.ubuntu.com",
        "security.ubuntu.com",
        "azure.archive.ubuntu.com",
        "changelogs.ubuntu.com",
        "snapshot.ubuntu.com",
        "packages.microsoft.com",
        "*.ubuntu.com",
        "*.canonical.com",
        "*.azureedge.net",
        "aksrepos.azureedge.net",
        "docker.io",
        "registry-1.docker.io",
        "auth.docker.io",
        "production.cloudflare.docker.com"
      ]
      protocols { 
        type = "Http"  
        port = 80  
        }
      protocols { 
        type = "Https" 
        port = 443 
        }
    }

    rule {
      name             = "mcr"
      source_addresses = var.aks_subnet_address_prefix_list
      destination_fqdns = [
      "mcr.microsoft.com",
      "*.data.mcr.microsoft.com",
      "*.mcr-msedge.net"        
      ]
        protocols { 
        type = "Https" 
        port = 443 
        }
    }

    rule {
      name             = "aks-control-plane"
      source_addresses = var.aks_subnet_address_prefix_list
      destination_fqdns = [
        "*.hcp.${var.location}.azmk8s.io",
        "management.azure.com",
        "login.microsoftonline.com",
        "acs-mirror.azureedge.net",
        "packages.aks.azure.com",
        "registry.k8s.io"
      ]
          protocols { 
        type = "Https" 
        port = 443 
        }
    }

    rule {
      name             = "monitor-defender"
      source_addresses = var.aks_subnet_address_prefix_list
      destination_fqdns = [
        "*.ods.opinsights.azure.com",
        "*.oms.opinsights.azure.com",
        "*.cloud.defender.microsoft.com",
        "*.monitoring.azure.com",
        "*.ingest.monitor.azure.com",
        "*.metrics.ingest.monitor.azure.com",
        "*.in.applicationinsights.azure.com",
        "dc.services.visualstudio.com",
        "global.handler.control.monitor.azure.com"
      ]
          protocols { 
        type = "Https" 
        port = 443 
        }
    }

    rule {
      name             = "policy"
      source_addresses = var.aks_subnet_address_prefix_list
      destination_fqdns = [
        "data.policy.core.windows.net",
        "store.policy.core.windows.net"
      ]
          protocols { 
        type = "Https" 
        port = 443 
        }
    }

    rule {
      name             = "keyvault-csi"
      source_addresses = var.aks_subnet_address_prefix_list
      destination_fqdns = ["*.vault.azure.net"]
          protocols { 
        type = "Https" 
        port = 443 
        }
    }

    rule {
      name             = "cluster-extensions"
      source_addresses = var.aks_subnet_address_prefix_list
      destination_fqdns = [
        "${var.location}.dp.kubernetesconfiguration.azure.com",
        "mcr.microsoft.com",
        "*.data.mcr.microsoft.com",
        "arcmktplaceprod.azurecr.io",
        "arcmktplaceprod.centralindia.data.azurecr.io",
        "arcmktplaceprod.japaneast.data.azurecr.io",
        "arcmktplaceprod.westus2.data.azurecr.io",
        "arcmktplaceprod.westeurope.data.azurecr.io",
        "arcmktplaceprod.eastus.data.azurecr.io",
        "arcmktplaceprod.${var.location}.data.azurecr.io",
        "*.ingestion.msftcloudes.com",
        "*.microsoftmetrics.com",
        "marketplaceapi.microsoft.com"
      ]
          protocols { 
        type = "Https" 
        port = 443 
        }
    }

    rule {
      name             = "azure-container-registry"
      source_addresses = var.aks_subnet_address_prefix_list
      destination_fqdns = [
        "*.azurecr.io",
        "*.data.azurecr.io",
        "*.privatelink.azurecr.io",
        "*.privatelink.${var.location}.data.azurecr.io",
        "*.blob.core.windows.net",
        "*.cdn.mscr.io"        
      ]
          protocols { 
        type = "Https" 
        port = 443 
        }
    }

    rule {
      name             = "gpu-nodes"
      source_addresses = var.aks_subnet_address_prefix_list
      destination_fqdns = [
        "nvidia.github.io",
        "us.download.nvidia.com",
        "download.docker.com"
      ]
          protocols { 
        type = "Https" 
        port = 443 
        }
    }

    # Optional: if you use Windows node pools
    rule {
      name             = "windows-update"
      source_addresses = var.aks_subnet_address_prefix_list
      destination_fqdns = [
        "*.windowsupdate.com",
        "*.update.microsoft.com",
        "download.windowsupdate.com",
        "ctldl.windowsupdate.com",
        "tsfe.trafficshaping.dsp.mp.microsoft.com",
        "go.microsoft.com",
        "www.msftconnecttest.com",
        "*.mp.microsoft.com",
        "onegetcdn.azureedge.net"
      ]
          protocols { 
        type = "Https" 
        port = 443 
        }
            protocols { 
        type = "Http"  
        port = 80  
        }
    }
  }

# In azurerm_firewall_policy_rule_collection_group "aks_rules"
application_rule_collection {
  name     = "gpu-and-helm"
  priority = 205
  action   = "Allow"
  rule {
    name             = "gpu-operator-and-helm-repos"
    source_addresses = var.aks_subnet_address_prefix_list
    destination_fqdns = [
      "nvcr.io",                     # NVIDIA container images
      "helm.ngc.nvidia.com",         # NVIDIA Helm repo (GPU Operator)
      "quay.io",                     # some deps (prometheus, etc.)
      "kubernetes.github.io",        # ingress-nginx Helm repo
      "ghcr.io"                      # common images in charts
    ]
    protocols { 
      type = "Https" 
      port = 443 
      }
  }
}

# Append inside azurerm_firewall_policy_rule_collection_group "aks_rules"
application_rule_collection {
  name     = "aks-core-fqdn-tag"
  priority = 210
  action   = "Allow"

  rule {
    name             = "aks-allow-fqdn-tag"
    source_addresses = var.aks_subnet_address_prefix_list
    destination_fqdn_tags        = ["AzureKubernetesService"]
    protocols { 
      type = "Https" 
      port = 443 
      }
  }
}

  # ── Network Rules ──
  network_rule_collection {
    name     = "infra"
    priority = 100
    action   = "Allow"

    # NTP
    rule {
      name                  = "ntp"
      source_addresses      = var.aks_subnet_address_prefix_list
      destination_fqdns     = ["ntp.ubuntu.com", "time.windows.com"]
      destination_ports     = ["123"]
      protocols             = ["UDP"]
    }
    # DNS to Azure-provided DNS VIP (needed since we route all egress via FW)
    rule {
      name                  = "azure-dns-1686312916"
      source_addresses      = var.aks_subnet_address_prefix_list
      destination_addresses = ["168.63.129.16"]
      destination_ports     = ["53"]
      protocols             = ["UDP", "TCP"]
    }

    # Azure health probes/infra VIP (covers LB probe responses)
    rule {
      name                  = "azure-vip-1686312916"
      source_addresses      = var.aks_subnet_address_prefix_list
      destination_addresses = ["168.63.129.16"]
      destination_ports     = ["*"]
      protocols             = ["TCP"]
    }

  }
}

resource "azurerm_firewall_policy_rule_collection_group" "aks_dnat" {
  name               = "aks-dnat-rules"
  firewall_policy_id = var.azurerm_firewall_policy_aks_policy_id
  priority           = 200

  nat_rule_collection {
    name     = "ingress-ilb"
    priority = 100
    action   = "Dnat"

    rule {
      name = "allow-ilb-http"
      source_addresses = ["*"]
      destination_address = var.azurerm_public_ip_fw_pip_id_address # Firewall PIP
      destination_ports     = ["80"]
      protocols             = ["TCP"]

      translated_address = var.ingress_ilb_ip  # The ingress ILB private IP (10.240.x.x)
      translated_port    = "80"                # Will map 80 -> 80, 443 -> 443
    }

    rule {
      name = "allow-ilb-https"
      source_addresses = ["*"]
      destination_address = var.azurerm_public_ip_fw_pip_id_address # Firewall PIP
      destination_ports     = ["443"]
      protocols             = ["TCP"]

      translated_address = var.ingress_ilb_ip  # The ingress ILB private IP (10.240.x.x)
      translated_port    = "443"                # Will map 80 -> 80, 443 -> 443
    }

  }
}


