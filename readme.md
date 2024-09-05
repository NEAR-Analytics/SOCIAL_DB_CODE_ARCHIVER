# About
This repo serves to update the [BOS-WIDGETS](https://github.com/NEAR-Analytics/BOS_WIDGETS) repo that tracks BOS development on NEAR.

## Automated Run
There are 2 automated GitHub actions that run weekly on Mondays
1. [Update BOS Widgets](https://github.com/NEAR-Analytics/SOCIAL_DB_CODE_ARCHIVER/actions/workflows/merge.yml) - The update workflow sets up a Python environment, installs dependencies, runs a script to update the widgets, and commits the changes. It runs on a scheduled basis (every Monday at 00:00) and can also be triggered manually. The workflow performs the following steps:
2. [Merge BOS Widgets](https://github.com/NEAR-Analytics/SOCIAL_DB_CODE_ARCHIVER/actions/workflows/update.yml) - The merge workflow handles merging the update branch into the master branch and creates a pull request if conflicts are detected. It runs on a schedule every Monday at 03:00 and can also be triggered manually.

## To Run Manually:
You can use dev_commit.py from this repo and have it create/update files in another repo (BOS_WIDGETS).

1. Local Setup
- Clone this repo locally
- Then clone the repo https://github.com/NEAR-Analytics/BOS_WIDGETS
- Set the export to to have it update the BOS_WIDGETS repo

```
export WIDGET_ROOT_DIR='<YOUR_LOCAL_PATH>/BOS_WIDGETS'
export SHROOM_SDK='<FLIPSIDE_API_KEY_HERE>'

# As an example it might look like
WIDGET_ROOT_DIR='/Users/username/Documents/GitHub/BOS_WIDGETS'
export SHROOM_SDK='asdfljbd89ag325ndsefdeff'
```

2. Navigate to this repo's subfolder: 
```
cd <YOUR_PATH>/SOCIAL_DB_CODE_ARCHIVER/cli_tool
```
3. Run python file - This creates an individual folder per widget at the location of WIDGET_ROOT_DIR specified in step 1
``` 
python dev_commit.py
```

4. Navigate to the BOS_WIDGET repo and push the changes. I like to checkout a new branch
```
cd <YOUR_PATH>/BOS_WIDGETS
git checkout -b <YOUR_BRANCH>
git push origin <YOUR_BRANCH>
```

5. create a PR before merging