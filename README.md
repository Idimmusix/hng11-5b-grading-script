This is a simple terraform project used to grade stage 5b of the HNG11 Task.
The task can be seen in [Ansible task](https://docs.google.com/document/d/1Btr9AE-vg1sLXqMaZ1u8dgL3jSLMPsax7vCa79Fc9L4/edit#heading=h.88s5jdp56k6p)

To grade, 
Run bash start.sh <intern-repo> <intern-boilerplate-project> <intern-slack-name>
The script will do the follwoing
1. Setup gcloud cli, install terraform and ansible
2. clone the <intern-repo>
3. configure .tfvars with intern slack name
4. terraform apply - which will create the server and run the intern ansible script in it.
5. check the assertions to determine the score
6. post the score on terminal
 - To post the score to the google sheet, use -x <intern>
 - To send the score to the intern on slack, use -s <slack-URL> -u <intern-email-address>

