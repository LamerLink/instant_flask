import os
import time
from typing import Union


PARENT_DIR = r'ph_for_parent_dir'
SERVE_DIR = os.path.join(PARENT_DIR, 'files_to_serve')
UPLOAD_DIR = os.path.join(PARENT_DIR, 'uploads')

def get_time():
    return time.strftime("%Y%m%d-%H%M%S")

def ensure_unique(file_path):
    parts = file_path.split('.')
    extension = parts[-1]
    while os.path.isfile(file_path):
        file_path = f'{file_path}-{get_time()}.{extension}'
    return file_path
