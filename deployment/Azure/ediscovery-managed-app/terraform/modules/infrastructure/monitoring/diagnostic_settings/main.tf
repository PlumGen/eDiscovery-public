data "azurerm_client_config" "current" {}

resource "azurerm_monitor_diagnostic_setting" "target" {
  for_each                   = { for t in var.diagnostic_targets : t.name => t } # <- static keys
  name                       = "diagm-${each.key}"
  target_resource_id         = each.value.id
  log_analytics_workspace_id = var.workspace_id 

  dynamic "enabled_log" {
    for_each = toset(each.value.categories)
    content {
      category = enabled_log.value
    }
  }
}


resource "azurerm_monitor_diagnostic_setting" "activity" {
  count                      = var.enable_diagnostic_activity_log ? 1 : 0
  name                       = "subscription-activity-to-la"
  target_resource_id         = "/subscriptions/${var.subscription_id}"
  log_analytics_workspace_id = var.workspace_id

  dynamic "enabled_log" {
    for_each = toset(var.activity_log_categories)
    content {
      category = enabled_log.value

    }
  }
}

