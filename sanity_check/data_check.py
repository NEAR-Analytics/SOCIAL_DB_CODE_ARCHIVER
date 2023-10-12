import pandas as pd

# Load the CSV into a DataFrame
commits_df = pd.read_csv('commit_messages_fromated.csv')

# Count unique authors
unique_authors = commits_df['NEAR_DEV'].nunique()
print(f"Number of unique authors: {unique_authors}")

# Convert the 'Time' column to datetime format using mixed format option and extract the date part
commits_df['Date'] = pd.to_datetime(commits_df['TX_TIME'], format='mixed').apply(lambda x: x.date())

# Group by date and count unique authors for each day
author_activity_per_day = commits_df.groupby('Date')['NEAR_DEV'].nunique()
print("\nUnique author activity day by day:")
print(author_activity_per_day)

# save author_activity_per_day as csv
author_activity_per_day.to_csv('author_activity_per_day.csv')