import os
import sys
import subprocess
import json
import logging
import shutil
from time import sleep

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def run_command(command, error_message="Error running command", fail_on_error=True):
    try:
        logging.debug(f"Running command: {command}")
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        logging.debug(f"Command output: {result.stdout.decode('utf-8')}")
        return result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        logging.error(f"{error_message}: {e.stderr.decode('utf-8')}")
        if fail_on_error:
            sys.exit(1)
        return None

# def create_terraform_files(slack_name, project_id, region, zone, instance_type, key_name, private_key_path):
#     """Create Terraform configuration files."""
#     terraform_main = f"""
#     provider "google" {{
#         project     = "{project_id}"
#         region      = "{region}"
#         zone        = "{zone}"
#     }}
#     resource "google_compute_instance" "hng" {{
#         provider = google
#         name = {slack_name}
#         machine_type = "{instance_type}" #"e2-small"
#         network_interface {{
#             network = google_compute_network.hng.name
#             access_config {{
#                 nat_ip = google_compute_address.static-ip.address
#             }}
#         }}

#         data "local_file" "ssh_keyfile" {{
#             filename = "{key_name}"
#         }}

#         metadata = {{
#             ssh-keys = "{slack_name}:${{data.local_file.ssh_keyfile.content}}"
#             user-data = file("${{path.module}}/cloud-config.yaml")
#         }}

#         boot_disk {{
#             initialize_params {{
#                 size = 10
#                 image = "ubuntu-os-cloud/ubuntu-2204-jammy-v20240726"
#             }}
#         }}
#         allow_stopping_for_update = true
#     }}

#     resource "google_compute_address" "static-ip" {{
#         provider = google
#         name = "hng11-ip"
#         address_type = "EXTERNAL"
#         network_tier = "PREMIUM"
#     }}

#     resource "google_compute_network" "hng" {{
#         provider = google
#         name = "hngnetwork"
#         auto_create_subnetworks = true
#     }}

#     resource "google_compute_firewall" "firewall" {{
#         provider = google
#         name    = "hngfirewall"
#         network = google_compute_network.hng.name

#         source_ranges = ["0.0.0.0/0"]
#         allow {{
#             protocol = "tcp"
#         }}
#     }}

#     provisioner "local-exec" {{
#         command = "printf '{{\\"public_ip\\": \\"%s\\"}}' ${{self.public_ip}} > instance_ip.json"
#     }}

#     output "public_ip" {{
#         value = google_compute_address.static-ip.address
#     }}
#     # Wait for the instance to be ready for SSH
#     resource "null_resource" "wait_for_instance" {{
#         depends_on = [google_compute_instance.hng]
    

#         provisioner "local-exec" {{
#             command = <<EOT
#             #!/bin/bash
#             # cp ansible_test/ansible.cfg ~/.ansible.cfg
#             while true; do
#             echo "we are waiting for server port 22 to open"
#             if nc -zv -w 5 ${{google_compute_address.static-ip.address}} 22 2>&1 | grep -q 'succeeded'; then
#                 echo "port 22 is open now"
#                 break
#             else
#                 echo "Port 22 is not open yet on ${{google_compute_address.static-ip.address}}. Retrying..."
#                 sleep 5  # Wait for 5 seconds before retrying
#             fi
#             done
#             EOT
#             interpreter = ["/bin/bash", "-c"]
#         }}
#     }}
#     """
#     with open("main.tf", "w") as f:
#         f.write(terraform_main)
    
#     logging.info("Terraform configuration files created.")
#     run_command("terraform init", "Terraform initialization failed")

# def create_terraform_files(region, instance_type, key_name, private_key_path):
#     """Create Terraform configuration files."""
#     terraform_main = f"""
#     provider "aws" {{
#       region = "{region}"
#     }}

#     resource "aws_key_pair" "deployer_key" {{
#       key_name   = "{key_name}"
#       public_key = file("{private_key_path}.pub")
#     }}

#     resource "aws_security_group" "allow_all_traffic" {{
#       name_prefix = "allow_all_traffic_"
      
