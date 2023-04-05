import requests
import subprocess
import json
import os

import time


def is_git_repo(path):
    try:
        # subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], check=True, capture_output=True, cwd=path)
        subprocess.check_call(["git", "rev-parse", "--is-inside-work-tree"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=path)

        return True
    except subprocess.CalledProcessError:
        return False

def has_remote_url(path):
    try:
        # result = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True, cwd=path)
        result = subprocess.check_output(["git", "remote", "get-url", "origin"], stderr=subprocess.DEVNULL, text=True, cwd=path)

        return result.strip() != ""
    except subprocess.CalledProcessError:
        return False

def push_commits(path):
    try:
        subprocess.check_call(["git", "push", "-u", "origin", "master"], cwd=path)
        print("Commits pushed.")
    except subprocess.CalledProcessError as e:
        print(f"Error pushing commits: {e}")


def push_git_repo(path, subdir, access_token):
    if is_git_repo(path):
        if has_remote_url(path):
            push_commits(path)
        else:
            repo_url = create_github_repo(access_token, subdir)
            repo_url = "git@github.com:" + repo_url.split('git://github.com/')[1]
            print(f"Repository created: {repo_url}")
            subprocess.check_call(["git", "remote", "add", "origin", repo_url], cwd=path)
            push_commits(path)
    else:
        print("not a repo")
        # it's not a git repo




def create_github_repo(access_token, repo_name):
    # The data to send in the request body
    data = {
        "name": repo_name,
        "description": "widgets from social_db smart_contract",
        "private": False,
        "has_issues": True,
        "has_projects": True,
        "has_wiki": False
    }

    # The headers to include in the request
    headers = {
        "Authorization": f"Token {access_token}",
        "Accept": "application/vnd.github+json"
    }

    # Make the request
    response = requests.post("https://api.github.com/orgs/NEAR-WIDGET-DEPOT/repos", json=data, headers=headers)
    # Check if the request was successful
    if response.status_code == 201:
        # The repository was successfully created
        repo_url = response.json()["git_url"]
        return repo_url
    else:
        # There was an error
        raise Exception(f"Error creating repository: {response.text}")




def get_org_repos(org_name):
    url = f"https://api.github.com/orgs/{org_name}/repos"
    params = {"per_page": 100} # Set the number of repositories to retrieve per page
    headers = {
        "Authorization": f"Token {access_token}",
        "Accept": "application/vnd.github+json"
    }
    repositories = []

    while url:

        response = requests.get(url, headers=headers, params=params)
        time.sleep(4)
        if response.status_code == 200:
            repos_page = response.json()
            repositories += repos_page

            # Check if there are more pages to retrieve
            if "Link" in response.headers:
                links = response.headers["Link"].split(", ")
                for link in links:
                    if "rel=\"next\"" in link:
                        url = link[link.index("<")+1:link.index(">")]
                        break
                else:
                    url = None
            else:
                url = None
        else:
            print(f"Failed to get repositories: {response.status_code}")
            return []

    return [repo["name"] for repo in repositories]

# Your GitHub access token
access_token = "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"

# The name of the repository you want to create


root_dir = "/Users/yadkonrad/dev_dev/year2023/mar23/widget_wise/cli_tool/_widgets/"

org_name = "NEAR-WIDGET-DEPOT" # Replace with your organization name
repositories = get_org_repos(org_name)

# load a json file for the repos that have already been created:
with open('existing_repos.json', 'r') as f:
    repositories = json.load(f)
repositories = [repo.strip() for repo in repositories]

try:
    for subdir in list(reversed(os.listdir(root_dir))):
        subdir_path = os.path.join(root_dir, subdir)
        if os.path.isdir(subdir_path):
            print(subdir)
            if subdir in repositories:
                print("repo already exists")
                continue
            #repo_url = create_github_repo(access_token, subdir)
            push_git_repo(subdir_path, subdir, access_token)
            time.sleep(25)
except Exception as e:
    print(e)


