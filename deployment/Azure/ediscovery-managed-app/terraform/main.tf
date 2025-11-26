terraform {
  required_version = ">= 1.6.0, < 2.0.0"   # or >= 1.6.0, < 1.13.0
  required_providers {
    azurerm = { source = "hashicorp/azurerm", version = "~> 4.14" }
    azapi   = { source = "azure/azapi",       version = ">= 2.5.0" } # needed for sensitive_body
    kubernetes = { source = "hashicorp/kubernetes", version = ">= 2.20.0" }
    helm       = { source = "hashicorp/helm",       version = ">= 2.10.0" }
    random     = { source = "hashicorp/random",     version = ">= 3.5.1" }
    kubectl = {source  = "gavinbunney/kubectl",     version = ">= 1.14.0" }

  }
}



provider "azurerm" {
  resource_provider_registrations = "none"
  features { 
    }
  use_oidc        = true
  subscription_id = var.subscription_id
}

resource "random_id" "unique" {
  byte_length = 2
}

resource "random_id" "cookie_secret" {
  byte_length = 16
}

locals {
  frontend_authonly = (
    length(trimspace(var.frontend_aad_client_id)) > 0 &&
    length(trimspace(var.frontend_aad_client_secret)) > 0
  ) ? 1 : 0

  generateVPN = (
    length(trimspace(var.vpn_server_app_id)) > 0
  ) ? 1 : 0

}


resource "azurerm_user_assigned_identity" "frontend_identity" {
  name                = "frontend-identity"
  location            = var.resource_location
  resource_group_name = var.resource_group_name


  tags = {
    "Application" = "plumgenediscovery-${var.resource_group_name}"
  }

}

#1 Network Foundation
######################################################
module "networking" {
  source              = "./modules/infrastructure/networking"
  resource_group_name = var.resource_group_name
  location            = var.resource_location

  tagkey                        = "Application"
  tagvalue                      = "plumgenediscovery-${var.resource_group_name}"

}

module "perimeter" {
  source              = "./modules/infrastructure/perimeter"
  resource_group_name = var.resource_group_name
  location            = var.resource_location

  aks_subnet_address_prefix      = module.networking.aks_subnet_address_prefix
  aks_subnet_address_prefix_list = module.networking.aks_subnet_address_prefix_list
  pe_subnet_address_prefix       = module.networking.pe_subnet_address_prefix
  postgres_subnet_address_prefix = module.networking.postgres_subnet_address_prefix
  general_subnet_address_prefix  = module.networking.general_subnet_address_prefix
  
  azurerm_route_table_aks_rt_name = module.networking.azurerm_route_table_aks_rt_name

  azurerm_firewall_policy_aks_policy_id = module.networking.azurerm_firewall_policy_aks_policy_id  

  azurerm_subnet_firewall_id = module.networking.azurerm_subnet_firewall_id

  aks_subnet_id   = module.networking.aks_subnet_id
  aks_subnet_name = module.networking.aks_subnet_name
  virtual_network_name = module.networking.virtual_network_name
  virtual_network_id   = module.networking.virtual_network_id
  workload_nsg_id      = module.networking.workload_nsg_id
  workload_nsg_name    = module.networking.workload_nsg_name


  tagkey                        = "Application"
  tagvalue                      = "plumgenediscovery-${var.resource_group_name}"

  depends_on        = [module.networking]

}

import {
  to = azurerm_virtual_network.main
  id = "/subscriptions/${var.subscription_id}/resourceGroups/${var.resource_group_name}/providers/Microsoft.Network/virtualNetworks/ediscovery-vnet"
}


resource "azurerm_virtual_network" "main" {
  name                = "ediscovery-vnet"
  location            = var.resource_location
  resource_group_name = var.resource_group_name

  # Keep the same address space — import ensures it matches the real one
  address_space = ["10.240.0.0/16"]

  # Add or update DNS servers here
  dns_servers = [module.networking.azurerm_firewall_aks_fw_ip]

  # Optional: protect from accidental recreation
  lifecycle {
    prevent_destroy = true
  }

  depends_on        = [module.lockdown]
}


#End Network Fabric
######################################################
module "vpn" {
  count=local.generateVPN
  
  source              = "./modules/infrastructure/vpn"
  resource_group_name = var.resource_group_name
  location            = var.resource_location