#       ingress {{
#         from_port   = 0
#         to_port     = 65535
#         protocol    = "tcp"
#         cidr_blocks = ["0.0.0.0/0"]
#       }}

#       egress {{
#         from_port   = 0
#         to_port     = 65535
#         protocol    = "tcp"
#         cidr_blocks = ["0.0.0.0/0"]
#       }}

#       tags = {{
#         Name = "allow_all_traffic"
#       }}
#     }}

#     resource "aws_instance" "server" {{
#       ami           = "ami-0491f59ddbd8b9a64" # Ubuntu 22.04 AMI
#       instance_type = "{instance_type}"
#       key_name      = "{key_name}"
#       vpc_security_group_ids = [aws_security_group.allow_all_traffic.id]

#       tags = {{
#         Name = "Ansible-Terraform-Instance"
#       }}

#       provisioner "local-exec" {{
#         command = "printf '{{\\"public_ip\\": \\"%s\\"}}' ${{self.public_ip}} > instance_ip.json"
#       }}
#     }}

#     output "public_ip" {{
#       value = aws_instance.server.public_ip
#     }}
#     """
    
#     with open("main.tf", "w") as f:
#         f.write(terraform_main)
    
#     logging.info("Terraform configuration files created.")
#     run_command("terraform init", "Terraform initialization failed")

def apply_terraform():
    """Apply Terraform configuration to create the EC2 instance."""
    logging.info("Applying Terraform configuration...")
    run_command("terraform apply -auto-approve", "Terraform apply failed")
    logging.info("Terraform apply complete.")

def destroy_terraform(slack_name):
    """Destroy Terraform-managed infrastructure."""
    logging.info("Destroying Terraform-managed infrastructure...")
    slack_name_var=f"slack_name={slack_name}"
    run_command(f"terraform destroy -auto-approve -var={slack_name_var}", "Terraform destroy failed")
    logging.info("Infrastructure destroyed.")

def create_ansible_inventory(ip_address, key_path):
    """Create Ansible inventory file with hostname 'hng'."""
    inventory_content = f"""
    [hng]
    {ip_address} ansible_user=ubuntu ansible_ssh_private_key_file={key_path} ansible_ssh_extra_args='-o StrictHostKeyChecking=no' ansible_python_interpreter=/usr/bin/python3
    """
    with open("inventory.cfg", "w") as f:
        f.write(inventory_content)
    logging.info(f"Ansible inventory file created with hostname 'hng' for IP: {ip_address}")

# def create_ssh_key(key_name):
#     """Create an SSH key pair locally."""
#     private_key_path = f"./{key_name}"
#     public_key_path = f"{private_key_path}.pub"

#     if not os.path.exists(private_key_path):
#         logging.info(f"Creating SSH key pair: {key_name}")
#         run_command(f"ssh-keygen -t rsa -b 2048 -f {private_key_path} -q -N ''", "SSH key generation failed")
#     else:
#         logging.info(f"SSH key pair already exists: {key_name}")

#     return private_key_path

def clone_repo(github_repo):
    """Clone the specified GitHub repository into a 'testing' directory, replacing it if it already exists."""
    testing_dir = os.path.join(os.getcwd(), 'testing')
    
    if os.path.exists(testing_dir):
        logging.info(f"Removing existing directory: {testing_dir}")
        shutil.rmtree(testing_dir)
    
    os.makedirs(testing_dir, exist_ok=True)
    logging.info(f"Cloning repository {github_repo} into {testing_dir}...")
    run_command(f"git clone {github_repo} {testing_dir}", "Git clone failed")
    logging.info(f"Repository cloned into {testing_dir}")

