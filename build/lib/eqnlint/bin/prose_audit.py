#!/bin/python
# ================================================================
# eqn-lint: Prose Audit Tool for LaTeX Papers
# Copyright (c) 2024 John Ryan
# Licensed under the MIT License
# https://opensource.org/licenses/MIT
# ================================================================

import sys
import argparse
import os
import re
import openai
from dotenv import load_dotenv

# === Load API Key ===
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    sys.exit("❌ ERROR: OPENAI_API_KEY not found. Please set it in a .env file.")
openai.api_key = OPENAI_API_KEY

# === Few-shot examples ===
few_shot_prose = [
    {"role": "system", "content": "You are an expert editor helping scientists write clean, concise, and accessible English."},
    {"role": "user", "content": """Paragraph:
In accordance with the methodologies delineated heretofore, the present exposition attempts to render comprehensible the fundamental axioms.

Audit:
Identify issues and suggest improvements."""},
    {"role": "assistant", "content": "❌ WORDY: This sentence is overly complex. ✅ Suggested: 'This paper explains the basic axioms using established methods.'"},
    {"role": "user", "content": """Paragraph:
This work provides an overview of quantum field theory and its applications to condensed matter physics.

Audit:
Identify issues and suggest improvements."""},
    {"role": "assistant", "content": "✅ CLEAR: The paragraph is concise and easy to understand."},
]

# === Helpers ===
def extract_paragraphs(tex_data):
    """Extract plain text paragraphs from LaTeX (ignores equations)."""
    # Remove LaTeX commands and equations
    cleaned = re.sub(r"\\begin\{.*?\}.*?\\end\{.*?\}", "", tex_data, flags=re.DOTALL)
    cleaned = re.sub(r"\$.*?\$", "", cleaned)
    paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]
    return paragraphs

def audit_prose(paragraph):
    """Call OpenAI to audit prose clarity."""
    prompt = f"""Paragraph:
\"\"\"{paragraph}\"\"\"

Audit:
Identify issues and suggest improvements."""
    messages = few_shot_prose + [{"role": "user", "content": prompt}]
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ OpenAI API error: {e}"

# === Main ===
def main():
    parser = argparse.ArgumentParser(description="Prose Audit for LaTeX papers")
    parser.add_argument("-f", "--file", required=True, help="Input LaTeX file")
    parser.add_argument("-o", "--output", help="Optional log file")
    parser.add_argument("--abstract-only", action="store_true", help="Only audit the abstract section")
    parser.add_argument("--dry-run", action="store_true", help="Show paragraphs without calling OpenAI")
    args = parser.parse_args()

    try:
        with open(args.file, "r") as f:
            tex_data = f.read()
    except FileNotFoundError:
        sys.exit(f"❌ ERROR: File {args.file} not found.")

    paragraphs = extract_paragraphs(tex_data)
    if args.abstract_only:
        abstract_match = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex_data, re.DOTALL)
        if abstract_match:
            paragraphs = [abstract_match.group(1).strip()]
        else:
            sys.exit("❌ ERROR: No abstract section found.")

    if args.dry_run:
        print("=== DRY RUN: Extracted Paragraphs ===")
        for i, para in enumerate(paragraphs, 1):
            print(f"\n--- Paragraph {i} ---")
            print(para)
        print("\n✅ Dry run complete.")
        sys.exit(0)

    log_lines = []
    for i, para in enumerate(paragraphs, 1):
        print(f"\n--- Paragraph {i} ---")
        print(para)
        result = audit_prose(para)
        print("🔍 Prose Check Result:")
        print(result)
        log_lines.append(f"--- Paragraph {i} ---\n{para}\n🔍 {result}\n")

    if args.output:
        with open(args.output, "w") as out:
            out.writelines("\n".join(log_lines))
        print(f"\n✅ Audit complete. Results saved to {args.output}")

if __name__ == "__main__":
    main()
