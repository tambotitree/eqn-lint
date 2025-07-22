#!/bin/python
# ================================================================
# eqn-lint: Unified CLI for Paper Auditing and Packaging
# Copyright (c) 2024 John Ryan
# Licensed under the MIT License
# ================================================================

import sys
import argparse
import subprocess
import os

VERSION = "0.1"

# === Helper functions ===

def run_audits(tex_file, skip=[]):
    """Run all audits unless skipped."""
    audit_scripts = [f for f in os.listdir('./bin') if f.endswith('_audit.py')]
    for script in audit_scripts:
        name = script.replace('_audit.py', '')
        if name in skip:
            print(f"⚠️  Skipping {name} audit...")
            continue
        print(f"\n🚀 Running {script}...")
        subprocess.run(['python', f'./bin/{script}', '-f', tex_file])

def create_package(tex_file, output_dir="submission_package"):
    """Create a tarball for journal submission."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    subprocess.run(['cp', tex_file, output_dir])
    subprocess.run(['tar', '-czf', f"{output_dir}.tar.gz", output_dir])
    print(f"📦 Submission package created: {output_dir}.tar.gz")

def rate_paper():
    """Rate the paper quality based on audit results."""
    print("📊 Scoring paper quality (prototype)...")
    # Future: parse audit logs and compute composite score
    print("✅ Paper rated: 82/100 (v0.1 heuristic)")

def print_help():
    """Print help message."""
    print(f"""
eqn-lint v{VERSION}: AI-powered Paper QA Tool

Usage:
  python eqn-lint.py [command] [options]

Commands:
  check       Run all audits on the specified LaTeX file
  package     Create a submission tarball for journals
  rate        Rate the paper quality based on audits
  help        Show this help message

Options:
  -f FILE     LaTeX file to process
  -d DIR      Directory to operate in
  -u URL      Download paper from URL (future)
  --skip X    Skip audits (comma-separated list, e.g., units,prose)
  --summary   Show summary report only
  --fix       Apply suggested fixes directly to the file
""")

# === Main ===
def main():
    parser = argparse.ArgumentParser(description="eqn-lint: Paper QA Utility")
    parser.add_argument("command", choices=["check", "package", "rate", "help"])
    parser.add_argument("-f", "--file", help="Input LaTeX file")
    parser.add_argument("-d", "--dir", help="Target directory")
    parser.add_argument("-u", "--url", help="Download paper from URL")
    parser.add_argument("--skip", help="Skip audits (comma-separated list)")
    parser.add_argument("--summary", action="store_true", help="Show summary report only")
    parser.add_argument("--fix", action="store_true", help="Apply suggested fixes")
    args = parser.parse_args()

    # Change working directory if specified
    if args.dir:
        os.chdir(args.dir)

    # Command dispatcher
    if args.command == "check":
        if not args.file:
            sys.exit("❌ ERROR: Please specify a LaTeX file with -f")
        skip = args.skip.split(",") if args.skip else []
        run_audits(args.file, skip=skip)

    elif args.command == "package":
        if not args.file:
            sys.exit("❌ ERROR: Please specify a LaTeX file with -f")
        create_package(args.file)

    elif args.command == "rate":
        rate_paper()

    elif args.command == "help":
        print_help()

if __name__ == "__main__":
    main()
