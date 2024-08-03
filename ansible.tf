terraform {
  required_providers {
    ansible = {
      version = "~> 1.3.0"
      source  = "ansible/ansible"
    }
  }
}

# Wait for the instance to be ready for SSH
resource "null_resource" "wait_for_instance" {
  depends_on = [google_compute_instance.hng]
  

  provisioner "local-exec" {
    command = <<EOT
    #!/bin/bash
    ssh-keygen -f '/home/idimma/.ssh/known_hosts' -R '${google_compute_address.static-ip.address}'
    # cp ansible_test/ansible.cfg ~
    while true; do
      echo "we are waiting for server port 22 to open"
      if nc -zv -w 5 ${google_compute_address.static-ip.address} 22 2>&1 | grep -q 'succeeded'; then
        echo "port 22 is open now"
        break
      else
        echo "Port 22 is not open yet on ${google_compute_address.static-ip.address}. Retrying..."
        sleep 5  # Wait for 5 seconds before retrying
    fi
    done
    EOT
    interpreter = ["/bin/bash", "-c"]
  }
}

resource "ansible_playbook" "main" {
  playbook   = "testing/main.yaml"
  name       = "hng ansible_ssh_private_key_file=${var.ssh_private_file} ansible_ssh_extra_args='-o StrictHostKeyChecking=no' ansible_ssh_host=${google_compute_address.static-ip.address} ansible_ssh_user=${var.slack_name}"
  replayable = true

  extra_vars = {
    inventory = "inventory.ini"
  }
  depends_on = [null_resource.wait_for_instance]
}
