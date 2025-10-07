#!/usr/bin/env python3
"""
WebSocket conformance verification script for GitHub Actions.

This script checks if all test cases in a WebSocket conformance index.json file
have passed (behavior: "OK" and behaviorClose: "OK", or both "INFORMATIONAL").
"""

import json
import sys
import argparse
from pathlib import Path


def verify_conformance(json_file: Path, test_type: str) -> bool:
    """
    Verify 100% conformance for a given index.json file.
    
    Args:
        json_file: Path to the index.json file
        test_type: Type of test (e.g., "Client" or "Server")
    
    Returns:
        True if all tests passed, False otherwise
    """
    if not json_file.exists():
        print(f"❌ {json_file} not found")
        return False
    
    print(f"==> Checking {test_type} conformance...")
    
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"❌ Error reading {json_file}: {e}")
        return False
    
    all_passed = True
    total_testees = len(data)
    passed_testees = 0
    
    for testee, cases in data.items():
        total_cases = len(cases)
        ok_cases = 0
        failed_cases = []
        
        for case_id, case_data in cases.items():
            behavior = case_data.get("behavior")
            behavior_close = case_data.get("behaviorClose")
            
            # Test passes if both behaviors are OK, or both are INFORMATIONAL
            if (behavior == "OK" and behavior_close == "OK") or \
               (behavior == "INFORMATIONAL" and behavior_close == "INFORMATIONAL"):
                ok_cases += 1
            else:
                failed_cases.append({
                    "case_id": case_id,
                    "behavior": behavior,
                    "behaviorClose": behavior_close
                })
        
        if ok_cases == total_cases:
            print(f'✅ {testee}: {ok_cases}/{total_cases} tests passed')
            passed_testees += 1
        else:
            print(f'❌ {testee}: {ok_cases}/{total_cases} tests passed')
            # Show details of first few failed cases for debugging
            for i, failed_case in enumerate(failed_cases[:3]):
                print(f'   Failed case {failed_case["case_id"]}: '
                      f'behavior={failed_case["behavior"]}, '
                      f'behaviorClose={failed_case["behaviorClose"]}')
            if len(failed_cases) > 3:
                print(f'   ... and {len(failed_cases) - 3} more failed cases')
            all_passed = False
    
    print(f'')
    print(f'{test_type} Summary: {passed_testees}/{total_testees} testees passed all tests')
    
    if not all_passed:
        print(f'❌ {test_type} conformance: FAILED - Not all tests passed')
        return False
    else:
        print(f'✅ {test_type} conformance: PASSED - All tests passed')
        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Verify WebSocket conformance test results')
    parser.add_argument('client_json', type=Path, help='Path to client index.json file')
    parser.add_argument('server_json', type=Path, help='Path to server index.json file')
    
    args = parser.parse_args()
    
    print("==> Verifying 100% WebSocket conformance...")
    
    client_passed = verify_conformance(args.client_json, "Client")
    print("")
    server_passed = verify_conformance(args.server_json, "Server")
    
    print("")
    print("==> Overall WebSocket Conformance Verification:")
    
    if client_passed and server_passed:
        print("✅ PASSED - Both client and server conformance tests achieved 100% pass rate")
        sys.exit(0)
    else:
        print("❌ FAILED - One or more conformance tests did not achieve 100% pass rate")
        print("")
        print("This means the WebSocket implementation has conformance issues that need to be addressed.")
        print("Download the detailed reports from the workflow artifacts to investigate specific failures.")
        sys.exit(1)


if __name__ == "__main__":
    main()