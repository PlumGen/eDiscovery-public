terraform {
  required_providers {
    kubernetes = { source = "hashicorp/kubernetes" }
    helm       = { source = "hashicorp/helm" }
  }
}

# Static Public IP in the AKS node RG
#resource "azurerm_public_ip" "ingress" {
#  name                = "ingress-pip"
#  resource_group_name = var.aks_rg
#  location            = var.location
#  allocation_method   = "Static"
#  sku                 = "Standard"
#}

#ip binding 
######################################################################################################################
resource "azurerm_role_assignment" "aks_subnet_network_contrib_kubelet" {
  scope                = var.subnet_id
  role_definition_name = "Network Contributor"
  principal_id         = var.kubelet_identity
}

resource "azurerm_role_assignment" "aks_subnet_network_contrib_uami" {
  scope                = var.subnet_id
  role_definition_name = "Network Contributor"
  principal_id         = var.managed_identity_principal_id
}



resource "helm_release" "nginx_ingress" {
  name             = "nginx-ingress"
  repository       = "https://kubernetes.github.io/ingress-nginx"
  chart            = "ingress-nginx"
  version          = "4.10.1"
  namespace        = "ingress-nginx"
  create_namespace = true

  set = [
    {
      name  = "controller.service.type"
      value = "LoadBalancer"
    },

    # Bind Helm Service to your static IP
#    {
#      name  = "controller.service.loadBalancerIP"
#      value = azurerm_public_ip.ingress.ip_address
#    },

#    {
#      name  = "controller.service.annotations.service\\.beta\\.kubernetes\\.io/azure-pip-name"
#      value = azurerm_public_ip.ingress.name
#    },

#    {
#      name  = "controller.service.annotations.service\\.beta\\.kubernetes\\.io/azure-load-balancer-resource-group"
#      value = var.aks_rg
#    },

    {
      name  = "controller.service.annotations.service\\.beta\\.kubernetes\\.io/azure-load-balancer-internal"
      value = "true"
    },

    {
      name  = "controller.service.annotations.service\\.beta\\.kubernetes\\.io/azure-load-balancer-internal-subnet"
      value = var.aks_subnet_name
    },


    {
      name  = "controller.publishService.enabled"
      value = "true"
    },

    {
      name  = "controller.service.externalTrafficPolicy"
      value = "Local"
    },

    {
      name  = "controller.config.allow-snippet-annotations"
      value = "true"
    },

#    {
#      name  = "controller.service.annotations.service\\.beta\\.kubernetes\\.io/azure-load-balancer-health-probe-request-path"
#      value = "/healthz"
#    }


  ]
}
