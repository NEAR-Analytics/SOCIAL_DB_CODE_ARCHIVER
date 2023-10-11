
# generate code to load dev_profiles from file:
with open("dev_profiles.json") as file:
  dev_profiles = json.load(file)


def get_github_id(signed_id):
    if signed_id in dev_profiles:
        profile_data_raw = dev_profiles[signed_id]
        if len(profile_data_raw):
            profile_data = dev_profiles[signed_id]['profile_data']
            if 'github' in profile_data:
                return profile_data['github']

    return signed_id
