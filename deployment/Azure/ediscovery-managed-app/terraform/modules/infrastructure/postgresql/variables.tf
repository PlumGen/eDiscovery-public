# modules/infrastructure/postgresql/variables.tf
variable "db_name" {
  type = string
}

variable "admin_login" {
  type = string
}

variable "admin_password" {
  type      = string
  sensitive = true
}

variable "resource_group_name" {
  type = string
}

variable "location" {
  type = string
}



variable "subnet_cidr" {
  type = string
}

variable "managed_identity_principal_id" {
  type        = string
  description = "Principal ID of the workload identity for role assignment"
}

variable "tagkey" {
  type = string
}

variable "tagvalue" {
  type = string
}

variable "private_endpoints_subnet_id" {
  type = string
}

variable "private_dns_zone_postgres_id" {
  type = string
}



