# modules/infrastructure/storage/variables.tf
variable "storage_suffix" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "location" {
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
