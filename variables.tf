variable "machine_type" {
    description = "Type of GCP machine to spin up"
    type        = string
    default     = "e2-small"
}

variable "slack_name" {
    description = "Slack Name of the owner of the intern"
    type        = string
    default     = "hng11"
}

variable "project_id" {
    description = "ID of the google cloud project to run"
    type        = string
    default     = "lovemeapp-1"
}

variable "zone" {
    description = "GCP Zone to run"
    type        = string
    default     = "europe-west2-b"
}

variable "region" {
    description = "GCP Region to run"
    type        = string
    default     = "europe-west2"
}

variable "ssh_file" {
    description = "Public SSH file for accessing the server"
    type = string
    default = "hng.pub"
}

variable "ssh_private_file" {
    default = "hng2"
}