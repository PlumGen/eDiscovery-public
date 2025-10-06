# modules/infrastructure/aks/variables.tf
variable "cluster_name" {
  type = string
}

variable "aks_compute_default" {
  type      = string
}

variable "aks_compute_cpu" {
  type      = string
}

variable "aks_compute_gpu" {
  type      = string
}

variable "subscription_id" {
  type      = string
}

variable "msi_principal_id" {
  type = string
}

variable "msi_client_id" {
  type = string
}

variable "msi_resource_id" {
  type = string
}


variable "resource_group_name" {
  type = string
}

variable "location" {
  type = string
}

variable "dns_prefix" {
  type    = string
  default = "ediscovery"
}

variable "acr_id" {
  type = string
}

variable "frontend_identity_principal_id" {
  type = string
}

variable "identity_ids" {
  type = string
}

variable "tagkey" {
  type = string
}

variable "tagvalue" {
  type = string
}


variable "subnet_id" {
  type = string
}

variable "nsg_id" {
  type = string
}

variable "subnet_cidr" {
  type = string
}

variable "log_analytics_workspace_id" {
  type = string
}

