import os
import pandas as pd
import subprocess
from collections import defaultdict
import json

from query_engine.client import *
import time
# Read the CSV file


# create a delay within a loop:


dev_list = get_list_of_all_devs()
dev_profiles = {}


for dev in dev_list:
    time.sleep(1)
    try:
        dev_profile = get_dev_info(dev)
        dev_profiles[dev] = dev_profile.to_dict('records')
    except Exception as e:
        print(f"Error getting profile for {dev}: {e}")
# save json to text json file:

# open a file in write mode
with open("dev_profiles.json", "w") as f:
    # write the dictionary to the file in JSON format
    json.dump(dev_profiles, f)
# df = get_all_widget()