import os
import re
import sys
import shutil

SEARCH_TEXT = "OpenLinuxTrainer"
REPLACEMENT_TEXT = "CloudedTrainer"
TEXT_FILE_EXTENSIONS = ('.txt', '.py', '.md', '.json', '.xml', '.html', '.css', '.js', '.ini', '.cfg', '.csv', '.yml', '.yaml')

script_path = os.path.abspath(sys.argv[0])

def is_text_file(filepath):
    return filepath.endswith(TEXT_FILE_EXTENSIONS)

def replace_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        if SEARCH_TEXT not in content:
            return
        new_content = content.replace(SEARCH_TEXT, REPLACEMENT_TEXT)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"[UPDATED] {filepath}")
    except (UnicodeDecodeError, PermissionError) as e:
        print(f"[SKIPPED] {filepath} (reason: {e})")

def rename_if_needed(path):
    dirname, basename = os.path.split(path)
    if SEARCH_TEXT in basename:
        new_basename = basename.replace(SEARCH_TEXT, REPLACEMENT_TEXT)
        new_path = os.path.join(dirname, new_basename)
        shutil.move(path, new_path)
        print(f"[RENAMED] {path} -> {new_path}")
        return new_path
    return path

# Walk the directory tree bottom-up to safely rename folders
for root, dirs, files in os.walk('.', topdown=False):
    # Rename files and replace content
    for name in files:
        full_path = os.path.abspath(os.path.join(root, name))
        if full_path == script_path:
            continue  # Don't modify or rename this script
        if is_text_file(full_path):
            replace_in_file(full_path)
        new_file_path = rename_if_needed(full_path)

    # Rename directories
    for name in dirs:
        dir_path = os.path.abspath(os.path.join(root, name))
        rename_if_needed(dir_path)

