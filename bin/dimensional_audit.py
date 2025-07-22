#!/bin/python
# ================================================================
# eqn-lint: Dimensional Audit Tool for LaTeX Papers
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
few_shot_symbols = [
    {"role": "system", "content": "You are an expert in dimensional analysis and LaTeX math."},
    {"role": "user", "content": "Build a symbol dictionary for: E = mc^2"},
    {"role": "assistant", "content": """{
  "E": "energy (J)",
  "m": "mass (kg)",
  "c": "speed of light (m/s)"
}"""},
]

few_shot_dimensions = [
    {"role": "system", "content": "You are auditing LaTeX math for dimensional consistency."},
    {"role": "user", "content": """Check: E = mc^2
Symbols:
{
  "E": "energy (J)",
  "m": "mass (kg)",
  "c": "speed of light (m/s)"
}"""},
    {"role": "assistant", "content": "✅ CONSISTENT: [J] = [kg][m/s]^2 is dimensionally valid."},
]

# === Helpers ===
def extract_equations_and_context(tex_data):
    """Extract LaTeX equations and nearby context."""
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

def build_symbol_dict(equation, context):
    """Call OpenAI to build symbol dictionary."""
    prompt = f"""Given the equation:\n{equation}\n\nAnd nearby context:\n\"\"\"\n{context}\n\"\"\"\nBuild a JSON symbol dictionary mapping each symbol to its meaning and SI dimensions."""
    messages = few_shot_symbols + [{"role": "user", "content": prompt}]
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ OpenAI API error in build_symbol_dict: {e}"

def check_dimensions(equation, symbol_dict):
    """Call OpenAI to check dimensional consistency."""
    prompt = f"""Check dimensional consistency of:\n{equation}\n\nSymbols:\n{symbol_dict}"""
    messages = few_shot_dimensions + [{"role": "user", "content": prompt}]
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ OpenAI API error in check_dimensions: {e}"

# === Main ===
def main():
    parser = argparse.ArgumentParser(description="Dimensional Audit for LaTeX papers")
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
        symbol_dict = build_symbol_dict(entry['equation'], entry['context'])
        print("📖 Symbol Dictionary:")
        print(symbol_dict)
        result = check_dimensions(entry['equation'], symbol_dict)
        print("📊 Audit Result:")
        print(result)
        log_lines.append(f"--- Equation {i} ---\n{entry['equation']}\n📖 {symbol_dict}\n📊 {result}\n")

    if args.output:
        with open(args.output, "w") as out:
            out.writelines("\n".join(log_lines))
        print(f"\n✅ Audit complete. Results saved to {args.output}")

if __name__ == "__main__":
    main()
