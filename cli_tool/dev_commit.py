# imports
import os
import pandas as pd
import subprocess
import json
import uuid
from datetime import datetime
from collections import defaultdict

from query_engine.client import *

# Constants and Initial Setup:

COMMIT_RAW_FILENAME = 'commit_raw.json'
SOURCE_CODE_FILENAME = 'source_code.jsx'

base_path = os.environ.get('WIDGET_ROOT_DIR', './default_directory')  # Use a default directory if environment variable is not set

# Utility Functions:

def run_git_command(command, path='.', env=None):
    process = subprocess.Popen(command, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(stderr.decode())
    else:
        print(stdout.decode())


def commit_parse_date(date_string):
    formats = ['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S.%fZ']
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            pass
    raise ValueError(f'time data {date_string} does not match any of the formats')


def find_files(root_dir, file_name):
    return [os.path.join(dirpath, file) for dirpath, _, filenames in os.walk(root_dir) for file in filenames if file == file_name]


def get_checkpoints(root_directory):
    files_found = find_files(root_directory, COMMIT_RAW_FILENAME)

    checkpoints = {}
    if files_found:
        print(f"Found {len(files_found)} {COMMIT_RAW_FILENAME} files:")
        for file_path in files_found:
            with open(file_path) as json_file:
                data = json.load(json_file)
            checkpoints[data['widget_name']] = data
            print(file_path)
    else:
        print(f"No {COMMIT_RAW_FILENAME} files found in {root_directory}")

    return checkpoints



# Main Script:
existing_widgets = get_checkpoints(base_path)
failed_widgets = []

snowflake_data = get_widget_names()
widget_names_list = set(row['widget_name'] for row in snowflake_data)

for widget_name in widget_names_list:
    widget_name = str(widget_name)
    try:
        if widget_name in existing_widgets:
            print(f"Updating Index {widget_name}")
            df_arr = get_widget_updates(widget_name, existing_widgets[widget_name]['block_timestamp'])
        else:
            print(f"Creating Index {widget_name}")
            df_arr = get_widget_updates(widget_name)

        df = pd.DataFrame(df_arr).sort_values(by=['block_timestamp'])
        widget_data = df.to_dict('records')

        dev_widgets = defaultdict(list)
        for entry in widget_data:
            dev_widgets[entry['signer_id']].append(entry)

        for near_dev, widget_entries in dev_widgets.items():
            widget_path = os.path.join(base_path, near_dev)
            os.makedirs(widget_path, exist_ok=True)

            # Ensure it's a git repository
            if not os.path.exists(os.path.join(widget_path, '.git')):
                run_git_command(['git', 'init'], widget_path)

            for widget_entry in widget_entries:
                signer_dir = widget_entry['signer_id']
                source_code = widget_entry.get('source_code') or ''
                timestamp = widget_entry['block_timestamp']
                current_widget_name = widget_entry['widget_name'] or f"{signer_dir}_{uuid.uuid4()}"

                env = os.environ.copy()
                env['GIT_COMMITTER_NAME'] = signer_dir
                env['GIT_COMMITTER_EMAIL'] = signer_dir

                widget_folder = os.path.join(widget_path, current_widget_name)
                os.makedirs(widget_folder, exist_ok=True)

                # Check for actual changes before writing & committing
                has_changes = False
                source_code_file = os.path.join(widget_folder, SOURCE_CODE_FILENAME)
                if not os.path.exists(source_code_file) or open(source_code_file).read() != source_code:
                    with open(source_code_file, 'w') as f:
                        f.write(source_code)
                    has_changes = True

                widget_details_file = os.path.join(widget_folder, COMMIT_RAW_FILENAME)
                if not os.path.exists(widget_details_file) or json.load(open(widget_details_file)) != widget_entry:
                    with open(widget_details_file, 'w') as f:
                        json.dump(widget_entry, f)
                    has_changes = True

                if has_changes:
                    run_git_command(['git', 'add', '.'], widget_folder, env=env)
                    run_git_command(['git', 'commit', '-m', f'Update {current_widget_name} by {signer_dir} at {timestamp}', '--date', timestamp], widget_folder, env=env)

    except Exception as e:
        print(f"Error processing {widget_name}: {e}")
        failed_widgets.append(widget_name)

print(f"Failed widgets: {failed_widgets}")