  azurerm_subnet      = module.networking.gateway_subnet_id
  azurerm_public_ip   = module.networking.gateway_public_ip_id
  tenant_id           = var.tenant_id
  vpn_server_app_id   = var.vpn_server_app_id

  tagkey                        = "Application"
  tagvalue                      = "plumgenediscovery-${var.resource_group_name}"

  depends_on        = [azurerm_virtual_network.main] #[module.acr, module.ingress, module.frontend_ingress, module.perimeter] #
}

#######################################################
#Private DNS

module "privateendpoints" {
  source              = "./modules/infrastructure/privateendpoints"
  resource_group_name = var.resource_group_name
  location            = var.resource_location

  azurerm_private_dns_zone_acr_name     = module.perimeter.azurerm_private_dns_zone_acr_name
  azurerm_private_dns_zone_acr_data_name = module.perimeter.azurerm_private_dns_zone_acr_data_name

  azurerm_private_dns_zone_acr_id     = module.perimeter.private_dns_zone_acr_id 
  azurerm_private_dns_zone_acr_data_id = module.perimeter.private_dns_zone_acr_data_id


  azurerm_private_dns_zone_storage_name = module.perimeter.azurerm_private_dns_zone_storage_name  
  azurerm_private_dns_zone_storage_id = module.perimeter.private_dns_zone_storage_id

  private_dns_zone_postgres_id = module.perimeter.private_dns_zone_postgres_id
  azurerm_subnet_private_endpoints_id   = module.networking.pe_subnet_address_id 

  private_connection_acr_resource_id     = module.acr.acr_id
  private_connection_storage_resource_id = module.storage.storage_id
  private_connection_postgres_resource_id = module.postgresql.server_id


  acr_login_server =   module.acr.login_server
  storage_name     =   module.storage.storage_name

  tagkey                        = "Application"
  tagvalue                      = "plumgenediscovery-${var.resource_group_name}"

  depends_on = [module.perimeter, module.storage, module.acr, module.postgresql]
}

#End of PrivateEndpoint
########################################################

resource "azurerm_federated_identity_credential" "frontend_federation" {
  name                = "frontend-federation"
  resource_group_name = var.resource_group_name
  parent_id           = azurerm_user_assigned_identity.frontend_identity.id
  issuer              = module.aks.oidc_issuer_url
  subject             = "system:serviceaccount:default:frontend-sa"
  audience            = ["api://AzureADTokenExchange"]

}

resource "azurerm_federated_identity_credential" "oauth2_proxy_federation" {
  name                = "oauth2-proxy-federation"
  resource_group_name = var.resource_group_name
  parent_id           = azurerm_user_assigned_identity.frontend_identity.id  # AKS managed identity
  issuer              = module.aks.oidc_issuer_url
  subject             = "system:serviceaccount:default:oauth2-proxy"
  audience            = ["api://AzureADTokenExchange"]
}


module "storage" {
  source                        = "./modules/infrastructure/storage"
  resource_group_name           = var.resource_group_name
  location                      = var.resource_location
  storage_suffix                = random_id.unique.hex
  managed_identity_principal_id = azurerm_user_assigned_identity.frontend_identity.principal_id

  tagkey                        = "Application"
  tagvalue                      = "plumgenediscovery-${var.resource_group_name}"
 
  depends_on = [module.networking]

}


module "acr" {
  source              = "./modules/infrastructure/acr"
  resource_group_name = var.resource_group_name
  location            = var.resource_location
  registry_name       = "consumerplumgenediscoveryregistry${random_id.unique.hex}"
  publisher_username  = var.publisher_username
  publisher_password  = var.publisher_password

  tagkey                        = "Application"
  tagvalue                      = "plumgenediscovery-${var.resource_group_name}"

  depends_on = [module.networking]
} 


module "postgresql" {
  source                        = "./modules/infrastructure/postgresql"
  resource_group_name           = var.resource_group_name
  location                      = var.resource_location
  db_name                       = "ediscovery-${var.resource_group_name}"
  admin_login                   = var.admin_login
  admin_password                = var.db_admin_password
  subnet_cidr                   = module.networking.postgres_subnet_address_prefix
  managed_identity_principal_id = azurerm_user_assigned_identity.frontend_identity.principal_id

  private_dns_zone_postgres_id = module.perimeter.private_dns_zone_postgres_id
  private_endpoints_subnet_id  = module.networking.postgres_subnet_id


