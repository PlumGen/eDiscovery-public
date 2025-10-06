terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 4.14.0"
    }
  }
}


resource "azurerm_log_analytics_workspace_table" "override" {
  for_each = { for t in var.overrides : t.name => t }

  #resource_group_name     = var.resource_group_name
  workspace_id = var.workspace_id
  name         = each.value.name

  plan                    = "Analytics" # e.g., Analytics or Basic (if applicable)
  retention_in_days       = each.value.days
  total_retention_in_days = each.value.days
}
