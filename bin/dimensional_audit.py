#!/usr/bin/env python3
# bin/dimensional_audit.py
import sys, os, json
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1] / "lib"))

from eqnlint.lib._cli import base_parser, info_block, write_outputs
from eqnlint.lib._textio import read_text, emit_human, emit_json
from eqnlint.lib._extract import extract_equations_with_context
from eqnlint.lib._ai import AIClient

AUDIT = "dimensional"
SUMMARY = "Checks SI dimensional consistency of each extracted equation."
INPUTS = "-f TEX_FILE; optional --dry-run; optional model selection."
OUTPUTS = "Human log to -o; JSON to --json with per-equation verdicts."
STEPS = """\
1) Extract equations from LaTeX.
2) For each, build symbol dictionary guess and units hints.
3) Ask model to verify dimensional balance; return verdict + notes.
4) Emit human and JSON reports.
"""

def main():
    p = base_parser("Dimensional Audit", AUDIT)
    args = p.parse_args()

    if args.help_info:
        print(info_block(AUDIT, SUMMARY, INPUTS, OUTPUTS, STEPS))
        sys.exit(0)

    tex = read_text(args.file)
    eqs = extract_equations_with_context(tex)
    if args.dry_run:
        human = emit_human("=== DRY RUN: Equations ===",
                           [f"\n--- Equation {i+1} ---\n{e['equation']}\n\n{e['context']}"
                            for i,e in enumerate(eqs)])
        write_outputs(human, {"equations":[e["equation"] for e in eqs]}, args.output, args.json)
        sys.exit(0)

    ai = AIClient(args.model, rate=args.rate, max_tokens=args.max_tokens)
    system = "You are a rigorous SI dimensional analysis assistant. Be strict and concise."
    # Load few-shot if you like from prompts/dimensional.yaml (omitted here)

    results=[]
    for i,e in enumerate(eqs,1):
        user = f"""Equation:
{e['equation']}

Context:
{e['context']}

Task: List symbols with their likely SI dimensions; check both sides match.
Return JSON with keys: verdict ("CONSISTENT"/"INCONSISTENT"), notes (short), symbols (dict)."""
        try:
            txt = ai.complete(system, user)
            # accept raw JSON or short text; be robust:
            try:
                obj = json.loads(txt)
            except Exception:
                obj = {"verdict": "UNKNOWN", "notes": txt.strip(), "symbols": {}}
        except Exception as ex:
            obj = {"verdict":"ERROR","notes":str(ex),"symbols":{}}
        results.append({"index":i, "equation":e["equation"], **obj})

    # Human log
    lines=[]
    for r in results:
        lines.append(f"\n--- Equation {r['index']} ---\n{r['equation']}\n"
                     f"Result: {r.get('verdict','?')} — {r.get('notes','')}")
    human = emit_human("=== Dimensional Audit ===", lines)
    write_outputs(human, emit_json(audit=AUDIT, results=results), args.output, args.json)

if __name__ == "__main__":
    main()
