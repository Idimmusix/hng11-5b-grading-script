output "private_ip" {
    value = google_compute_instance.hng.network_interface.0.network_ip
}

output "public_ip" {
    value = google_compute_address.static-ip.address
}