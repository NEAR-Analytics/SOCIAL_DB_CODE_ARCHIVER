



```
This repo serves to update BOS widget development. You can use dev_commit.py from this repo and have it create/update files in another repo (BOS_WIDGETS).

1. Local Setup
- Clone this repo locally
- Then clone the repo https://github.com/NEAR-Analytics/BOS_WIDGETS
- Set the export to to have it update the BOS_WIDGETS repo

export WIDGET_ROOT_DIR='<YOUR_LOCAL_PATH>/BOS_WIDGETS'
export SHROOM_SDK='<FLIPSIDE_API_KEY_HERE>'

- As an example it might look like: 
WIDGET_ROOT_DIR='/Users/username/Documents/GitHub/BOS_WIDGETS'
export SHROOM_SDK='avhir30g98vdnjwr9df23esdf'

2. Navigate to this repo's subfolder: 
cd <YOUR_PATH>/SOCIAL_DB_CODE_ARCHIVER/cli_tool

3. Run python dev_commit.py
This creates an individual folder per widget at the location of WIDGET_ROOT_DIR specified in step 1

4. Navigate to the BOS_WIDGET repo and push the changes
I like to checkout a new branch
cd <YOUR_PATH>/BOS_WIDGETS
git checkout -b <YOUR_BRANCH>
git push origin <YOUR_BRANCH>

5. create a PR before merging

Old:
export WIDGET_ROOT_DIR='~/dev/_widgets/' 
^When running this locally it will create a folder in this repo and begin updating files

python get_dev_list.py
^this is an old list

```