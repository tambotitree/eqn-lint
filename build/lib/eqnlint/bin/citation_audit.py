#!/bin/python
# ================================================================
# eqn-lint: Citation Audit Tool for LaTeX Papers
# Copyright (c) 2024 John Ryan
# Licensed under the MIT License
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
few_shot_citations = [
    {"role": "system", "content": "You are an expert in LaTeX and academic citation checking."},
    {"role": "user", "content": "Check citations in: The well-known result \\cite{Einstein1905} changed physics."},
    {"role": "assistant", "content": "✅ DEFINED: \\cite{Einstein1905} appears correctly."},
    {"role": "user", "content": "Check citations in: A new method was proposed in \\cite{MissingRef}."},
    {"role": "assistant", "content": "❌ UNDEFINED: \\cite{MissingRef} is not defined in the bibliography."},
    {"role": "user", "content": "Check citations in: Smith et al. (2023) proposed this, but the DOI cannot be verified."},
    {"role": "assistant", "content": "⚠️ POSSIBLY FABRICATED: Smith et al. (2023) is not verifiable; double check."}
]

# === Helpers ===
def extract_citations_and_context(tex_data):
    """Extract LaTeX citations and nearby context."""
    cite_pattern = r"(\\cite\{.*?\})|(\\bibitem\{.*?\})"
    matches = re.finditer(cite_pattern, tex_data, re.DOTALL)
    cites_with_context = []
    for m in matches:
        start, end = m.span()
        # Get ±1 paragraph context
        context_start = max(0, tex_data.rfind("\n\n", 0, start))
        context_end = tex_data.find("\n\n", end)
        if context_end == -1:
            context_end = len(tex_data)
        context = tex_data[context_start:context_end]
        cites_with_context.append({"citation": m.group().strip(), "context": context.strip()})
    return cites_with_context

def check_citation_consistency(citation, context):
    """Call OpenAI to check citation consistency."""
    prompt = f"""Check the following LaTeX citation for consistency:
Citation: {citation}
Context:
\"\"\"
{context}
\"\"\"
Respond with:
✅ DEFINED if found in bibliography.
❌ UNDEFINED if missing from bibliography.
⚠️ POSSIBLY FABRICATED if the citation seems non-existent or unverifiable."""
    messages = few_shot_citations + [{"role": "user", "content": prompt}]
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ OpenAI API error in check_citation_consistency: {e}"

# === Main ===
def main():
    parser = argparse.ArgumentParser(description="Citation Audit for LaTeX papers")
    parser.add_argument("-f", "--file", required=True, help="Input LaTeX file")
    parser.add_argument("-o", "--output", help="Optional log file")
    parser.add_argument("--dry-run", action="store_true", help="Only extract and display citations without API calls")
    args = parser.parse_args()

    try:
        with open(args.file, "r") as f:
            tex_data = f.read()
    except FileNotFoundError:
        sys.exit(f"❌ ERROR: File {args.file} not found.")

    cites = extract_citations_and_context(tex_data)

    if args.dry_run:
        print("=== DRY RUN: Extracted Citations and Contexts ===")
        for i, entry in enumerate(cites, 1):
            print(f"\n--- Citation {i} ---")
            print(entry['citation'])
            print("📄 Context:")
            print(entry['context'])
        print("\n✅ Dry run complete.")
        sys.exit(0)

    log_lines = []
    for i, entry in enumerate(cites, 1):
        print(f"\n--- Citation {i} ---")
        print(entry['citation'])
        result = check_citation_consistency(entry['citation'], entry['context'])
        print("🔍 Citation Check Result:")
        print(result)
        log_lines.append(f"--- Citation {i} ---\n{entry['citation']}\n🔍 {result}\n")

    if args.output:
        with open(args.output, "w") as out:
            out.writelines("\n".join(log_lines))
        print(f"\n✅ Citation audit complete. Results saved to {args.output}")

if __name__ == "__main__":
    main()
