# modules/k8s/frontend/variables.tf
variable "hostname" {
  type        = string
  description = "DNS host used by the ingress (e.g., only allow access if address is: ediscovery.lawfirm.com)"
  default     = ""
}

variable "allowed_ip_ranges" {
  type        = string
  description = "Comma-separated list of allowed source IPs (CIDR blocks)"
}

variable "service_name" {
  type        = string
  description = "Name of the frontend service"
}

variable "location" {
  type        = string
  description = "Cloud Region, east, west, etc."
}

variable "service_port" {
  type        = number
  description = "Port that the frontend service exposes"
}

variable "db_fqdn" {}
variable "db_name" {}
variable "db_user" {}
variable "db_password" {}

variable "static_env_vars" {
  type    = map(string)
  default = {}
}

variable "tenant_id" {
  type        = string
  description = "tenant ID for the federated identity binding and refresh"
}

variable "managed_identity_client_id" {
  type        = string
  description = "Client ID for the federated identity binding"
}

variable "storage_account_name" {
  type        = string
  description = "name of storage account"
}

variable "subscription_id" {
  type        = string
  description = "subscription id for Azure account"
}


variable "acr_login_server" { 
  type = string 
  }
variable "frontend_image_tag" {
   type = string  
   default = "latest" 
   }

variable "tagkey" {
  type = string
}

variable "tagvalue" {
  type = string
}

variable "frontend_authonly" {
  type = string
}

variable "frontend_aad_client_id" {
  type = string
}

