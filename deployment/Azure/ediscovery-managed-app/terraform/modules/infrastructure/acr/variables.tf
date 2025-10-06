variable "registry_name" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "location" {
  type = string
}


variable "tagkey" {
  type = string
}

variable "tagvalue" {
  type = string
}


# ------- inputs -------
variable "publisher_login_server" {
  type    = string
  default = "plumgenediscoverypublished.azurecr.io"
}

variable "publisher_username" {
  type      = string
  sensitive = true
}
variable "publisher_password" {
  type      = string
  sensitive = true
}


variable "images" {
  type = map(list(string))
  default = {
    "ediscovery-frontend-image"    = ["latest"]
    "ediscovery-backend-gpu-image" = ["latest"]
  }
}