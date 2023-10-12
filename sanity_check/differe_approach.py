import subprocess
import re
import csv

# Step 1: Extract Commit Messages
repo_path = '/PATH/june23/NEAR_SOCIAL_DB_WIDGETS'  # Replace with the path to your repo
command = ['git', '-C', repo_path, 'log', '--pretty=format:%s']
output = subprocess.check_output(command, text=True)
commit_messages = output.splitlines()

# Step 2: Filter Messages
pattern = r'^Update .+ by .+ at .+$'
filtered_messages = [msg for msg in commit_messages if re.match(pattern, msg)]

# Step 3: Save to CSV
csv_file = 'commit_messages.csv'
with open(csv_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Commit Message'])
    for msg in filtered_messages:
        writer.writerow([msg])



input_csv = 'commit_messages.csv'  # Path to your input CSV file
output_csv = 'commit_messages_fromated.csv'  # Path to the desired output CSV file


with open(input_csv, 'r') as infile, open(output_csv, 'w', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    # Write headers to the output CSV
    writer.writerow(['WIDGET_NAME', 'NEAR_DEV', 'TX_TIME'])

    # Skip header in the input CSV
    next(reader)

    for row in reader:
        try:
            message = row[0]

            # Split the message into parts
            parts = message.split(' by ')
            widget_name = parts[0].split(' ')[1]
            near_dev, tx_time = parts[1].split(' at ')

            # Write the split data to the output CSV
            writer.writerow([widget_name, near_dev, tx_time])
        except Exception as e:
            print(f"Error processing row {row}: {e}")