  tagkey                        = "Application"
  tagvalue                      = "plumgenediscovery-${var.resource_group_name}"

  #depends_on = [module.networking, module.perimeter]
}



module "frontend_ingress" {
  depends_on        = [module.aks, module.postgresql, module.storage, module.acr]
  source            = "./modules/k8s/frontend"
  hostname          = var.hostname
  allowed_ip_ranges = var.allowed_ip_ranges
  service_name      = "ediscovery-frontend"
  service_port      = 80

  frontend_aad_client_id = var.frontend_aad_client_id
  frontend_authonly      = local.frontend_authonly
  
  static_env_vars            = var.static_env_vars
  location                   = var.resource_location
  db_fqdn                    = module.postgresql.db_fqdn
  db_name                    = module.postgresql.db_name
  db_user                    = var.admin_login
  db_password                = module.postgresql.db_password
  managed_identity_client_id = azurerm_user_assigned_identity.frontend_identity.client_id 
  storage_account_name       = module.storage.storage_account_name
  subscription_id            = var.subscription_id
  tenant_id                  = var.tenant_id
  acr_login_server           = module.acr.login_server

  tagkey                        = "Application"
  tagvalue                      = "plumgenediscovery-${var.resource_group_name}"


  providers = {
    kubernetes = kubernetes.aks
    helm       = helm.aks
  }


}



provider "kubernetes" {
  alias                  = "aks"
  host                   = module.aks.aks_host
  cluster_ca_certificate = base64decode(module.aks.aks_cluster_ca_certificate)
  client_certificate     = base64decode(module.aks.aks_client_certificate)
  client_key             = base64decode(module.aks.aks_client_key)

}

provider "helm" {
  alias = "aks"
  kubernetes = {
    host                   = module.aks.aks_host
    cluster_ca_certificate = base64decode(module.aks.aks_cluster_ca_certificate)
    client_certificate     = base64decode(module.aks.aks_client_certificate)
    client_key             = base64decode(module.aks.aks_client_key)
  }
}

provider "kubectl" {
  alias                  = "aks"
  host                   = module.aks.aks_host
  cluster_ca_certificate = base64decode(module.aks.aks_cluster_ca_certificate)
  client_certificate     = base64decode(module.aks.aks_client_certificate)
  client_key             = base64decode(module.aks.aks_client_key)

  load_config_file = false

}


resource "azurerm_log_analytics_workspace" "ci" {
  name                = "${var.resource_group_name}-law"
  location            = var.resource_location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = var.workspace_retention_days

  depends_on = [module.networking]   
}

module "aks" {
  depends_on        = [    module.networking,
                            azurerm_log_analytics_workspace.ci,
                            module.acr,
                            module.storage]

  source                         = "./modules/infrastructure/aks"
  resource_group_name            = var.resource_group_name
  location                       = var.resource_location
  cluster_name                   = "ediscovery-aks"
  dns_prefix                     = "ediscovery"
  acr_id                         = module.acr.acr_id
  frontend_identity_principal_id = azurerm_user_assigned_identity.frontend_identity.principal_id #azurerm_user_assigned_identity.frontend_identity.principal_id
  identity_ids                   = azurerm_user_assigned_identity.frontend_identity.id #azurerm_user_assigned_identity.frontend_identity.id
  msi_principal_id               = azurerm_user_assigned_identity.frontend_identity.principal_id
  msi_client_id                  = azurerm_user_assigned_identity.frontend_identity.client_id
  msi_resource_id                = azurerm_user_assigned_identity.frontend_identity.id


  aks_compute_default  = var.aks_compute_default
  aks_compute_cpu  = var.aks_compute_cpu 
  aks_compute_gpu  = var.aks_compute_gpu

  subnet_id    = module.networking.aks_subnet_id
  nsg_id       = module.networking.workload_nsg_id
  subnet_cidr  = module.networking.aks_subnet_address_prefix

  log_analytics_workspace_id = azurerm_log_analytics_workspace.ci.id

  subscription_id            = var.subscription_id
  
  tagkey                        = "Application"
  tagvalue                      = "plumgenediscovery-${var.resource_group_name}"

}

module "ingress" {
  source = "./modules/ingress"

  tagkey                        = "Application"
  tagvalue                      = "plumgenediscovery-${var.resource_group_name}"

