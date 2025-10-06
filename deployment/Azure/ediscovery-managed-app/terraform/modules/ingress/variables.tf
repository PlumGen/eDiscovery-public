variable "namespace" {
  type    = string
  default = "ingress-nginx"
}

# Optional if you want to set a static IP
# variable "load_balancer_ip" {
#   type    = string
#   default = null
# }

variable "tagkey" {
  type = string
}

variable "tagvalue" {
  type = string
}

variable "aks_name" {
  type = string
}

variable "aks_rg" {
  type = string
}
variable "location" {
  type = string
}

variable "kubelet_identity" {
  type = string
}
variable "subnet_id" {
  type = string
}
variable "managed_identity_principal_id" {
  type = string
}
variable "aks_subnet_name" {
  type = string
}

