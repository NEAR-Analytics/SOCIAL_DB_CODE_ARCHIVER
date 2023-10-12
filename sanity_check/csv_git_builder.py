import subprocess
import re
import csv
import os

def get_git_log(repo_path="."):
    cmd = ['git', 'log']
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=repo_path)
    stdout, _ = process.communicate()
    return stdout.decode()

def extract_commit_data(log):
    commits = []

    commit_pattern = re.compile(r'commit (?P<hash>[0-9a-fA-F]+)')
    update_pattern = re.compile(r'Update (?P<widget_name>[\w\.]+)(?: by (?P<author>[\w\.]+))? at (?P<time>[\w\:\-\.TZ]+)')

    lines = log.split("\n")
    for i in range(len(lines)):
        if lines[i].startswith('commit'):
            commit_hash = commit_pattern.search(lines[i]).group('hash')
            message = lines[i+4].strip() if i+4 < len(lines) else ""
            update_match = update_pattern.search(message)

            if update_match:
                widget_name = update_match.group('widget_name')
                author = update_match.group('author') or "Unknown Author"
                time = update_match.group('time')
            else:
                print(lines[i])
                widget_name = "Unknown Widget"
                author = "Unknown Author"
                time = "Unknown Time"

            commits.append([commit_hash, widget_name, author, time])

    return commits



def write_to_csv(commits, filename="commits.csv"):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Commit Hash', 'Widget Name', 'Author', 'Time'])
        writer.writerows(commits)

if __name__ == '__main__':
    repo_path = input("Enter the path to the git repository (or leave empty for current directory): ").strip() or "."
    if not os.path.exists(os.path.join(repo_path, '.git')):
        print(f"Error: No git repository found in {repo_path}")
    else:
        log = get_git_log(repo_path)
        commits = extract_commit_data(log)
        write_to_csv(commits)
        print(f"Commits written to commits.csv")
