#!/bin/python
# ================================================================
# eqn-lint: Symbolic Audit Tool for LaTeX Papers
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

# === Few-shot examples (escaped braces & backslashes) ===
symbol_dict_few_shot = """
Example 1:
Equation:
\\begin{{equation}}
F = ma
\\end{{equation}}
Context:
Newton's second law, where F is force, m is mass, and a is acceleration.

Output:
{{
  "F": "Force (N)",
  "m": "Mass (kg)",
  "a": "Acceleration (m/s^2)"
}}

Example 2:
Equation:
\\begin{{equation}}
g_{{\\mu\\nu}} = \\eta_{{\\mu\\nu}} + h_{{\\mu\\nu}}
\\end{{equation}}
Context:
General relativity: g_{{\\mu\\nu}} is the metric tensor, \\eta_{{\\mu\\nu}} is the Minkowski metric, and h_{{\\mu\\nu}} is a perturbation.

Output:
{{
  "g_{{\\mu\\nu}}": "Metric tensor (dimensionless)",
  "\\eta_{{\\mu\\nu}}": "Minkowski metric tensor (dimensionless)",
  "h_{{\\mu\\nu}}": "Perturbation tensor (dimensionless)"
}}

Example 3:
Equation:
\\begin{{equation}}
E = mc^2
\\end{{equation}}
Context:
Special relativity, where E is energy, m is mass, and c is the speed of light.

Output:
{{
  "E": "Energy (J)",
  "m": "Mass (kg)",
  "c^2": "Speed of light squared (m^2/s^2)"
}}

Now process:
Equation:
{equation}
Context:
{context}
Output:
"""

symbolic_consistency_few_shot = """
Example 1:
Equation:
\\begin{{equation}}
F = ma
\\end{{equation}}
Symbol meanings:
{{
  "F": "Force (N)",
  "m": "Mass (kg)",
  "a": "Acceleration (m/s^2)"
}}
Output:
✅ CONSISTENT: Both sides of the equation have dimensions of force (N).

Example 2:
Equation:
\\begin{{equation}}
g_{{\\mu\\nu}} = \\eta_{{\\mu\\nu}} + h_{{\\mu\\nu}}
\\end{{equation}}
Symbol meanings:
{{
  "g_{{\\mu\\nu}}": "Metric tensor (dimensionless)",
  "\\eta_{{\\mu\\nu}}": "Minkowski metric tensor (dimensionless)",
  "h_{{\\mu\\nu}}": "Perturbation tensor (dimensionless)"
}}
Output:
✅ CONSISTENT: Tensor indices are correctly contracted on both sides.

Example 3:
Equation:
\\begin{{equation}}
F = m + a
\\end{{equation}}
Symbol meanings:
{{
  "F": "Force (N)",
  "m": "Mass (kg)",
  "a": "Acceleration (m/s^2)"
}}
Output:
❌ INCONSISTENT: Cannot add mass (kg) and acceleration (m/s^2).

Now process:
Equation:
{equation}
Symbol meanings:
{symbol_dict}
Output:
"""

# === Helpers ===
def extract_equations_and_context(tex_data):
    """Extract equations + nearby context from LaTeX."""
    eqn_pattern = r"(\\begin\{equation\}.*?\\end\{equation\})|(\$\$.*?\$\$)|(\$.*?\$)"
    matches = re.finditer(eqn_pattern, tex_data, re.DOTALL)
    eqns_with_context = []
    for m in matches:
        start, end = m.span()
        # Get ±2 paragraphs around equation for context
        context_start = max(0, tex_data.rfind("\n\n", 0, start))
        context_end = tex_data.find("\n\n", end)
        if context_end == -1:
            context_end = len(tex_data)
        context = tex_data[context_start:context_end]
        eqns_with_context.append({"equation": m.group().strip(), "context": context.strip()})
    return eqns_with_context

def build_symbol_dict(equation, context):
    """Call OpenAI to build symbol dictionary from context."""
    prompt = symbol_dict_few_shot.format(equation=equation, context=context)
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ OpenAI API error in build_symbol_dict: {e}"

def check_symbolic_consistency(equation, symbol_dict):
    """Call OpenAI to check symbolic consistency."""
    prompt = symbolic_consistency_few_shot.format(equation=equation, symbol_dict=symbol_dict)
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ OpenAI API error in check_symbolic_consistency: {e}"

# === Main ===
def main():
    parser = argparse.ArgumentParser(description="Symbolic Audit for LaTeX papers")
    parser.add_argument("-f", "--file", required=True, help="Input LaTeX file")
    parser.add_argument("-o", "--output", help="Optional log file")
    args = parser.parse_args()

    try:
        with open(args.file, "r") as f:
            tex_data = f.read()
    except FileNotFoundError:
        sys.exit(f"❌ ERROR: File {args.file} not found.")

    eqns = extract_equations_and_context(tex_data)

    log_lines = []
    for i, entry in enumerate(eqns, 1):
        print(f"\n--- Equation {i} ---")
        print(entry['equation'])

        # Skip trivial single symbols gracefully
        if re.match(r'^\$?[\w\\\{\}^_]+\$?$', entry['equation']):
            print("📖 Symbol Dictionary: Skipped (single term)")
            print("📊 Audit Result: ✅ TRIVIAL PASS")
            log_lines.append(f"--- Equation {i} ---\n{entry['equation']}\n📖 Skipped (single term)\n📊 ✅ TRIVIAL PASS\n")
            continue

        symbol_dict = build_symbol_dict(entry['equation'], entry['context'])
        print("📖 Symbol Dictionary:")
        print(symbol_dict)
        result = check_symbolic_consistency(entry['equation'], symbol_dict)
        print("📊 Audit Result:")
        print(result)
        log_lines.append(f"--- Equation {i} ---\n{entry['equation']}\n📖 {symbol_dict}\n📊 {result}\n")

    if args.output:
        with open(args.output, "w") as out:
            out.writelines("\n".join(log_lines))
        print(f"\n✅ Audit complete. Results saved to {args.output}")

if __name__ == "__main__":
    main()
