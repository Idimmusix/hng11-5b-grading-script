terraform {
  required_providers {
    ansible = {
      version = "~> 1.3.0"
      source  = "ansible/ansible"
    }
  }
}

resource "ansible_playbook" "main" {
  playbook   = "ansible_test/main.yaml"
  name       = var.slack_name
  replayable = false

  extra_vars = {
    inventory = "inventory.ini"
  }
  depends_on = [local_file.ip, google_compute_instance.hng]
}