  aks_name = module.aks.aks_name
  aks_rg   = module.aks.aks_node_resource_group
  location = module.aks.aks_location

  ## send kubelet identity and subnet
  kubelet_identity = module.aks.kubelet_identity
  managed_identity_principal_id = azurerm_user_assigned_identity.frontend_identity.principal_id 
  subnet_id        = module.networking.aks_subnet_id
  aks_subnet_name  = module.networking.aks_subnet_name

  providers = {
    kubernetes = kubernetes.aks
    helm       = helm.aks
  }

  depends_on        = [module.aks]

}


data "kubernetes_service" "ingress_service" {
  provider   = kubernetes.aks   # 👈 force it to use your AKS kubeconfig
  depends_on = [module.ingress] # waits for Helm install

  metadata {
    name      = "nginx-ingress-ingress-nginx-controller"
    namespace = "ingress-nginx"
  }
}

resource "helm_release" "nvidia_gpu_operator" {
  provider   = helm.aks
  name       = "nvidia-gpu-operator"
  namespace  = "kube-system"
  repository = "https://nvidia.github.io/gpu-operator"
  chart      = "gpu-operator"


  values = [<<-YAML
  operator:
    defaultRuntime: "containerd"

  node-feature-discovery:
    enabled: true
    worker:
      nodeSelector:
        kubernetes.azure.com/agentpool: "gpupool"
      tolerations:
        - key: "nvidia.com/gpu"
          operator: "Exists"
          effect: "NoSchedule"

  driver:
    enabled: true
    nodeSelector: { kubernetes.azure.com/agentpool: "gpupool" }
    tolerations:
      - { key: "nvidia.com/gpu", operator: "Exists", effect: "NoSchedule" }

  toolkit:
    enabled: true
    nodeSelector: { kubernetes.azure.com/agentpool: "gpupool" }
    tolerations:
      - { key: "nvidia.com/gpu", operator: "Exists", effect: "NoSchedule" }

  devicePlugin:
    enabled: true
    nodeSelector: { kubernetes.azure.com/agentpool: "gpupool" }
    tolerations:
      - { key: "nvidia.com/gpu", operator: "Exists", effect: "NoSchedule" }

  gfd:
    enabled: true
    nodeSelector: { kubernetes.azure.com/agentpool: "gpupool" }
    tolerations:
      - { key: "nvidia.com/gpu", operator: "Exists", effect: "NoSchedule" }

  dcgmExporter:
    enabled: true
    nodeSelector: { kubernetes.azure.com/agentpool: "gpupool" }
    tolerations:
      - { key: "nvidia.com/gpu", operator: "Exists", effect: "NoSchedule" }

  migManager:
    enabled: true
    nodeSelector: { kubernetes.azure.com/agentpool: "gpupool" }
    tolerations:
      - { key: "nvidia.com/gpu", operator: "Exists", effect: "NoSchedule" }

  validator:
    nodeSelector: { kubernetes.azure.com/agentpool: "gpupool" }
    tolerations:
      - { key: "nvidia.com/gpu", operator: "Exists", effect: "NoSchedule" }
YAML
  ]


  depends_on = [module.aks]


    
}



locals {
  network_watcher_name = "NetworkWatcher_${var.resource_location}"
  network_watcher_rg   = "NetworkWatcherRG"
}


data "azurerm_client_config" "current" {}

# principalId/objectId of the caller (what RBAC wants)
locals {
  caller_object_id = data.azurerm_client_config.current.object_id
  caller_client_id = data.azurerm_client_config.current.client_id
}


module "monitoring" {
  depends_on = [module.aks, azurerm_log_analytics_workspace.ci]

  source              = "./modules/infrastructure/monitoring"
  location            = var.resource_location
  resource_group_name = var.resource_group_name
  subscription_id     = var.subscription_id

  aks_id                   = module.aks.cluster_id
  workspace_retention_days = var.workspace_retention_days

  enable_container_insights = true
  enable_flow_logs          = true
  nsg_id                    = module.networking.workload_nsg_id

  network_watcher_name      = local.network_watcher_name
  network_watcher_rg_name   = local.network_watcher_rg
  network_watcher_location  = var.resource_location

  aks_parent_id             ="/subscriptions/${var.subscription_id}/resourceGroups/${var.resource_group_name}"
  aks_location              = module.aks.aks_location
  aks_name                  = module.aks.aks_name  



