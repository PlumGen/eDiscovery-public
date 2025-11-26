terraform {
  required_providers {

    azapi = {
      source  = "azure/azapi"
      version = ">=2.5.0"
    }
  }
}




locals {
  flat_images = flatten([
    for repo, tags in var.images : [
      for tag in tags : {
        repo = repo
        tag  = tag
        key  = "${repo}:${tag}"
      }
    ]
  ])

  by_key = { for i in local.flat_images : i.key => i }
}

# your ACR (consumer) – you already have this; shown here for completeness
resource "azurerm_container_registry" "acr" {
  name                = var.registry_name
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "Premium"
  admin_enabled       = false
  public_network_access_enabled = false # optional
  data_endpoint_enabled       = true
  
  tags = {
    "${var.tagkey}" = var.tagvalue
  }

}

resource "azapi_resource_action" "import_images" {
  for_each    = local.by_key
  type        = "Microsoft.ContainerRegistry/registries@2023-06-01-preview"
  resource_id = azurerm_container_registry.acr.id
  action      = "importImage"
  method      = "POST"

  body = sensitive({
    source = {
      registryUri = var.publisher_login_server
      sourceImage = "${each.value.repo}:${each.value.tag}"
      credentials = {
        username = var.publisher_username
        password = var.publisher_password
      }
    }
    targetTags = ["${each.value.repo}:${each.value.tag}"]
    mode       = "Force"
  })

  response_export_values = []


    
}
