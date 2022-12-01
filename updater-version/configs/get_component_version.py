#!/usr/bin/env python3.8

from kubernetes import client, config
import sys
import re
from git import Repo
from git import Git
import shutil
import os

try:
    ns = sys.argv[1]
except IndexError:
    print(f"Usage: {sys.argv[0]} <namespace>")
    sys.exit(1)

result_file = f"{ns}.txt"
repo_url = "<you_git_repo>"
git_clone_dir = "/tmp/devops-components-version"

if ns == "dev" or ns == "test":
    config.load_kube_config(config_file='./config_dev')
elif ns == "prod":
    config.load_kube_config(config_file='./config_prod')

v1 = client.AppsV1Api()
deployment = v1.list_namespaced_deployment(ns)

def get_component_and_version():
    print(f"[+] Get component version from namespace {ns}...")
    file = open(result_file, 'w')
    char_for_delete = "[']"
    for item in deployment.items:
        image = str(re.findall(r'<you_repo>/project>.*\w', str(item.spec)))
        for char in char_for_delete:
            image = image.replace(char, "")
        if image == "":
            continue
        elif (",") in image:
            full_app = image.split(",")[0]
            full_app = full_app.split("/")[2]
            file.write(full_app + '\n')
        else:
            full_app = image.split("/")[2]
            file.write(full_app+'\n')
    file.close()

def clone_repository(repo, dir):
    print(f"[+] Cloning repository {repo} to {dir}...")
    git_dir_is_exist = os.path.exists(dir)
    if not git_dir_is_exist:
        os.makedirs(dir)
    shutil.rmtree(dir)
    Repo.clone_from(repo, dir, env=dict(GIT_SSH_COMMAND="ssh -i ./private_ssh_key -o StrictHostKeyChecking=no"))
    
get_component_and_version()
clone_repository(repo_url, git_clone_dir)
shutil.copy(result_file, git_clone_dir)
print(f"[+] Push changes to {repo_url}...")
repo = Repo(git_clone_dir)
with repo.git.custom_environment(GIT_SSH_COMMAND="ssh -i /opt/private_ssh_key"):
    repo.git.add(update=True)
    repo.index.commit("Update devops-component-version")
    repo.git.push('origin', 'master')
print("[+] Successfully...")
