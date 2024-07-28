output "private_ip" {
    value = google_compute_instance.hng.network_interface.0.network_ip
}

output "public_ip" {
    value = google_compute_address.static-ip.address
}

output "ansible_err" {
    value = ansible_playbook.main.ansible_playbook_stderr
}

output "ansible_out" {
    value = ansible_playbook.main.ansible_playbook_stdout
}