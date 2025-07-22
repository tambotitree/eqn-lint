#!/bin/python
# ================================================================
# eqn-lint: Run All Audits for LaTeX Papers
# Copyright (c) 2024 John Ryan
# Licensed under the MIT License
# ================================================================

import subprocess
import sys
import os
import glob
import argparse

def main():
    parser = argparse.ArgumentParser(description="Run all eqn-lint audits on a LaTeX file")
    parser.add_argument("-f", "--file", required=True, help="Input LaTeX file")
    parser.add_argument("--dry-run", action="store_true", help="Only extract and display without API calls")
    parser.add_argument("--skip", nargs="*", help="List of audit scripts to skip (by filename)")
    args = parser.parse_args()

    tex_file = args.file
    extra_args = []
    if args.dry_run:
        extra_args.append("--dry-run")

    if not os.path.isfile(tex_file):
        sys.exit(f"❌ ERROR: File {tex_file} not found.")

    audit_scripts = sorted(glob.glob("./bin/*_audit.py"))

    if args.skip:
        audit_scripts = [s for s in audit_scripts if os.path.basename(s) not in args.skip]

    if not audit_scripts:
        sys.exit("❌ ERROR: No *_audit.py scripts found in ./bin/")

    print(f"📄 Running all audits on: {tex_file}\n")

    for script in audit_scripts:
        print(f"🚀 Running {os.path.basename(script)}...")
        cmd = ["python", script, "-f", tex_file] + extra_args
        try:
            subprocess.run(cmd, check=True)
            print(f"✅ Completed {os.path.basename(script)}\n")
        except subprocess.CalledProcessError:
            print(f"❌ ERROR: {os.path.basename(script)} failed.\n")

    print("🎉 All audits completed.")

if __name__ == "__main__":
    main()