  workspace_id          = azurerm_log_analytics_workspace.ci.id
  workspace_name        = azurerm_log_analytics_workspace.ci.name
  workspace_customer_id = azurerm_log_analytics_workspace.ci.workspace_id
  workspace_region      = azurerm_log_analytics_workspace.ci.location





  runner_object_id          = local.caller_object_id

  enable_activity_log     = true
  activity_log_categories = ["Administrative", "Security", "ServiceHealth", "Alert", "Recommendation", "Policy", "Autoscale", "ResourceHealth"]

  diagnostic_targets = [

    {
      name       = "acr"
      id         = module.acr.acr_id
      categories = ["ContainerRegistryLoginEvents", "ContainerRegistryRepositoryEvents"]
    },
 
  ]

  export_tables            = concat(["ContainerLogV2", "KubeEvents", "KubePodInventory", "AKSAuditAdmin", "AKSControlPlane", "AzureDiagnostics", "PostgreSQLLogs"],
                                      var.export_activity ? ["AzureActivity"] : []
                                    )
  export_account_name      = "ediscoverylogarchive${random_id.unique.hex}"
  export_container_name    = "logarchive${random_id.unique.hex}"
  flowlog_sa_name          = "ediscoveryflowlogsaa${random_id.unique.hex}"

  export_immutability_days = 365

  table_retention_overrides = [{ name = "ContainerLogV2", days = 365 }]

  enable_postgres_pgaudit = true
  postgres_server_id      = module.postgresql.server_id

  tagkey                        = "Application"
  tagvalue                      = "plumgenediscovery-${var.resource_group_name}"  
}


##finallockdown
module "lockdown" {
  source              = "./modules/infrastructure/lockdown"
  resource_group_name = var.resource_group_name
  location            = var.resource_location

  aks_subnet_address_prefix      = module.networking.aks_subnet_address_prefix
  aks_subnet_address_prefix_list = module.networking.aks_subnet_address_prefix_list
  pe_subnet_address_prefix       = module.networking.pe_subnet_address_prefix
  postgres_subnet_address_prefix = module.networking.postgres_subnet_address_prefix
  
  azurerm_route_table_aks_rt_name = module.networking.azurerm_route_table_aks_rt_name

  azurerm_firewall_policy_aks_policy_id = module.networking.azurerm_firewall_policy_aks_policy_id  

  azurerm_public_ip_fw_pip_id_address = module.networking.azurerm_public_ip_fw_pip_id_address
  ingress_ilb_ip = data.kubernetes_service.ingress_service.status[0].load_balancer[0].ingress[0].ip

  azurerm_subnet_firewall_id = module.networking.azurerm_subnet_firewall_id

  aks_subnet_id   = module.networking.aks_subnet_id
  aks_subnet_name = module.networking.aks_subnet_name
  virtual_network_name = module.networking.virtual_network_name
  virtual_network_id   = module.networking.virtual_network_id
  workload_nsg_id      = module.networking.workload_nsg_id
  workload_nsg_name    = module.networking.workload_nsg_name


  tagkey                        = "Application"
  tagvalue                      = "plumgenediscovery-${var.resource_group_name}"

  depends_on        = [module.acr, module.ingress, module.frontend_ingress, module.perimeter, data.kubernetes_service.ingress_service]
}



module "oauth" {
  
  count = local.frontend_authonly

  source = "./modules/oauth"


  frontend_aad_client_id     = var.frontend_aad_client_id

  frontend_aad_client_secret = var.frontend_aad_client_secret
  cookie_secret              = random_id.cookie_secret.hex

  tenant_id              = var.tenant_id
  hostname               = var.hostname
  hostname_path          = var.hostname_path  
  service_name      = "ediscovery-frontend"
  service_port      = 80

  azurerm_public_ip_fw_pip_id_address = module.networking.azurerm_public_ip_fw_pip_id_address

  providers = {
    kubernetes       = kubernetes.aks
    helm             = helm.aks
  }

  depends_on        = [module.aks]
}

module "tlscert" {
  
  source = "./modules/tlscert"

  providers = {
    kubernetes       = kubernetes.aks
    helm             = helm.aks
  }

  depends_on        = [module.aks, data.kubernetes_service.ingress_service, module.lockdown]
}