variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "aks_id" {
  type = string
}


variable "subscription_id" {
  type    = string
  default = null
}

 
variable "workspace_region" {
  type    = string
  default = null
}

variable "workspace_retention_days" {
  type    = number
  default = 180
}

variable "workspace_name" {
  type    = string
  default = null
}

variable "workspace_customer_id" {
  type    = string
  default = null
}

variable "workspace_id" {
  type    = string
  default = null
}




variable "enable_flow_logs" {
  type    = string
}

variable "enable_container_insights" {
  type    = bool
  default = true
}

variable "ci_streams" {
  type = list(string)
  default = [
    "Microsoft-ContainerLogV2",
    "Microsoft-KubeEvents",
    "Microsoft-KubePodInventory",
    "Microsoft-KubeNodeInventory",
    "Microsoft-KubeServices",
    "Microsoft-KubePVInventory",
    "Microsoft-ContainerInventory",
    "Microsoft-ContainerNodeInventory",
    "Microsoft-InsightsMetrics",
    "Microsoft-Perf"
  ]
}



variable "enable_activity_log" {
  type    = bool
  default = true
}

variable "activity_log_categories" {
  type = list(string)
  default = [
    "Administrative",
    "Security",
    "ServiceHealth",
    "Alert",
    "Recommendation",
    "Policy",
    "Autoscale",
    "ResourceHealth"
  ]
}


variable "network_watcher_rg_id" {
  type    = string
  default = "NetworkWatcherRG"
}

variable "nsg_id" {
  type    = string
  default = null
}

variable "flowlog_sa_name" {
  type    = string
}

variable "export_tables" {
  type    = list(string)
  default = []
}

variable "export_account_name" {
  type    = string
}

variable "export_container_name" {
  type    = string
}

variable "export_immutability_days" {
  type    = number
  default = 365
}

variable "table_retention_overrides" {
  type = list(object({
    name = string
    days = number
  }))
  default = []
}

variable "enable_postgres_pgaudit" {
  type    = bool
  default = false
}

variable "postgres_server_id" {
  type    = string
  default = null
}


variable "diagnostic_targets" {
  type = list(object({
    name       = string
    id         = string
    categories = list(string)
  }))
}

variable "tagkey" {
  type = string
}

variable "tagvalue" {
  type = string
}


variable "network_watcher_name" { type = string }
variable "network_watcher_rg_name" { type = string }
variable "network_watcher_location" { type = string }




variable "aks_parent_id" { type = string }
variable "aks_location" { type = string }
variable "aks_name" { type = string }

variable "runner_object_id" { type = string }

