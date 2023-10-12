import os
import subprocess
import shutil

def run_git_command(command, path, env=None):
    """Run a git command in a specified directory."""
    return subprocess.check_output(command, cwd=path, env=env, text=True, stderr=subprocess.STDOUT)

def integrate_submodule_commits(base_path, main_repo_path):
    """Integrate commits from submodules into the main repository using patches."""

    for root, dirs, files in os.walk(base_path):
        if '.git' in dirs:
            print(f"Integrating submodule at {root} into main repo...")

            # Create a patch for the submodule
            patch_file_path = os.path.join(root, "changes.patch")
            try:
                run_git_command(['git', 'format-patch', '--stdout', 'origin/master', '--root'], root, env=None)
            except subprocess.CalledProcessError:
                # This might fail if there's no "origin/master", in which case, let's try without specifying a branch.
                run_git_command(['git', 'format-patch', '--stdout', '--root', '-o', patch_file_path], root, env=None)

            # Apply the patch to the main repo
            try:
                run_git_command(['git', 'apply', '--check', patch_file_path], main_repo_path)
                run_git_command(['git', 'am', '--3way', patch_file_path], main_repo_path)
            except subprocess.CalledProcessError as e:
                print(f"Failed to apply patch from {root}. Error: {e}")
                continue

            # Remove the submodule directory's .git
            shutil.rmtree(os.path.join(root, '.git'))

            # Delete the patch file
            os.remove(patch_file_path)

            # Exclude the current .git directory from being traversed again
            dirs.remove('.git')

base_path = '"/PATH/"'  # Change this to your directory path
main_repo_path = '"/PATH/"'  # Change this to your main repository path
integrate_submodule_commits(base_path, main_repo_path)
