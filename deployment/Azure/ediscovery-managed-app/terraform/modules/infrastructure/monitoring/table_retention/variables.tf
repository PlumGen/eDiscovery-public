variable "resource_group_name" { type = string }
variable "workspace_id" { type = string }
variable "overrides" { type = list(object({ name = string, days = number })) }


