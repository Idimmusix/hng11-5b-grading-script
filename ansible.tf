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
  name       = "hng ansible_ssh_private_key_file=${var.ssh_private_file} ansible_ssh_extra_args='-o StrictHostKeyChecking=no' ansible_ssh_host=${google_compute_address.static-ip.address} ansible_ssh_user=${var.slack_name}"
  replayable = true

  extra_vars = {
    inventory = "inventory.ini"
  }
  depends_on = [local_file.ip, google_compute_instance.hng]
}