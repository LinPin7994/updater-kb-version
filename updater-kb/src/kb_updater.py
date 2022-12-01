from atlassian import Confluence
import yaml
from git import Repo
from git import Git
import shutil
import os
import urllib3
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings()

kb_url = "<you_kb_url>"
config_file = "/opt/auto_jira_update.yaml"
page_id = "<you_page_id>"

data = {"dev": {}, "test": {}, "prod": {}}
lose_app = []
repo_url = "<git_url_with_components_version>"
git_clone_dir = "/tmp/devops-components-version"

def get_credentials(config):
    with open (config, 'r', encoding="utf-8") as file:
        config_yaml = yaml.safe_load(file)
        kb_login = config_yaml["jira"]["login"]
        kb_password = config_yaml["jira"]["password"]
    return kb_login, kb_password

def get_new_page_id(page_id, kb):
    new_page_id = kb.get_page_by_id(page_id, expand=None, status=None, version=None)
    new_page_id = int(new_page_id["version"]["number"]) + 1
    return new_page_id

def get_repo_info(repo_url, repo_clone_dir):
    print(f"[INFO] Cloning repository {repo_url} into {repo_clone_dir}...")
    clone_dir_exist = os.path.exists(repo_clone_dir)
    if not clone_dir_exist:
        os.makedirs(repo_clone_dir)
    shutil.rmtree(repo_clone_dir)
    Repo.clone_from(repo_url, repo_clone_dir, env=dict(GIT_SSH_COMMAND="ssh -i /opt/private_ssh_key -o StrictHostKeyChecking=no"))
    for file in data.keys():
        file_path = repo_clone_dir + "/" + file + ".txt"
        with open (file_path, 'r', encoding="utf-8") as f:
            for item in f:
                app_name = item.split(":")[0]
                app_version = item.split(":")[1]
                data[file][app_name] = app_version

    return data

def post_content(data, new_pade_id, page_id, kb):
    table_body = ""
    table_body += """<table class="wrapped relative-table" style="width: 70%;"><colgroup><col style="width: 70%;"/><col style="width: 30%;"/></colgroup><tbody>"""
    table_body += "<tr><th>Component</th>"

    for ns in data.keys():
        table_body += f"<th>{ns}</th>"
    table_body += "</tr>"

    for app in sorted(data["dev"]):
        table_body += f"<tr><td>{app}</td><td>{data['dev'][app]}</td>"
        try:
            if data['dev'][app] != data["test"][app]:
                table_body += f"<td>{data['test'][app]}</td>"
            else:
                table_body += f"<td>{data['test'][app]}</td>"
        except KeyError as e:
            table_body += "<td>null</td>"
        try:
            if data['dev'][app] != data["prod"][app]:
                table_body += f"<td>{data['prod'][app]}</td>"
            else:
                table_body += f"<td>{data['prod'][app]}</td>"
        except KeyError as e:
            table_body += "<td>null</td>"
        table_body += "</tr>"
    
    table_body += """</tbody></table>"""
    table_body += """<p class="auto-cursor-target"><br /></p>"""
    kb.update_page(page_id, title="Installed Componet version", body=table_body, parent_id=None, type='page', representation='storage', minor_edit=False)


def main():
    kb_login = get_credentials(config_file)[0]
    kb_password = get_credentials(config_file)[1]
    kb = Confluence(url=kb_url, username=kb_login, password=kb_password, verify_ssl=False)
    data = get_repo_info(repo_url, git_clone_dir)
    new_page_id = get_new_page_id(page_id, kb)
    post_content(data, new_page_id, page_id, kb)
    print("[INFO] Update success.")
    
if __name__ == "__main__":
    main()