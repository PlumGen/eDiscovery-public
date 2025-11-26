variable "frontend_aad_client_id" {
    type        = string
    description = "Name of the frontend service"
}

variable "tenant_id" {
    type        = string
    description = "tenant ID"  
}
variable "hostname" {
    type        = string
    description = "hostname"  
}

variable "hostname_path" {
    type        = string
    description = "hostname or full path"  
}


variable "service_port" {
  type        = number
  description = "Port that the frontend service exposes"
}

variable "service_name" {
  type        = string
  description = "Name of the frontend service"
}


variable "azurerm_public_ip_fw_pip_id_address" {
  type        = string
  description = "Name of the frontend service"
}

variable "frontend_aad_client_secret" {
  type        = string
  description = "Name of the frontend service"
}

variable "cookie_secret" {
  type        = string
  description = "Name of the frontend service"
}
