provider "google" {
    project     = var.project_id
    region      = var.region
    zone        = var.zone
}

data "local_file" "ssh_keyfile" {
  filename = var.ssh_file
}

data "local_file" "ssh_private_keyfile" {
  filename = var.ssh_private_file
}


resource "google_compute_instance" "hng" {
    provider = google
    name = var.slack_name
    machine_type = var.machine_type #"e2-small"
    network_interface {
        network = google_compute_network.hng.name
        access_config {
            nat_ip = google_compute_address.static-ip.address
        }
    
    }

    metadata = {
        ssh-keys = "${var.slack_name}:${data.local_file.ssh_keyfile.content}"
        user-data = file("${path.module}/cloud-config.yaml")
    }

    boot_disk {
        initialize_params {
            size = 10
            image = "ubuntu-os-cloud/ubuntu-2204-jammy-v20240726"
        }
    }
    
    # Some changes require full VM restarts
    # consider disabling this flag in production
    #   depending on your needs
    allow_stopping_for_update = true
}


resource "local_file" "ip" {
    content  = "{\"public_ip\": \"${google_compute_address.static-ip.address}\"}"
    filename = "ip.json"
    directory_permission = 0775
    file_permission = 0640
}

resource "google_compute_address" "static-ip" {
  provider = google
  name = "${var.slack_name}-ip"
  address_type = "EXTERNAL"
  network_tier = "PREMIUM"
}

# Create a network
resource "google_compute_network" "hng" {
    provider = google
    name = "${var.slack_name}-network"
    auto_create_subnetworks = true
}

# Create a subnet with IPv6 capabilities
# resource "google_compute_subnetwork" "ipv6subnet" {
#     provider = google
#     name = "ipv6subnet"
#     network = google_compute_network.ipv6.id
#     ip_cidr_range = "10.0.0.0/8"
#     stack_type = "IPV4_IPV6"
#     ipv6_access_type = "EXTERNAL"
# }

# Allow SSH from all IPs (insecure, but ok for this tutorial)
resource "google_compute_firewall" "firewall" {
    provider = google
    name    = "${var.slack_name}-firewall"
    network = google_compute_network.hng.name

    source_ranges = ["0.0.0.0/0"]
    allow {
        protocol = "tcp"
        # ports    = ["22", "80", "443", "3000", "9000", ]
    }
}
