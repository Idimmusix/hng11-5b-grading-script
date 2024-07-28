resource "local_file" "ansible_inventory" {
  content = templatefile("inventory.tftpl", {
    host = google_compute_address.static-ip.address
    user = var.slack_name
    ssh_keyfile = var.ssh_private_file
  })
  filename = format("%s/%s", abspath(path.root), "inventory.ini")
  file_permission = 0600
  directory_permission = 0755
}
