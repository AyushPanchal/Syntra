import os
from datetime import datetime

src_path = 'src'

for root, dirs, files in os.walk(src_path):
    for file in files:
        file_path = os.path.join(root, file)
        size = os.path.getsize(file_path)
        modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        print(f"File: {file_path}")