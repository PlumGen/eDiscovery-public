variable "location" { type = string }
variable "resource_group_name" { type = string }
variable "aks_id" { type = string }
variable "workspace_retention_days" { type = number }
variable "streams" { type = list(string) }

variable "aks_parent_id" { type = string }
variable "aks_location" { type = string }
variable "aks_name" { type = string }

variable "runner_object_id" { type = string }