

variable "aks_compute_default" {
  type      = string
}

variable "aks_compute_cpu" {
  type      = string
}

variable "aks_compute_gpu" {
  type      = string
}

variable "resource_group_name" { type = string }
variable "resource_location" { type = string }

variable "db_admin_password" {
  type      = string
  sensitive = true
}

variable "admin_login" {
  type      = string
  sensitive = true
  default   = "ediscoveryadmin"
}

variable "hostname" {
  description = "Client's DNS hostname (must be mapped to the ingress IP)"
  type        = string
  default     = ""
}

variable "hostname_path" {
  description = "Client's DNS hostname full path(must be mapped to the ingress IP)"
  type        = string
  default     = ""
}




variable "allowed_ip_ranges" {
  description = "Comma-separated list of allowed IP CIDRs"
  type        = string
}


variable "static_env_vars" {
  type        = map(string)
  description = "Static environment variables passed to frontend container"
}

variable "subscription_id" {
  type = string
}


variable "tenant_id" {
  type = string
}

variable "network_watcher_rg_id" { default = "NetworkWatcherRG" }

variable "publisher_username" {
  type      = string
  sensitive = true
}
variable "publisher_password" {
  type      = string
  sensitive = true
}

variable "export_activity" {
  type    = bool
  default = false
}

variable "workspace_retention_days" {
  type    = number
  default = 180
}


variable "vpn_server_app_id" {
  description = "Application (client) ID of the pre-created vpn-server app registration"
  type        = string
}

variable "frontend_aad_client_id" {
  description = "Application (client) ID of the pre-created vpn-server app registration"
  type        = string
}

variable "frontend_aad_client_secret" {
  description = "Application (client) ID of the pre-created vpn-server app registration"
  type        = string
}





