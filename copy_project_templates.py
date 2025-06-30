#!/usr/bin/env python3

import os
import shutil
from pathlib import Path

# --- Configuration ---

# The name of the current repository, used as the string to be replaced.
CURRENT_REPO_NAME = "autobahn-python"

# List of i) AI Policy and ii) GitHub template files to copy.
#
# src_file_str, replace_repo_name, create_docs_symlink
#
SOURCE_FILES = [
    ("OVERVIEW.md", False, True),
    ("AI_POLICY.md", True, True),
    ("AI_AUDIT_PROCESS.md", True, True),
    ("AI_AUDIT_PROCESS_REVIEW.md", False, True),
    ("CLAUDE.md", False, True),
    (".audit/README.md", True, False),
    (".github/pull_request_template.md", True, False),
    (".github/ISSUE_TEMPLATE/config.yml", True, False),
    (".github/ISSUE_TEMPLATE/bug_report.md", True, False),
    (".github/ISSUE_TEMPLATE/feature_request.md", True, False),
]

# List of target directories for copying the files.
DEST_DIRS = [
    (Path("."), True),
    (Path("../txaio"), False),
    (Path("../zlmdb"), False),
    (Path("../cfxdb"), False),
    (Path("../crossbar"), False),
]

# --- Main Logic ---


def main():
    """
    Copies a list of source files to multiple destination directories,
    preserving the directory structure, and performs a string replacement
    in a specific configuration file.
    """
    print("Copying AI Policy and GitHub templates via Python script...")

    for dest_dir, is_master in DEST_DIRS:
        if not dest_dir.is_dir():
            print(
                f"WARNING: Destination directory '{dest_dir}' does not exist. Skipping."
            )
            continue

        if not is_master:
            print(f"--- Syncing to: {dest_dir}")
        else:
            print(f"--- Processing master dir: {dest_dir}")

        step = 0

        # Iterate over all source files
        for src_file_str, replace_repo_name, create_docs_symlink in SOURCE_FILES:
            if not is_master:
                src_file = Path(src_file_str)
                dest_file = dest_dir / src_file

                # Create parent directories in destination if they don't exist
                dest_file.parent.mkdir(parents=True, exist_ok=True)

                # 1. Copy the file, preserving metadata
                step += 1
                step_str = "{:03d}".format(step)

                shutil.copy2(src_file, dest_file)
                print(
                    f"{step_str}  => OK, DONE! Copied template file '{src_file}' to '{dest_file}'"
                )

                # 2. Modify the specific config file after it has been copied
                step += 1
                step_str = "{:03d}".format(step)

                target_repo_name = dest_dir.name
                if replace_repo_name:
                    if dest_file.is_file():
                        # Read the file content
                        content = dest_file.read_text()
                        # Perform the replacement
                        new_content = content.replace(
                            CURRENT_REPO_NAME, target_repo_name
                        )
                        # Write the modified content back
                        dest_file.write_text(new_content)
                        print(
                            f"{step_str}  => OK, DONE! Modified repository name in '{dest_file}' to '{target_repo_name}'"
                        )
                else:
                    print(
                        f"{step_str}  =>     SKIP! NOT ENABLED - Not modifying repository name in '{dest_file}' to '{target_repo_name}'"
                    )

            # 3. Symlink config file into docs after it has been copied (or in master dir)
            step += 1
            step_str = "{:03d}".format(step)

            replace_existing_symlink = True
            dest_docs_symlink_target = Path(os.path.join("..", src_file_str))
            if create_docs_symlink:
                dest_docs_symlink = Path(os.path.join(dest_dir, "docs", src_file_str))
                if replace_existing_symlink and dest_docs_symlink.is_symlink():
                    dest_docs_symlink.unlink()
                if not dest_docs_symlink.is_symlink():
                    Path(dest_docs_symlink).symlink_to(dest_docs_symlink_target)
                    print(
                        f"{step_str}  => OK, DONE! Created symlink in docs, linking '{dest_docs_symlink}' to '{dest_docs_symlink_target}'"
                    )
                else:
                    print(
                        f"{step_str}  =>     SKIP! ALREADY EXISTS - Not creating symlink in docs, linking '{dest_docs_symlink}' to '{dest_docs_symlink_target}'"
                    )
            else:
                print(
                    f"{step_str}  =>     SKIP! NOT ENABLED - Not creating symlink in docs for '{dest_docs_symlink_target}'"
                )

    print("Done.")


if __name__ == "__main__":
    main()
