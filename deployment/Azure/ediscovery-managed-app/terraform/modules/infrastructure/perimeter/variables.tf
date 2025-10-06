variable "resource_group_name" {
  type = string
}


variable "location" {
  type = string
}

variable "address_space" {
  default = ["10.240.0.0/16"]
  type    = list(string)
}

variable "tagkey" {
  type = string
}

variable "tagvalue" {
  type = string
}

variable "aks_subnet_address_prefix" {
  type = string
}

variable "general_subnet_address_prefix" {
  type = string
}

variable "azurerm_route_table_aks_rt_name" {
  type = string
}

variable "azurerm_firewall_policy_aks_policy_id" {
  type = string
}


variable "aks_subnet_address_prefix_list" {
  type = list(string)
}

variable "pe_subnet_address_prefix" {
  type = string
}

variable "postgres_subnet_address_prefix" {
  type = string
}



variable "azurerm_subnet_firewall_id" {
  type = string
}



variable "aks_subnet_id" {
  type = string
}

variable "aks_subnet_name" {
  type = string
}

variable "virtual_network_id" {
  type = string
}

variable "virtual_network_name" {
  type = string
}

variable "workload_nsg_id" {
  type = string
}

variable "workload_nsg_name" {
  type = string
}

