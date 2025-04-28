# crontab -e
# 0 */1 * * * cd /home/aboro/projects/sqlbackup && python backup.py >> backup_projects.log 2>&1

# V0.1: copy from sqlbackup
# V0.2: copy to the same directory structure as the original
# V0.3: backup dirs, single files and wildcard-files
# V0.4: expanded glob so that wildcard can be used in the middle of a path
# V0.5: expanded with local backup (no rclone)
# V0.6: os.path.isdir does not raise exception

import sys, datetime, subprocess, json, argparse, os, glob, shutil

version = 'V0.6'
parser = argparse.ArgumentParser(description='store directories and files in cloud')
parser.add_argument('--no-cloud', dest='store_in_cloud', action='store_false')
parser.add_argument('--version', action='version', version=f'version: {version}')
program_arguments = parser.parse_args()

local_backup = False

def main():
    try:
        jf = open('config.json')
        config = json.load(jf)

        backup_path = config['backup_path']
        if not check_backup_path(backup_path):
            print("Could not determine backup path, terminating...")
            exit(-1)
        items = config['items']
        for item in items:
            print(f'{timestamp()}: >>> Backing up : {item} <<<<')

            glob_list = glob.glob(item)
            for glob_item in glob_list:
                if os.path.isdir(glob_item):
                    copy_dir(glob_item, backup_path)
                elif os.path.isfile(glob_item):
                    copy_file(glob_item, backup_path)

        print(f'{timestamp()}: Backup finished')
    except Exception as e:
        print(f"{timestamp()}: Could not backup : {e}")
        sys.exit()


def check_backup_path(backup_path):
    global local_backup
    if os.path.isdir(backup_path):
        local_backup = True
        print("Local backup")
        return True
    try:
        rclone = subprocess.run(f'rclone ls --max-depth 1 {backup_path}'.split())
        if rclone.returncode == 0:
            print("Remote backup, use rclone")
            return True
        else:
            print(f'{timestamp()}: Error, could not rclone ls --max-depth 1 {backup_path}')
            return False
    except Exception:
        return False


def copy_file(file, backup_path):
    if local_backup:
        dest_file = os.path.join(backup_path, file[3:])
        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
        shutil.copy2(file, dest_file)
    else:
        dir_name = os.path.dirname(file)
        rclone = subprocess.run(f'rclone copy {file} {backup_path}/{dir_name}'.split())
        if rclone.returncode == 0:
            print(f'{timestamp()}: rclone success: {file}')
        else:
            print(f'{timestamp()}: Error, could not rclone: {file}')


def copy_dir(path, backup_path):
    if local_backup:
        shutil.copytree(path, backup_path)
    else:
        rclone = subprocess.run(f'rclone copy {path} {backup_path}/{path}'.split())
        if rclone.returncode == 0:
            print(f'{timestamp()}: rclone success: {path}')
        else:
            print(f'{timestamp()}: Error, could not rclone: {path}')


def timestamp():
    now = datetime.datetime.now()
    return  now.strftime('%Y-%m-%d-%H-%M')


main()