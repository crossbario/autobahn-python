#!/usr/bin/env python3

import os
import shutil
from pathlib import Path

# --- Configuration ---

# The name of the current repository, used as the string to be replaced.
CURRENT_REPO_NAME = "autobahn-python"

# List of i) AI Policy and ii) GitHub template files to copy.
SOURCE_FILES = [
    ("OVERVIEW.md", False),
    ("AI_AUDIT_PROCESS.md", True),
    ("AI_POLICY.md", True),
    ("CLAUDE.md", False),
    (".audit/README.md", True),
    (".github/pull_request_template.md", True),
    (".github/ISSUE_TEMPLATE/config.yml", True),
    (".github/ISSUE_TEMPLATE/bug_report.md", True),
    (".github/ISSUE_TEMPLATE/feature_request.md", True),
]

# List of target directories for copying the files.
DEST_DIRS = [
    Path("../txaio"),
    Path("../zlmdb"),
    Path("../cfxdb"),
    Path("../crossbar"),
]

# --- Main Logic ---

def main():
    """
    Copies a list of source files to multiple destination directories,
    preserving the directory structure, and performs a string replacement
    in a specific configuration file.
    """
    print("Copying AI Policy and GitHub templates via Python script...")

    for dest_dir in DEST_DIRS:
        if not dest_dir.is_dir():
            print(f"WARNING: Destination directory '{dest_dir}' does not exist. Skipping.")
            continue

        print(f"--- Syncing to: {dest_dir}")

        # 1. Copy all source files
        for src_file_str, replace_repo_name in SOURCE_FILES:
            src_file = Path(src_file_str)
            dest_file = dest_dir / src_file

            # Create parent directories in destination if they don't exist
            dest_file.parent.mkdir(parents=True, exist_ok=True)

            # Copy the file, preserving metadata
            shutil.copy2(src_file, dest_file)

            # 2. Modify the specific config file after it has been copied
            if replace_repo_name:
                target_repo_name = dest_dir.name
                if dest_file.is_file():
                    print(f"  => Modifying repository name in {dest_file} to '{target_repo_name}'")
                    # Read the file content
                    content = dest_file.read_text()
                    # Perform the replacement
                    new_content = content.replace(CURRENT_REPO_NAME, target_repo_name)
                    # Write the modified content back
                    dest_file.write_text(new_content)

    print("Done.")

if __name__ == "__main__":
    main()
