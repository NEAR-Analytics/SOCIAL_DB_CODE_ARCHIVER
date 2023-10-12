import os

def get_subdirectories(directory_path):
    """Fetch all the immediate subdirectories of a given directory."""
    return [d for d in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, d))]

def count_widgets_for_dev(directory_path):
    """Count the unique widgets (subdirectories) inside a developer's directory."""
    return len(get_subdirectories(directory_path))

if __name__ == "__main__":
    root_directory = input("Enter the root directory path: ")

    if not os.path.exists(root_directory):
        print(f"Error: {root_directory} does not exist!")
        exit()

    # 1. Fetch all directories inside the given directory
    developers_dirs = get_subdirectories(root_directory)

    # 2. Count the unique directories (developer's directories)
    unique_developer_count = len(developers_dirs)
    print(f"Number of developers: {unique_developer_count}")

    # 3. For each developer directory, count the unique widgets and store in a dict
    widget_counts = {}
    for dev_dir in developers_dirs:
        widget_count = count_widgets_for_dev(os.path.join(root_directory, dev_dir))
        widget_counts[dev_dir] = widget_count

    for dev, count in widget_counts.items():
        print(f"Developer {dev} has created {count} unique widgets.")
