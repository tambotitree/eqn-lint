#!/bin/python
# ================================================================
# eqn-lint: Opacity Audit Tool for LaTeX Papers
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

# === Few-shot examples for opacity checking ===
few_shot_opacity = [
    {"role": "system", "content": "You are an AI that reviews LaTeX papers for opaque or undefined symbols, acronyms, and notation."},
    {"role": "user", "content": """Check this equation:
\\begin{equation}
\\Delta G = \\Delta H - T \\Delta S
\\end{equation}
Context:
This is a standard Gibbs free energy equation. \\Delta H is the enthalpy change, \\Delta S is the entropy change, but T is used without explanation.

Output:
❌ UNDEFINED SYMBOL: T appears in the equation but is not defined in the nearby text. Consider defining it as 'Temperature (K)'."""},
    {"role": "user", "content": """Check this equation:
\\begin{equation}
E = mc^2
\\end{equation}
Context:
Special relativity: m is mass, c is speed of light, E is energy.

Output:
✅ ALL SYMBOLS DEFINED: No undefined symbols found in nearby text."""}
]

# === Helpers ===
def extract_equations_and_context(tex_data):
    """Extract LaTeX equations and nearby text."""
    eqn_pattern = r"(\\begin\{equation\}.*?\\end\{equation\})|(\$\$.*?\$\$)|(\$.*?\$)"
    matches = re.finditer(eqn_pattern, tex_data, re.DOTALL)
    eqns_with_context = []
    for m in matches:
        start, end = m.span()
        # Get ±2 paragraphs for context
        context_start = max(0, tex_data.rfind("\n\n", 0, start))
        context_end = tex_data.find("\n\n", end)
        if context_end == -1:
            context_end = len(tex_data)
        context = tex_data[context_start:context_end]
        eqns_with_context.append({"equation": m.group().strip(), "context": context.strip()})
    return eqns_with_context

def check_opacity(equation, context):
    """Call OpenAI to check for opacity/undefined symbols."""
    prompt = f"""Check this equation:
{equation}
Context:
{context}

Identify any undefined symbols, acronyms, or notations that are missing from the context. Suggest clear definitions or mark as OK if all symbols are well-defined."""
    messages = few_shot_opacity + [{"role": "user", "content": prompt}]
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ OpenAI API error in check_opacity: {e}"

# === Main ===
def main():
    parser = argparse.ArgumentParser(description="Opacity Audit for LaTeX papers")
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
        result = check_opacity(entry['equation'], entry['context'])
        print("🔍 Opacity Check Result:")
        print(result)
        log_lines.append(f"--- Equation {i} ---\n{entry['equation']}\n🔍 {result}\n")

    if args.output:
        with open(args.output, "w") as out:
            out.writelines("\n".join(log_lines))
        print(f"\n✅ Opacity audit complete. Results saved to {args.output}")

if __name__ == "__main__":
    main()
