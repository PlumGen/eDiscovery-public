# modules/infrastructure/aks/main.tf
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 4.14.0"
    }
    azapi = {
      source  = "azure/azapi"
      version = ">=2.5.0"
    }
  }
}

#"Standard_DS3_v2"
############################
# AKS (no legacy oms_agent)
############################
resource "azurerm_kubernetes_cluster" "aks" {
  name                = var.cluster_name
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = var.dns_prefix

  default_node_pool {
    name       = "default"
    auto_scaling_enabled        = true
    node_count                  = 1
    min_count                   = 1
    max_count                   = 12

    vm_size    = var.aks_compute_default
    vnet_subnet_id = var.subnet_id
    max_pods        = 100
  }

  identity {
    type         = "UserAssigned"
    identity_ids = [var.identity_ids] # UAMI for the control plane
  }

  oidc_issuer_enabled       = true
  workload_identity_enabled = true

  tags = {
    "${var.tagkey}" = var.tagvalue
  }  

  network_profile {
    network_plugin = "azure"
    service_cidr   = "10.0.0.0/16"
    dns_service_ip = "10.0.0.10"
    outbound_type  = "userDefinedRouting"
  }

  api_server_access_profile {
    authorized_ip_ranges = []
    
  }
  
  private_cluster_enabled = true
  private_cluster_public_fqdn_enabled = false
  
  monitor_metrics {
    annotations_allowed = "*"
    labels_allowed      = "*"
  }
}


#########################################
# LAW roles for kubelet identity (optional but common)
#########################################
#resource "azurerm_role_assignment" "kubelet_metrics_publisher" {
#  scope                = var.log_analytics_workspace_id
#  role_definition_name = "Monitoring Metrics Publisher"
#  principal_id         = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
#}

#resource "azurerm_role_assignment" "kubelet_law_contributor" {
#  scope                = var.log_analytics_workspace_id
#  role_definition_name = "Log Analytics Contributor"
#  principal_id         = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
#}

# If you still need to grant your app's UAMI access to LAW, keep these:
# resource "azurerm_role_assignment" "frontend_logs" {
#   scope                = var.log_analytics_workspace_id
#   role_definition_name = "Log Analytics Contributor"
#   principal_id         = var.frontend_identity_principal_id
# }
# resource "azurerm_role_assignment" "frontend_metrics" {
#   scope                = var.log_analytics_workspace_id
#   role_definition_name = "Monitoring Metrics Publisher"
#   principal_id         = var.frontend_identity_principal_id
# }

############################
# DCR (flows + destinations)
############################
#resource "azurerm_monitor_data_collection_rule" "aks_dcr" {
#  name                = "${var.cluster_name}-dcr"
#  location            = var.location
#  resource_group_name = var.resource_group_name

#  destinations {
#    log_analytics {
#      name                  = "law"
#      workspace_resource_id = var.log_analytics_workspace_id
#    }
#  }

#  data_flow {
#    streams      = ["Microsoft-ContainerLogV2", "Microsoft-InsightsMetrics"]
#    destinations = ["law"]
#  }
#}


# Associate the DCR to the AKS cluster
#resource "azurerm_monitor_data_collection_rule_association" "aks_dcra" {
#  name                    = "${var.cluster_name}-dcr-association"
#  target_resource_id      = azurerm_kubernetes_cluster.aks.id
#  data_collection_rule_id = azurerm_monitor_data_collection_rule.aks_dcr.id
#}



#########################################
# RBAC: allow installer MSI to touch AKS
#########################################
# Reader on the AKS resource
resource "azurerm_role_assignment" "aks_reader" {
  scope                = azurerm_kubernetes_cluster.aks.id
  role_definition_name = "Reader"
  principal_id         = var.msi_principal_id
}

# Can install extensions on the AKS resource
#resource "azurerm_role_assignment" "aks_extension_writer" {
#  scope                = azurerm_kubernetes_cluster.aks.id
#  role_definition_name = "AKS ManagedCluster Extensions Writer"
#  principal_id         = var.msi_principal_id
#}

# MC_* resource group scope (computed from the created cluster)
locals {
  mc_rg_id = "/subscriptions/${var.subscription_id}/resourceGroups/${azurerm_kubernetes_cluster.aks.node_resource_group}"
}

# Contributor on MC_* RG (pods/objects deployed by the extension)
#resource "azurerm_role_assignment" "mc_contributor" {
#  scope                = local.mc_rg_id
#  role_definition_name = "Contributor"
#  principal_id         = var.msi_principal_id
#  depends_on           = [azurerm_kubernetes_cluster.aks]
#}

