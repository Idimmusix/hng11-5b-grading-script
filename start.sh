#!/bin/bash

# Check if the script is run as root
# if [[ $UID != 0 ]]; then
#   echo "This script must be run as root or with sudo privileges"
#   exit 1
# fi

# Function to display help information
show_help() {
    echo "Usage: start.sh <intern-repo> <intern-boilerplate-project> <intern-slack-name>"
    echo "Instantiate and run the intern's ansible script in a remote server, then test for some specific scenarios."
    echo
    echo "Options:"
    echo "  -r, --repo [URL]                             Intern ansible repository URL"
    echo "  -b, --boilerplate [Programming Language]     Intern boilerplate project language e.g [csharp]"
    echo "  -x, --send-to-sheet [URL]                    Post to a sheet"
    echo "  -e, --email [EMAIL]                          Add the intern email address"
    echo "  -s, --slack-url [URL]                        send to slack URL"
    echo "  -h, --help                                   Display this help message"
}

if [[ -z $2 ]]; then
    echo "Usage: start.sh \":white_check_mark: <intern-repo> <intern-boilerplate-project>\""
fi

if [[ -d "ansible_test" ]]; then 
    echo "removing ansible_test directory"
    rm -rf ansible_test;
fi

git_repo=$1
boilerplate=$2
slack_name=$3

setup_dependencies() {
    echo "configuring your server"
    echo "checking..."
}

#clone git repo
clone_git() {
    echo "$slack_name's git repo: $git_repo"
    git clone $git_repo ansible_test
}

get_boilerplate() {
    case "$boilerplate" in
        Python|python)
            echo "https://github.com/hngprojects/hng_boilerplate_python_fastapi_web"
            ;;
        NestJs|nestjs)
            echo "nest"
            ;;
        NextJs|nextjs)
            echo "next"
            ;;
        PHP|php)
            echo "php"
            ;;
        *)
            echo "Invalid boilerplate language"
            exit 1
    esac
}
setup_terraform() {
    echo "installing and setting up terraform"
    terraform init
}
setup_ansible() {
    echo "installing and setting up ansible"
}

create_gcp_server() {
    echo "setting up the server"
    terraform apply --auto-approve
}

run_tests() {
    echo "running tests"
}

shutdown_gcp_server() {
    echo "shutting down the server"
    terraform destroy --auto-approve
}
setup_dependencies
clone_git
get_boilerplate
setup_ansible
setup_terraform
create_gcp_server
run_tests

# Main execution
# case "$1" in
#     -p|--port)
#         get_ports "$2"
#         ;;
#     -d|--docker)
#         get_docker_info "$2"
#         ;;
#     -n|--nginx)
#         get_nginx_info "$2"
#         ;;
#     -u|--users)
#         get_user_info "$2"
#         ;;
#     -t|--time)
#         shift
#         get_time_range_activities "$@"
#         ;;
#     -h|--help)
#         show_help
#         ;;
#     *)
#         echo "Invalid option. Use -h or --help for usage information."
#         exit 1
#         ;;
# esac