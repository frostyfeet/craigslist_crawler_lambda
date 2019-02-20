variable "region" {
  description = "Region to run assessment on, and where resources are placed"
  default     = "us-west-2"
}
variable "contact" {
  description = "Value for Contact tag"
  default     = "Pablo"
}

variable "service" {
  description = "Value for Service tag"
  default     = "craigslist-slack"
}

variable "type" {
  description = "Value for Type tag"
  default     = "craigslist_lambda"
}

variable "env" {
  description = "Value for Environment tag"
  default = "production"
}