# Extension Writer on MC_* RG (some providers check here too)
#resource "azurerm_role_assignment" "mc_extension_writer" {
#  scope                = local.mc_rg_id
#  role_definition_name = "AKS ManagedCluster Extensions Writer"
#  principal_id         = var.msi_principal_id
#  depends_on           = [azurerm_kubernetes_cluster.aks]
#}


# Add dataSources.extensions via azapi (provider models don’t include it yet)
#resource "azapi_update_resource" "aks_dcr_add_extensions" {
#  type        = "Microsoft.Insights/dataCollectionRules@2022-06-01"
#  resource_id = azurerm_monitor_data_collection_rule.aks_dcr.id

#  body = {
#    properties = {
#      dataSources = {
#        extensions = [{
#          name          = "ci-extension"
#          extensionName = "ContainerInsights"
#          streams       = ["Microsoft-ContainerLogV2", "Microsoft-InsightsMetrics"]
#        }]
#      }
#    }
#  }
#}

##############################################
# AKS extension: azuremonitor-containers (AMA)
##############################################
#resource "azapi_resource" "aks_monitor_extension" {
#  type      = "Microsoft.KubernetesConfiguration/extensions@2023-05-01"
#  name      = "azuremonitor-containers"
#  parent_id = azurerm_kubernetes_cluster.aks.id

#  identity {
#    type = "SystemAssigned"
#  }

#  body = {
#    properties = {
#      extensionType           = "microsoft.azuremonitor.containers"
#      autoUpgradeMinorVersion = true
#      releaseTrain            = "Stable"
#      configurationSettings = {
#        "ama-logs.dcrResourceId" = azurerm_monitor_data_collection_rule.aks_dcr.id
#      }
#    }
#  }

#  depends_on = [
#    #azurerm_role_assignment.mc_contributor,
#    #azurerm_role_assignment.mc_extension_writer,
#    azapi_update_resource.aks_dcr_add_extensions,
#    azurerm_monitor_data_collection_rule_association.aks_dcra
#  ]
#}

# Give the extension’s MSI rights to write to LAW
#resource "azurerm_role_assignment" "law_for_extension_msi" {
#  scope                = var.log_analytics_workspace_id
#  role_definition_name = "Log Analytics Contributor"
#  principal_id         = azapi_resource.aks_monitor_extension.identity[0].principal_id
#  depends_on           = [azapi_resource.aks_monitor_extension]
#}




######################################################################################################################
# AKS kubelet -> ACR (this is what image pulls need)
resource "azurerm_role_assignment" "acr_pull_kubelet" {
  principal_id         = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
  role_definition_name = "AcrPull"
  scope                = var.acr_id

}


# OPTIONAL: only if the frontend UAI must pull/push itself
resource "azurerm_role_assignment" "frontend_acr_pull" {
  principal_id         = var.frontend_identity_principal_id # objectId, not clientId
  role_definition_name = "AcrPull"
  scope                = var.acr_id

}

#Standard_D4ds_v6  -common
#"Standard_D4s_v3"
#priority              = "Spot"
#eviction_policy       = "Delete"        # or "Deallocate"
#spot_max_price        = -1              # -1 means "pay up to on-demand price"

resource "azurerm_kubernetes_cluster_node_pool" "cpupool" {
  name                        = "cpupool"
  kubernetes_cluster_id       = azurerm_kubernetes_cluster.aks.id
  vm_size                     = var.aks_compute_cpu
  mode                        = "User"
  os_type                     = "Linux"
  orchestrator_version        = azurerm_kubernetes_cluster.aks.kubernetes_version
  auto_scaling_enabled        = true
  node_count                  = 0
  min_count                   = 0
  max_count                   = 12
  temporary_name_for_rotation = "cpupooltm"

  max_pods                    = 100

  node_labels = {
        "agentpool" = "cpupool"    
  }

  node_taints = ["cpu-job=true:NoSchedule"]

  tags = {
    "${var.tagkey}" = var.tagvalue
  }  
}

#"Standard_NC4as_T4_v3"
resource "azurerm_kubernetes_cluster_node_pool" "gpupool" {
  name                        = "gpupool"
  kubernetes_cluster_id       = azurerm_kubernetes_cluster.aks.id
  vm_size                     = var.aks_compute_gpu
  mode                        = "User"
  os_type                     = "Linux"
  orchestrator_version        = azurerm_kubernetes_cluster.aks.kubernetes_version
  auto_scaling_enabled        = true
  node_count                  = 0
  min_count                   = 0
  max_count                   = 12
  temporary_name_for_rotation = "gpupooltm"

  max_pods                    = 100

  node_labels = {
        "agentpool" = "gpupool"
  }

  node_taints = [
    "nvidia.com/gpu=:NoSchedule"
  ]


  tags = {
    "${var.tagkey}" = var.tagvalue
  }  
}


