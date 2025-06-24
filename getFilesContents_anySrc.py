import os
import sys
import shutil
import tempfile
import subprocess
from pathlib import Path

def is_github_url(url):
    return url.startswith("https://github.com/") or url.startswith("git@github.com:")

def clone_github_repo(repo_url, dest_folder):
    try:
        subprocess.run(["git", "clone", repo_url, dest_folder], check=True)
        return dest_folder
    except subprocess.CalledProcessError as e:
        print("Failed to clone the repository:", e)
        sys.exit(1)

def find_src_folders(root_path):
    src_folders = []
    for dirpath, dirnames, _ in os.walk(root_path):
        for dirname in dirnames:
            if dirname.endswith(".src"):
                src_folders.append(os.path.join(dirpath, dirname))
    return src_folders

def collect_file_contents(root_path):
    contents = []

    # Walk the full tree and find all 'src' directories
    for dirpath, dirnames, filenames in os.walk(root_path):
        if os.path.basename(dirpath) == "src":
            for subdirpath, _, subfiles in os.walk(dirpath):
                for filename in subfiles:
                    file_path = os.path.join(subdirpath, filename)
                    rel_path = os.path.relpath(file_path, root_path)

                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            contents.append(f"\n=== ./{rel_path} ===\n")
                            contents.append(f.read())
                    except Exception as e:
                        contents.append(f"\n=== ./{rel_path} (Failed to read: {e}) ===\n")
    
    if not contents:
        print("No 'src/' directories found in the project.")
    
    return "\n".join(contents)
    contents = []
    src_folders = find_src_folders(root_path)

    if not src_folders:
        print(f"No '.src' folders found in {root_path}")
        return ""

    for src_path in src_folders:
        for dirpath, _, filenames in os.walk(src_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(file_path, root_path)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        contents.append(f"\n=== ./{rel_path} ===\n")
                        contents.append(f.read())
                except Exception as e:
                    contents.append(f"\n=== ./{rel_path} (Failed to read: {e}) ===\n")

    return "\n".join(contents)

def main(input_path):
    temp_dir = None
    if is_github_url(input_path):
        temp_dir = tempfile.mkdtemp()
        target_dir = clone_github_repo(input_path, temp_dir)
    else:
        target_dir = input_path

    output_file = "repository_contents_all_src.txt"

    print("[*] Searching for '.src' folders and collecting contents...")
    content_str = collect_file_contents(target_dir)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content_str)

    print(f"[*] Done! Output written to {output_file}")

    if temp_dir:
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python getFilesContents_anySrc.py <GitHub URL or local folder>")
        sys.exit(1)

    input_path = sys.argv[1]
    main(input_path)