def run_ansible_playbook():
    """Run Ansible playbook with enhanced error handling."""
    logging.info("Running Ansible playbook...")

    playbook_path = None
    for ext in ['yaml', 'yml']:
        if os.path.exists(f"testing/main.{ext}"):
            playbook_path = f"testing/main.{ext}"
            break
    
    if not playbook_path:
        logging.error("No playbook file found in 'testing' directory.")
        sys.exit(1)

    try:
        result = subprocess.run(
            f"ansible-playbook -i inventory.cfg {playbook_path} -b",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        logging.info("Ansible playbook execution complete.")
        logging.debug(f"Playbook stdout: {result.stdout.decode('utf-8')}")
    except subprocess.CalledProcessError as e:
        logging.error("Ansible playbook execution failed:")
        logging.error(e.stderr.decode('utf-8'))
        logging.error(e.stdout.decode('utf-8'))
        sys.exit(1)

def grade_deployment(ip_address, key_path, user):
    """Grade the deployment based on the criteria."""
    total_score = 0
    max_score = 10  

    logging.info("Grading deployment...")

    def check_condition(condition, weight):
        """Helper function to log results and update the score."""
        nonlocal total_score
        if condition:
            total_score += weight
            logging.info(f"Test Passed: +{weight} marks")
        else:
            logging.info(f"Test Failed: 0 marks")

    logging.info("Checking if 'inventory.cfg' does not exist in the cloned directory...")
    check_condition(not os.path.exists("testing/inventory.cfg"), 0.5)

    logging.info("Checking if 'main.yaml' exists in the cloned directory...")
    check_condition(os.path.exists("testing/main.yaml"), 0.5)

    logging.info("Checking if 'main.yaml' contains 'hosts: hng'...")
    try:
        with open("testing/main.yaml") as f:
            check_condition('hosts: hng' in f.read(), 0.5)
    except FileNotFoundError:
        check_condition(False, 0.5)

    logging.info("Checking if port 3000 is returning content...")
    result = run_command(f"ssh -i {key_path} -o StrictHostKeyChecking=no {user}@{ip_address} 'curl -s http://127.0.0.1:3000'", fail_on_error=False)
    check_condition(result is not None and len(result) > 0, 1)

    logging.info("Checking if port 3000 is not accessible from the internet...")
    result = run_command(f"curl -s http://{ip_address}:3000", fail_on_error=False)
    check_condition(result is None or len(result) == 0, 0.5)

    logging.info("Checking if port 80 is accessible from the internet and returning content...")
    result = run_command(f"curl -s http://{ip_address}", fail_on_error=False)
    check_condition(result is not None and len(result) > 0, 0.5)

    logging.info("Checking if 'hng' user is created on the server...")
    result = run_command(f"ssh -i {key_path} -o StrictHostKeyChecking=no {user}@{ip_address} 'id -u hng'", fail_on_error=False)
    check_condition(result is not None and "no such user" not in result.lower(), 0.5)

    logging.info("Checking if 'hng' user has sudo access...")
    result = run_command(f"ssh -i {key_path} -o StrictHostKeyChecking=no {user}@{ip_address} 'sudo -l -U hng'", fail_on_error=False)
    check_condition(result is not None and "may run the following commands on" in result, 0.5)

    logging.info("Checking if PostgreSQL is running on the server...")
    result = run_command(f"ssh -i {key_path} -o StrictHostKeyChecking=no {user}@{ip_address} 'pg_isready'", fail_on_error=False)
    check_condition(result is not None and "accepting connections" in result, 0.5)

    logging.info("Checking if the directory '/opt/stage_5b' exists...")
    result = run_command(f"ssh -i {key_path} -o StrictHostKeyChecking=no {user}@{ip_address} 'ls /opt/stage_5b'", fail_on_error=False)
    check_condition(result is not None and "No such file or directory" not in result, 0.5)

    logging.info("Checking if the repository was cloned from 'https://github.com/hngprojects' and is on the 'devops' branch...")
    repo_check_command = f"ssh -i {key_path} -o StrictHostKeyChecking=no {user}@{ip_address} 'git config --global --add safe.directory /opt/stage_5b && cd /opt/stage_5b && git remote get-url origin && git branch --show-current'"
    result = run_command(repo_check_command, fail_on_error=False)
    check_condition(result is not None and "https://github.com/hngprojects" in result and "devops" in result, 0.5)

    logging.info("Checking if '/opt/stage_5b' is owned by the 'hng' user...")
    result = run_command(f"ssh -i {key_path} -o StrictHostKeyChecking=no {user}@{ip_address} 'stat -c \"%U\" /opt/stage_5b'", fail_on_error=False)
    check_condition(result is not None and "hng" in result, 0.5)

    logging.info("Checking if nginx is running on the server...")
    result = run_command(f"ssh -i {key_path} -o StrictHostKeyChecking=no {user}@{ip_address} 'systemctl status nginx'", fail_on_error=False)
    check_condition(result is not None and "active (running)" in result, 0.5)

    logging.info("Checking if nginx version is 1.26...")
    result = run_command(f"ssh -i {key_path} -o StrictHostKeyChecking=no {user}@{ip_address} 'nginx -v 2>&1'", fail_on_error=False)
    check_condition(result is not None and "nginx/1.26" in result, 0.5)

    logging.info("Checking if '/var/secrets/pg_pw.txt' exists and is not empty...")
    result = run_command(f"ssh -i {key_path} -o StrictHostKeyChecking=no {user}@{ip_address} 'test -s /var/secrets/pg_pw.txt && echo exists'", fail_on_error=False)
    check_condition(result is not None and "exists" in result, 0.5)

    logging.info("Checking if '/var/log/stage_5b/error.log' exists...")
    result = run_command(f"ssh -i {key_path} -o StrictHostKeyChecking=no {user}@{ip_address} 'test -f /var/log/stage_5b/error.log && echo exists'", fail_on_error=False)
    check_condition(result is not None and "exists" in result, 0.5)

    logging.info("Checking if '/var/log/stage_5b/out.log' exists...")

    result = run_command(f"ssh -i {key_path} -o StrictHostKeyChecking=no {user}@{ip_address} 'test -f /var/log/stage_5b/out.log && echo exists'", fail_on_error=False)
    check_condition(result is not None and "exists" in result, 0.5)

    logging.info("Checking if '/var/log/stage_5b/error.log' is owned by the 'hng' user...")
    result = run_command(f"ssh -i {key_path} -o StrictHostKeyChecking=no {user}@{ip_address} 'stat -c \"%U\" /var/log/stage_5b/error.log'", fail_on_error=False)
    check_condition(result is not None and "hng" in result, 0.5)

    logging.info("Checking if '/var/log/stage_5b/out.log' is owned by the 'hng' user...")
    result = run_command(f"ssh -i {key_path} -o StrictHostKeyChecking=no {user}@{ip_address} 'stat -c \"%U\" /var/log/stage_5b/out.log'", fail_on_error=False)
    check_condition(result is not None and "hng" in result, 0.5)

    # Final score calculation
    logging.info(f"Final Score: {total_score}/{max_score}")
    print(f"Final Score: {total_score}/{max_score}")

def main():
    region = os.getenv("AWS_REGION", "europe-west2")
    zone = os.getenv("GCP_ZONE", "europe-west2-b")
    project_id = "lovemeapp-1"
    instance_type = "e2-small"
    key_name = "hng.pub"
    private_key_path = "hng"
    # slack_name = 
    slack_name = sys.argv[2]
    # create_terraform_files(slack_name, project_id, region, zone, instance_type, key_name, private_key_path)
    # create_terraform_files(region, instance_type, key_name, private_key_path)

    # apply_terraform()

    logging.info("Waiting for GCP instance to be ready...")
    # sleep(10)  # Wait for the EC2 instance to be fully up
    with open("ip.json") as f:
        instance_ip = json.load(f)["public_ip"]

    logging.info(f"EC2 Instance IP: {instance_ip}")

    # create_ansible_inventory(instance_ip, private_key_path)

    # clone_repo(sys.argv[1])

    # run_ansible_playbook()

    grade_deployment(instance_ip, private_key_path, "terraform")
    logging.info(f"slack name: {slack_name}")
    destroy_choice = input("Do you want to destroy the Terraform-managed infrastructure? (y/n): ").strip().lower()
    if destroy_choice == 'y':
        destroy_terraform(slack_name)

if __name__ == "__main__":
    main()