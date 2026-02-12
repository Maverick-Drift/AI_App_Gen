"""Open a list of local files from JSON stdin.

stdin format:
{
  "files": ["/path/a.txt", "/path/b.png"],
  "dry_run": true
}
"""

import json
import os
import platform
import subprocess
import sys


def open_file(path: str):
    system = platform.system().lower()
    if system == 'windows':
        os.startfile(path)  # type: ignore[attr-defined]
    elif system == 'darwin':
        subprocess.run(['open', path], check=False)
    else:
        subprocess.run(['xdg-open', path], check=False)


payload = json.loads(sys.stdin.read() or '{}')
files = payload.get('files', [])
dry_run = payload.get('dry_run', True)

opened = []
for file_path in files:
    if dry_run:
        opened.append({'file': file_path, 'status': 'dry_run'})
        continue
    open_file(file_path)
    opened.append({'file': file_path, 'status': 'opened'})

print(json.dumps({'processed': len(opened), 'results': opened}))
