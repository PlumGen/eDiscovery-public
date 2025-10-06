#module "container_insights" {
#  count                    = var.enable_container_insights ? 1 : 0
#  source                   = "./container_insights"
#  location                 = var.location
#  resource_group_name      = var.resource_group_name
#  aks_id                   = var.aks_id
#  workspace_retention_days = var.workspace_retention_days
#  streams                  = var.ci_streams

#  aks_parent_id             = var.aks_parent_id
#  aks_location              = var.aks_location
#  aks_name                  = var.aks_name  

#  runner_object_id          = var.runner_object_id
#}



module "diagnostic_settings" {
  source                  = "./diagnostic_settings"
  diagnostic_targets      = var.diagnostic_targets
  workspace_id            = var.workspace_id

  activity_log_categories = var.activity_log_categories
  subscription_id         = var.subscription_id
}

#module "flow_logs" {
#  count                      = var.enable_flow_logs ? 1 : 0
#  source                     = "./flow_logs"
#  location                   = var.location
#  network_watcher_rg         = var.network_watcher_rg_name
#  resource_group_name        = var.resource_group_name
#  network_watcher_name       = var.network_watcher_name    

#  subscription_id            = var.subscription_id
  
#  nsg_id                     = var.nsg_id 
#  flowlog_sa_name            = var.flowlog_sa_name

#  workspace_customer_id      = var.workspace_customer_id
#  workspace_id               = var.workspace_id
#}


#module "data_export" {
#  source              = "./data_export"
#  resource_group_name = var.resource_group_name
#  location            = var.location
#  workspace_id        = var.workspace_id
#  account_name        = var.export_account_name
#  container_name      = var.export_container_name
#  immutability_days   = var.export_immutability_days
#  table_names         = var.export_tables
#}

module "table_retention" {
  source              = "./table_retention"
  resource_group_name = var.resource_group_name
  workspace_id        = var.workspace_id
  overrides           = var.table_retention_overrides
}

module "postgres_audit" {
  for_each           = var.enable_postgres_pgaudit ? toset(["enabled"]) : toset([])
  source             = "./postgres_audit"
  postgres_server_id = var.postgres_server_id
}
