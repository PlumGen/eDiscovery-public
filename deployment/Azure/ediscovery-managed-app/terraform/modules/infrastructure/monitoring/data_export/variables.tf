variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "workspace_id" { type = string }
variable "account_name" { type = string }
variable "container_name" { type = string }
variable "immutability_days" { type = number }
variable "table_names" { type = list(string) }
