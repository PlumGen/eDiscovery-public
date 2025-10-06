variable "workspace_id" { type = string }

variable "enable_diagnostic_activity_log" { 
                                type = bool
                                default = false 
                                }
                                
variable "activity_log_categories" { type = list(string) }

variable "subscription_id" {
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
