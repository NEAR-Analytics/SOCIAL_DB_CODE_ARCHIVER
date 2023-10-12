
import os
import pandas as pd
import subprocess
from query_engine.client import *

# Read the CSV file



# df = get_all_widget()

# Sort data by block_timestamp

# Function to run git commands
def run_git_command(command, path='.', branch=None, env=None):
    if branch is not None:
        checkout_command = ['git', 'checkout', branch]
        process = subprocess.Popen(checkout_command, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            print("Error switching branches:")
            print(stderr.decode())
            return
        else:
            print("Switched to branch:")
            print(stdout.decode())

    process = subprocess.Popen(command, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print("Error executing command:")
        print(stderr.decode())
    else:
        print("Command output:")
        print(stdout.decode())

# Check if a git repository exists
def git_repo_exists(path):
    process = subprocess.Popen(['git', 'rev-parse'], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.communicate()
    return process.returncode == 0


def get_commit_message(widget_path, branch_name):
    os.chdir(widget_path)

    try:
        commit_message = subprocess.check_output(['git', 'log', '-n', '1', '--pretty=format:%s', branch_name])
        return commit_message.decode('utf-8').strip()
    except subprocess.CalledProcessError:
        return None
    finally:
        os.chdir(os.pardir)

widget_names_list = set(get_widget_names()['widget_name'])
widget_names_list = [name for name in widget_names_list if name]


failed_updates = []

WIDGETS_PATH = '/widget_wise/cli_tool/_widgets/'

# WIDGET_LOOP
for widget_name in widget_names_list:

    df = get_widget_updates(widget_name)
    df = df.sort_values(by=['block_timestamp'])

    # MAIN_LOOP
    # Iterate through each row of the dataframe
    for index, row in df.iterrows():
        widget_dir = WIDGETS_PATH + row['widget_name']
        signer_dir = row['signer_id']
        source_code = row['source_code']
        timestamp = row['block_timestamp']

        if 'metadata' in row and str(row['metadata']) != 'nan':
            committer_name = row['metadata']['github'] if row['metadata'] and 'github' in row['metadata'] else row['signer_id']
        else:
            committer_name = row['signer_id']
        committer_email = f"{committer_name}" # @example.com

        env = os.environ.copy()
        env['GIT_COMMITTER_NAME'] = committer_name
        env['GIT_COMMITTER_EMAIL'] = committer_email
        env['GIT_AUTHOR_NAME'] = committer_name
        env['GIT_AUTHOR_EMAIL'] = committer_email

        branch_name = 'branch-' + widget_dir

        # Create widget and signer directories if they do not exist
        if not os.path.exists(widget_dir):
            os.makedirs(widget_dir)

        # instead check if a branch exits, if not then create one and switch to that branch.
        if not os.path.exists(os.path.join(widget_dir, signer_dir)):
            os.makedirs(os.path.join(widget_dir, signer_dir))


        # Initialize git repository if it does not exist
        if not git_repo_exists(widget_dir):
            run_git_command(['git', 'init'], widget_dir, env=env, branch=branch_name)

        latest_commit_timestamp = get_commit_message(widget_dir, branch_name)
        print("latest_commit_timestamp")
        print(latest_commit_timestamp)

        if source_code:
            # Write the source code to a file inside the signer directory

            file_path = os.path.join(widget_dir, signer_dir, 'source_code.txt')
            with open(file_path, 'w') as f:
                f.write(source_code)
            # try:

            # except TypeError:
            #     failed_updates.append(row)
            #     print('Error writing source code to file')

            # Commit the changes
            run_git_command(['git', 'add', '.'], widget_dir, env=env, branch=branch_name)
            run_git_command(['git', 'commit', '-m', f'Update source_code by {signer_dir} at {timestamp}', '--date', timestamp], widget_dir, env=env, branch=branch_name)


            metadata_note = f"TxHash: {row['tx_hash']}\nActionID: {row['action_id_social']}\nBlockID: {row['block_id']}\nWidgetModules: {row['widget_modules_used']}\nWidgetURL: {row['widget_url']}"

            run_git_command(['git', 'notes', 'add', '-m', metadata_note], env=env, branch=branch_name)
