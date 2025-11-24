#!/usr/bin/env python3
"""
WebSocket conformance summary generator script for GitHub Actions.

This script processes a WebSocket conformance index.json file and generates
a markdown table summarizing the test results for each testee.
"""

import json
import sys
import argparse
from pathlib import Path


def generate_summary(json_file: Path, title: str) -> str:
    """
    Generate a markdown summary table from an index.json file.

    Args:
        json_file: Path to the index.json file
        title: Title for the summary section

    Returns:
        Markdown formatted summary table as a string
    """
    if not json_file.exists():
        return f"⚠️  {json_file} not found\n"

    try:
        with open(json_file, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        return f"❌ Error reading {json_file}: {e}\n"

    # Build markdown table
    lines = [
        "",
        f"## {title}",
        "",
        "| Testee | Cases OK / Total | Status |",
        "|--------|------------------|---------|",
    ]

    for testee, cases in data.items():
        total_cases = len(cases)
        ok_cases = 0

        for case_id, case_data in cases.items():
            behavior = case_data.get("behavior")
            behavior_close = case_data.get("behaviorClose")

            # Test passes if both behaviors are OK, or both are INFORMATIONAL
            if (behavior == "OK" and behavior_close == "OK") or (
                behavior == "INFORMATIONAL" and behavior_close == "INFORMATIONAL"
            ):
                ok_cases += 1

        status = "✅" if ok_cases == total_cases else "❌"
        lines.append(f"| {testee} | {ok_cases} / {total_cases} | {status} |")

    return "\n".join(lines)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate WebSocket conformance summary table"
    )
    parser.add_argument("json_file", type=Path, help="Path to the index.json file")
    parser.add_argument("title", help="Title for the summary section")

    args = parser.parse_args()

    summary = generate_summary(args.json_file, args.title)
    print(summary)


if __name__ == "__main__":
    main()
