#!/bin/bash

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

if [[ -d "testing" ]]; then 
    echo "removing testing directory"
    rm -rf testing;
fi

git_repo=$1
# boilerplate=$2
slack_name=$2
score=0
user=ddd

# setup_dependencies() {
#     echo "configuring your server"
#     echo "checking..."
# }

#clone git repo
clone_git() {
    echo "$slack_name's git repo: $1"
    git clone $1 testing

    if [[ -f "testing/ansible.cfg" ]]; then 
        echo "copying your ansible.cfg"
        cp testing/ansible.cfg ~/.ansible.cfg
    fi
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
    terraform apply --auto-approve -var="slack_name=$1"
}

echo "running tests"


user_exists(){ 
    id "$1" &>/dev/null; 
} # silent, it just sets the exit code

run_tests() {
    python3 script.py $1 $2
}
#echo "score: $score"
shutdown_gcp_server() {
    echo "shutting down the server"
    terraform destroy --auto-approve
}
# setup_dependencies
clone_git $git_repo
# get_boilerplate
# setup_ansible
# setup_terraform
create_gcp_server $slack_name
run_tests $git_repo $slack_name
