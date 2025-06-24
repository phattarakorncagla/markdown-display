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

def collect_file_contents(root_path):
    contents = []
    target_src_path = os.path.join(root_path, "public-server", "src")

    if not os.path.isdir(target_src_path):
        print(f"No 'public-server/src' directory found in {root_path}")
        return ""

    for dirpath, _, filenames in os.walk(target_src_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(file_path, target_src_path)  # relative to public-server/src

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    contents.append(f"\n=== ./public-server/src/{rel_path} ===\n")
                    contents.append(f.read())
            except Exception as e:
                contents.append(f"\n=== ./public-server/src/{rel_path} (Failed to read: {e}) ===\n")

    return "\n".join(contents)

def main(input_path):
    temp_dir = None
    if is_github_url(input_path):
        temp_dir = tempfile.mkdtemp()
        target_dir = clone_github_repo(input_path, temp_dir)
    else:
        target_dir = input_path

    output_file = "repository_contents.txt"

    print("[*] Collecting file contents...")
    content_str = collect_file_contents(target_dir)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content_str)

    print(f"[*] Done! Output written to {output_file}")

    if temp_dir:
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python getFilesContents.py <GitHub URL or local folder>")
        sys.exit(1)

    input_path = sys.argv[1]
    main(input_path)
