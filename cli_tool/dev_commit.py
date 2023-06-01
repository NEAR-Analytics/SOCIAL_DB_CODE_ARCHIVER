
import os
import pandas as pd
import subprocess
from collections import defaultdict

from query_engine.client import *
import time
# Read the CSV file
import json

# create a delay within a loop:


base_path = os.environ['WIDGET_ROOT_DIR']

# generate code to load dev_profiles from file:
with open("dev_profiles.json") as file:
  dev_profiles = json.load(file)


def get_github_id(signed_id):
    if signed_id in dev_profiles:
        profile_data_raw = dev_profiles[signed_id]
        if len(profile_data_raw):
            profile_data = json.loads(dev_profiles[signed_id][0]['profile_data'])
            if 'github' in profile_data:
                return profile_data['github']

    return signed_id

# df = get_all_widget()


# Function to run git commands
def run_git_command(command, path='.', env=None):
    process = subprocess.Popen(command, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(stderr.decode())
    else:
        print(stdout.decode())

# Sort data by block_timestamp

widget_names_list = set(get_widget_names()['widget_name'])
widget_names_list = [name for name in widget_names_list if name]



def find_files(root_dir, file_name):
    file_paths = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for file in filenames:
            if file == file_name:
                file_path = os.path.join(dirpath, file)
                file_paths.append(file_path)

    return file_paths

def get_checkpoints(root_directory):
    target_file_name = 'commit_raw.json'

    checkpoints = {}

    files_found = find_files(root_directory, target_file_name)

    if files_found:
        print(f"Found {len(files_found)} {target_file_name} files:")
        for file_path in files_found:
            # open json file
            with open(file_path) as json_file:
                data = json.load(json_file)
                # print(data)
                # print(data['widget_name'])
                # print(data['source_code'])
                # print(data['block_timestamp'])
                # print(data['signer_id'])
                # print(data['block_height'])
                # print(data['block_hash'])
                # print(
            checkpoints[data['widget_name']] = data
            print(file_path)
    else:
        print(f"No {target_file_name} files found in {root_directory}")
    return checkpoints

# ad_hot, skip widgets in this list already:
existing_widgets = get_checkpoints(base_path)

failed_widgets = []

# WIDGET_LOOP

for widget_name in widget_names_list:

    # put this following if else inside a try except block
    try:
        if widget_name in existing_widgets:
            print(f"Updating Index {widget_name}")

            df = get_widget_updates(widget_name, existing_widgets[widget_name]['block_timestamp'])
        else:
            print(f"Creating Index {widget_name}")
            df = get_widget_updates(widget_name)
    except:
        # if there is an error, skip this widget and add it failed widgets list
        failed_widgets.append(widget_name)
        continue






    time.sleep(2)
    df = df.sort_values(by=['block_timestamp'])

    data = df.to_dict('records')
    # Organize data by widget_name
    widgets = defaultdict(list)
    dev_widgets = defaultdict(list)
    for entry in data:
        widgets[entry['widget_name']].append(entry)
        dev_widgets[entry['signer_id']].append(entry)




    # Create directories, initialize Git repositories, and commit changes
    for near_dev, widget_entries in dev_widgets.items():


        widget_path = os.path.join(base_path, near_dev)

        if not os.path.exists(widget_path):
            os.makedirs(widget_path)
            os.chdir(widget_path)

        else:
            os.chdir(widget_path)

        # Create sub-directories for each widget, store source_code, and commit changes
        for widget_entry in widget_entries:

            widget_dir = widget_path
            signer_dir = widget_entry['signer_id']
            source_code = widget_entry['source_code']
            timestamp = widget_entry['block_timestamp']


            committer_name = get_github_id(signer_dir)

            committer_email = f"{committer_name}" # @example.com

            env = os.environ.copy()
            env['GIT_COMMITTER_NAME'] = committer_name
            env['GIT_COMMITTER_EMAIL'] = committer_email


            if committer_name:

                env['GIT_AUTHOR_NAME'] = committer_name
                env['GIT_AUTHOR_EMAIL'] = committer_name
            else:
                env['GIT_AUTHOR_NAME'] = committer_name
                env['GIT_AUTHOR_EMAIL'] = committer_email


            widget_name = widget_entry['widget_name']



            if widget_name in existing_widgets:
                print(f"checking updates for {widget_name} by {signer_dir} at {timestamp}")

                current_commit_date = datetime.strptime(widget_entry['block_timestamp'], "%Y-%m-%d %H:%M:%S.%f")

                try:
                    with open(os.path.join(widget_name, 'commit_raw.json'), 'r') as f:
                        # read the json file
                        data = json.load(f)
                except:
                    failed_widgets.append(widget_name)
                    continue
                # get the latest commit date
                latest_commit_date = datetime.strptime(data['block_timestamp'], "%Y-%m-%d %H:%M:%S.%f")
                # Compare the dates
                if current_commit_date > latest_commit_date:
                    print(f"updating {widget_name}")

                    with open(os.path.join(widget_name, 'commit_raw.json'), 'w') as f:
                        json.dump(widget_entry, f)
                else:
                    print("No updates found")


            else:
                print(f"Creating {widget_name} by {signer_dir} at {timestamp}")
                # Create sub-directory for each widget
                if not os.path.exists(widget_name):
                    os.makedirs(widget_name)
                with open(os.path.join(widget_name, 'source_code.jsx'), 'w') as f:
                    if widget_entry['source_code']:
                        f.write(widget_entry['source_code'])
                    else:
                        f.write("")
                with open(os.path.join(widget_name, 'commit_raw.json'), 'w') as f:
                    json.dump(widget_entry, f)

            # Stage and commit the changes
            # subprocess.run(['git', 'add', os.path.join(signer_id, 'source_code.jsx')])

            # subprocess.run(['git', 'commit', '-m', commit_message])

            run_git_command(['git', 'add', '.'], widget_dir, env=env)
            run_git_command(['git', 'commit', '-m', f'Update {widget_name} by {signer_dir} at {timestamp}', '--date', timestamp], widget_dir, env=env)


            # metadata_note = f"TxHash: {widget_entry['tx_hash']}\nActionID: {widget_entry['action_id_social']}\nBlockID: {widget_entry['block_id']}\nWidgetModules: {widget_entry['widget_modules_used']}\nWidgetURL: {widget_entry['widget_url']}"

            # run_git_command(['git', 'notes', 'add', '-m', metadata_note], env=env)


    os.chdir(base_path)