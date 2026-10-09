## TP 03 : Ansible


### 3-1 Document your inventory and base commands.

```yaml
all: #root group, every host belongs to it
 vars:
   ansible_user: admin #Used for ansible to log in via default user admin
   ansible_ssh_private_key_file: ~/key/id_rsa #Used to communicate via SSH
 children:
   prod:
     hosts: ilies.nasr.takima.school

```



### 3-2 Document your playbook.
```yaml
- hosts: all
  gather_facts: true
  become: true

  tasks:
    # Install prerequisites for Docker
    - name: Install required packages
      apt:
        name:
          - apt-transport-https
          - ca-certificates
          - curl
          - gnupg
          - lsb-release
          - python3-venv
        state: latest
        update_cache: yes

    # Add Docker's official GPG key
    - name: Add Docker GPG key
      apt_key:
        url: https://download.docker.com/linux/debian/gpg
        state: present

    # Set up the Docker stable repository
    - name: Add Docker APT repository
      apt_repository:
        repo: "deb [arch=amd64] https://download.docker.com/linux/debian {{ ansible_facts['distribution_release'] }} stable"
        state: present
        update_cache: yes

    # Install Docker
    - name: Install Docker
      apt:
        name: docker-ce
        state: present

    # Install Python3 and pip3
    - name: Install Python3 and pip3
      apt:
        name:
          - python3
          - python3-pip
        state: present

    # Create a virtual environment for Python packages
    - name: Create a virtual environment for Docker SDK
      command: python3 -m venv /opt/docker_venv
      args:
        creates: /opt/docker_venv  # Only runs if this directory doesn't exist

    # Install Docker SDK for Python in the virtual environment
    - name: Install Docker SDK for Python in virtual environment
      command: /opt/docker_venv/bin/pip install docker

    # Ensure Docker is running
    - name: Make sure Docker is running
      service:
        name: docker
        state: started
      tags: docker
```
### 3-3 Document your docker_container tasks configuration.



### Is it really safe to deploy automatically every new image on the hub? Explain. WHat can I do to make it more secure?


