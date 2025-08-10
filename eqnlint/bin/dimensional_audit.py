#!/usr/bin/env python3
# bin/dimensional_audit.py
"""
dimensional_audit.py — Audit LaTeX equations for SI *dimensional* consistency.

This reuses the shared AuditStateMachine so it behaves like the other audits.
It asks for a categorical verdict with a brief reason focused on dimensions.
"""

import asyncio

from eqnlint.bin.audit_template import AuditStateMachine, State
from eqnlint.lib._fewshots import FewShotLibrary


class DimensionalAuditStateMachine(AuditStateMachine):
    def _get_few_shots(self):
        # System prompt + few-shot examples specialized for dimensional analysis
        self.system_prompt = (
            "You are auditing LaTeX equations for SI *dimensional* consistency. "
            "Be strict and concise. Prefer categorical answers with a short rationale."
        )
        self.few_shots = FewShotLibrary.dimensions()
        self.state = State.CALL_AI_WITH_FEW_SHOTS_AND_TARGETS
        self.log.debug(f"Audit Dimensional: few shots returns {self.few_shots}")
        self.log.debug(f"Audit Dimensional: After State call {self.state}")

    def _build_prompt(self, eq: dict) -> str:
        # Keep outputs short & categorical so our report is stable and easy to scan.
        return (
            "Task: Determine SI *dimensional* consistency of both sides.\n"
            f"Equation:\n{eq['equation']}\n"
            f"Context:\n{eq['context']}\n"
            "Return exactly one of: ✅ CONSISTENT or ❌ INCONSISTENT — "
            "plus a one‑sentence reason that references dimensions (e.g., "
            "[J] vs [kg·m^2·s^-2], or curvature ~ m^-2, etc.).\n"
        )


def main():
    asyncio.run(DimensionalAuditStateMachine().run())


if __name__ == "__main__":
    main()