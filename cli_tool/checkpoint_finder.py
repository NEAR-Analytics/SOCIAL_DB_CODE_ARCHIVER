import os
# get environment variables from os
env_widgets_root_directory = os.environ['WIDGET_ROOT_DIR']

def find_files(root_dir, file_name):
    file_paths = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for file in filenames:
            if file == file_name:
                file_path = os.path.join(dirpath, file)
                file_paths.append(file_path)

    return file_paths

def main():
    root_directory = env_widgets_root_directory # Change this to the desired starting directory
    target_file_name = 'commit_raw.json'

    checkpoints = []

    files_found = find_files(root_directory, target_file_name)

    if files_found:
        print(f"Found {len(files_found)} {target_file_name} files:")
        for file_path in files_found:
            checkpoints.append(file_path)
            print(file_path)
    else:
        print(f"No {target_file_name} files found in {root_directory}")
    return checkpoints

def update_query():
    # get latest updates for the widget from SocialDB

    # update the widget's source code

    # git commit-update.

    return

if __name__ == '__main__':
    checkpoints = main()
