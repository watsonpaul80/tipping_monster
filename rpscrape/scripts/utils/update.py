import subprocess

from pathlib import Path

class Update:

    def __init__(self):
        self.root_dir = Path.cwd().parent

    def available(self):
        if 'local out of date' in self.get_status().lower():
            return True
        return False

    def get_status(self):
        command = ['git', 'remote', 'show', 'origin']
        status = subprocess.check_output(command, cwd=self.root_dir)
        return status.decode('utf-8')

    def pull_latest(self):
        for command in ['git', 'fetch'], ['git', 'reset', '--hard', 'HEAD']:
            res = subprocess.run(command, cwd=self.root_dir, stdout=subprocess.DEVNULL)
            if res.returncode != 0:
                return False

        res = subprocess.run(['git', 'merge', 'origin/master'], cwd=self.root_dir, capture_output=True)
        return 'up-to-date' in res.stdout.decode('utf-8')
