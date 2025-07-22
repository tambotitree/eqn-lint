#!/bin/python
# ================================================================
# eqn-lint: Context + Bibliography Audit Tool for LaTeX Papers
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
few_shot_context = [
    {"role": "system", "content": "You are an expert scientific reviewer. Audit citations for accuracy."},
    {"role": "user", "content": """Context:
“As shown in \\cite{Hestenes1990}, the Zitterbewegung motion explains intrinsic spin.”
Audit:
Does \\cite{Hestenes1990} support this claim?"""},
    {"role": "assistant", "content": "✅ ACCURATE: The statement correctly reflects the findings in Hestenes1990."},

    {"role": "user", "content": """Context:
“\\cite{Hestenes1990} demonstrates faster-than-light particles exist.”
Audit:
Does \\cite{Hestenes1990} support this claim?"""},
    {"role": "assistant", "content": "❌ FABRICATION: Hestenes1990 does not claim faster-than-light particles exist."},
]

# === Helpers ===
def extract_citation_context(tex_data):
    """Extract citation references and ±1 paragraph context."""
    cite_pattern = r"(\\cite\{(.*?)\})"
    matches = re.finditer(cite_pattern, tex_data)
    cites_with_context = []
    for m in matches:
        full_cite = m.group(1).strip()
        cite_keys = m.group(2).split(",")
        start, end = m.span()
        context_start = max(0, tex_data.rfind("\n\n", 0, start))
        context_end = tex_data.find("\n\n", end)
        if context_end == -1:
            context_end = len(tex_data)
        context = tex_data[context_start:context_end]
        for key in cite_keys:
            cites_with_context.append({"cite": key.strip(), "full_cite": full_cite, "context": context.strip()})
    return cites_with_context

def check_bib_entries(tex_data):
    """Check for linked .bib file and parse keys."""
    bib_pattern = r"\\bibliography\{(.*?)\}|\\addbibresource\{(.*?)\}"
    match = re.search(bib_pattern, tex_data)
    if not match:
        return None, {}
    bib_file = match.group(1) or match.group(2)
    if not bib_file.endswith(".bib"):
        bib_file += ".bib"
    if not os.path.isfile(bib_file):
        print(f"⚠️ WARNING: Bibliography file '{bib_file}' not found.")
        return bib_file, {}

    with open(bib_file, "r") as bf:
        bib_data = bf.read()

    bib_keys = set(re.findall(r"@\w+\{(.*?),", bib_data))
    return bib_file, bib_keys

def check_citation_context(cite, context):
    """Call OpenAI to check citation accuracy."""
    prompt = f"""Context:
\"\"\"{context}\"\"\"
Audit:
Does \\cite{{{cite}}} support this claim?"""
    messages = few_shot_context + [{"role": "user", "content": prompt}]
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
    parser = argparse.ArgumentParser(description="Context + Bibliography Audit for LaTeX citations")
    parser.add_argument("-f", "--file", required=True, help="Input LaTeX file")
    parser.add_argument("-o", "--output", help="Optional log file")
    parser.add_argument("--dry-run", action="store_true", help="Only extract citations and contexts without API calls")
    args = parser.parse_args()

    try:
        with open(args.file, "r") as f:
            tex_data = f.read()
    except FileNotFoundError:
        sys.exit(f"❌ ERROR: File {args.file} not found.")

    cites = extract_citation_context(tex_data)
    bib_file, bib_keys = check_bib_entries(tex_data)

    log_lines = []
    if bib_file:
        print(f"📖 Bibliography file detected: {bib_file}")
    else:
        print("⚠️ No bibliography file detected.")

    for i, entry in enumerate(cites, 1):
        print(f"\n--- Citation {i} ---")
        print(f"\\cite{{{entry['cite']}}}")

        # Check if citation exists in bibliography
        if bib_keys and entry['cite'] not in bib_keys:
            print(f"❌ MISSING: \\cite{{{entry['cite']}}} not found in {bib_file}.")
            log_lines.append(f"--- Citation {i} ---\n\\cite{{{entry['cite']}}}\n❌ MISSING in {bib_file}\n")
            continue

        if args.dry_run:
            print("📄 Context:")
            print(entry['context'])
            continue

        result = check_citation_context(entry['cite'], entry['context'])
        print("🔍 Context Check Result:")
        print(result)
        log_lines.append(f"--- Citation {i} ---\n\\cite{{{entry['cite']}}}\n📄 {entry['context']}\n🔍 {result}\n")

    if args.output:
        with open(args.output, "w") as out:
            out.writelines("\n".join(log_lines))
        print(f"\n✅ Audit complete. Results saved to {args.output}")

if __name__ == "__main__":
    main()
