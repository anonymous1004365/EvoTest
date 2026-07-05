#!/usr/bin/env python3
"""Vanilla LLM Defects4J generated-suite evaluation entry point.

This wrapper runs the same fixed-version generated-suite evaluator used by
EvoTest, but forces the pure Q&A baseline setting:

- no tools,
- no SkillBank,
- no multi-attempt continuation,
- focal method/source included directly in the prompt.

All additional CLI arguments are forwarded to
`run_defects4j_generated_suite_eval.py`.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


def main() -> None:
    target = Path(__file__).with_name("run_defects4j_generated_suite_eval.py")
    forwarded = [str(target), "--vanilla-llm", *sys.argv[1:]]
    sys.argv = forwarded
    runpy.run_path(str(target), run_name="__main__")


if __name__ == "__main__":
    main()
