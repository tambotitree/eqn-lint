#!/bin/python
# ================================================================
# eqn-lint: Units Audit Tool for LaTeX Papers
# Copyright (c) 2024 John Ryan
# Licensed under the MIT License
# https://opensource.org/licenses/MIT
# ================================================================

import sys
import argparse
import re
import os
import openai
from dotenv import load_dotenv

# === Load API Key ===
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    sys.exit("❌ ERROR: OPENAI_API_KEY not found. Please set it in a .env file.")
openai.api_key = OPENAI_API_KEY

# === Few-shot examples ===
few_shot_units = [
    {"role": "system", "content": "You are auditing LaTeX equations for unit system consistency and detecting non-standard units."},
    {"role": "user", "content": """Check the units in: F = ma
Context: Newton's second law. All units are SI.
"""},
    {"role": "assistant", "content": "✅ CONSISTENT: All units are SI (Force in N, mass in kg, acceleration in m/s^2)."},
    {"role": "user", "content": """Check the units in: P = IV
Context: Electric power equation. Units: I in Amps, V in Volts, P in Watts.
"""},
    {"role": "assistant", "content": "✅ CONSISTENT: All units are SI."},
    {"role": "user", "content": """Check the units in: F = mg
Context: g = 32 ft/s^2
"""},
    {"role": "assistant", "content": "❌ INCONSISTENT: g uses Imperial units (ft/s^2) while the rest of the equation likely expects SI. Consider converting to m/s^2."},
    {"role": "user", "content": """Check the units in: E = hc/λ
Context: E in eV, h in J·s, c in m/s, λ in nm.
"""},
    {"role": "assistant", "content": "⚠️ MIXED UNITS: Energy is in eV and wavelength in nm, while Planck’s constant uses SI units. Consider converting to consistent units."},
]

# === Helpers ===
def extract_equations_and_context(tex_data):
    """Extract LaTeX equations and nearby context."""
    eqn_pattern = r"(\\begin\{equation\}.*?\\end\{equation\})|(\$\$.*?\$\$)|(\$.*?\$)"
    matches = re.finditer(eqn_pattern, tex_data, re.DOTALL)
    eqns_with_context = []
    for m in matches:
        start, end = m.span()
        context_start = max(0, tex_data.rfind("\n\n", 0, start))
        context_end = tex_data.find("\n\n", end)
        if context_end == -1:
            context_end = len(tex_data)
        context = tex_data[context_start:context_end]
        eqns_with_context.append({"equation": m.group().strip(), "context": context.strip()})
    return eqns_with_context

def check_units(equation, context):
    """Call OpenAI to check unit consistency."""
    prompt = f"""Check the units in: {equation}\nContext: {context}"""
    messages = few_shot_units + [{"role": "user", "content": prompt}]
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ OpenAI API error in check_units: {e}"

# === Main ===
def main():
    parser = argparse.ArgumentParser(description="Units Audit for LaTeX papers")
    parser.add_argument("-f", "--file", required=True, help="Input LaTeX file")
    parser.add_argument("-o", "--output", help="Optional log file")
    parser.add_argument("--dry-run", action="store_true", help="Only extract and display equations without API calls")
    args = parser.parse_args()

    try:
        with open(args.file, "r") as f:
            tex_data = f.read()
    except FileNotFoundError:
        sys.exit(f"❌ ERROR: File {args.file} not found.")

    eqns = extract_equations_and_context(tex_data)

    if args.dry_run:
        print("=== DRY RUN: Extracted Equations and Contexts ===")
        for i, entry in enumerate(eqns, 1):
            print(f"\n--- Equation {i} ---")
            print(entry['equation'])
            print("📄 Context:")
            print(entry['context'])
        print("\n✅ Dry run complete.")
        sys.exit(0)

    log_lines = []
    for i, entry in enumerate(eqns, 1):
        print(f"\n--- Equation {i} ---")
        print(entry['equation'])
        result = check_units(entry['equation'], entry['context'])
        print("🔍 Units Check Result:")
        print(result)
        log_lines.append(f"--- Equation {i} ---\n{entry['equation']}\n🔍 {result}\n")

    if args.output:
        with open(args.output, "w") as out:
            out.writelines("\n".join(log_lines))
        print(f"\n✅ Audit complete. Results saved to {args.output}")

if __name__ == "__main__":
    main()
