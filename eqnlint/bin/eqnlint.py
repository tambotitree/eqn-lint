#!/usr/bin/env python3
"""
eqnlint.py — Run all available audits sequentially.

Finds eqnlint/bin/*_audit.py and runs their main() in order.
All other CLI args are passed through to each audit.
"""

import sys
import argparse
import importlib
from pathlib import Path
from eqnlint import __version__

def main():
    # Provide --version at the top-level without consuming other args.
    top = argparse.ArgumentParser(add_help=False)
    top.add_argument("--version", action="version", version=f"eqnlint {__version__}")
    top.parse_known_args()  # don’t eat the rest; audits will parse them

    bin_dir = Path(__file__).resolve().parent
    audits = sorted(
        f.stem for f in bin_dir.glob("*_audit.py")
        if f.is_file() and not f.stem.startswith("_")
    )

    print(f"Running all audits: {', '.join(audits)}\n")

    exit_code = 0
    for name in audits:
        print(f"=== Running {name} ===")
        try:
            mod = importlib.import_module(f"eqnlint.bin.{name}")
            if hasattr(mod, "main"):
                mod.main()  # each audit uses base_parser(), which already has --version
            else:
                print(f"[WARN] {name} has no main(), skipping.")
        except SystemExit as e:
            if e.code not in (0, None):
                exit_code = e.code
        except Exception as e:
            print(f"[ERROR] {name} failed: {e}")
            exit_code = 1

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
