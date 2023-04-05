
import os
import pandas as pd
import subprocess
from collections import defaultdict

from query_engine.client import *
import time
# Read the CSV file
import json

# create a delay within a loop:



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

# Sort data by block_timestamp

widget_names_list = set(get_widget_names()['widget_name'])
widget_names_list = [name for name in widget_names_list if name]


# Function to run git commands
def run_git_command(command, path='.', env=None):
    process = subprocess.Popen(command, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(stderr.decode())
    else:
        print(stdout.decode())

base_path = '/Users/yadkonrad/dev_dev/year2023/mar23/widget_wise/cli_tool/_widgets/'




# ad_hot, skip widgets in this list already:
skip_widgets = os.listdir(base_path)

# WIDGET_LOOP
for widget_name in widget_names_list:

    if widget_name in skip_widgets:
        continue

    df = get_widget_updates(widget_name)
    time.sleep(2)
    df = df.sort_values(by=['block_timestamp'])

    data = df.to_dict('records')
    # Organize data by widget_name
    widgets = defaultdict(list)
    for entry in data:
        widgets[entry['widget_name']].append(entry)




    # Create directories, initialize Git repositories, and commit changes
    for widget_name, widget_entries in widgets.items():


        widget_path = os.path.join(base_path, widget_name)
        if not os.path.exists(widget_path):
            os.makedirs(widget_path)
            os.chdir(widget_path)
            subprocess.run(['git', 'init'])
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


            signer_id = widget_entry['signer_id']

            if not os.path.exists(signer_id):
                os.makedirs(signer_id)
            with open(os.path.join(signer_id, 'source_code.jsx'), 'w') as f:
                if widget_entry['source_code']:
                    f.write(widget_entry['source_code'])
                else:
                    f.write("")

            with open(os.path.join(signer_id, 'commit_raw.json'), 'w') as f:
                 json.dump(widget_entry, f)

            # Stage and commit the changes
            # subprocess.run(['git', 'add', os.path.join(signer_id, 'source_code.jsx')])

            # subprocess.run(['git', 'commit', '-m', commit_message])

            run_git_command(['git', 'add', '.'], widget_dir, env=env)
            run_git_command(['git', 'commit', '-m', f'Update source_code by {signer_dir} at {timestamp}', '--date', timestamp], widget_dir, env=env)




            metadata_note = f"TxHash: {widget_entry['tx_hash']}\nActionID: {widget_entry['action_id_social']}\nBlockID: {widget_entry['block_id']}\nWidgetModules: {widget_entry['widget_modules_used']}\nWidgetURL: {widget_entry['widget_url']}"

            run_git_command(['git', 'notes', 'add', '-m', metadata_note], env=env)


    os.chdir(base_path)