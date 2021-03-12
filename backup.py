# crontab -e
# 0 */1 * * * cd /home/aboro/projects/sqlbackup && python backup.py >> backup_projects.log 2>&1

# V0.1: copy from sqlbackup
# V0.2: copy to the same directory structure as the original

import sys, datetime, subprocess, json, argparse

version = 'V0.2'
parser = argparse.ArgumentParser(description='store directories and files in cloud')
parser.add_argument('--no-cloud', dest='store_in_cloud', action='store_false')
parser.add_argument('--version', action='version', version=f'version: {version}')
program_arguments = parser.parse_args()

now = datetime.datetime.now()
timestamp = now.strftime('%Y-%m-%d-%H-%M')

try:
    jf = open('config.json')
    config = json.load(jf)

    backup_path = config['backup_path']
    rclone = subprocess.run(f'rclone ls --max-depth 1 {backup_path}'.split())
    if rclone.returncode != 0:
        print(f'{timestamp}: Error, could not rclone ls --max-depth 1 {backup_path}')

    items = config['items']

    for item in items:
        print(f'{timestamp}: >>> Backing up : {item} <<<<')

        rclone = subprocess.run(f'rclone copy {item} {backup_path}/{item}'.split())
        if rclone.returncode != 0:
            print(f'{timestamp}: Error, could not rclone {item}')
            continue
        print(f'{timestamp}: Backup finished')

except Exception as e:
    print(f"{timestamp}: Could not backup : {e}")
    sys.exit()
