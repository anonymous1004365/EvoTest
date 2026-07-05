# Baseline References

This directory does not contain EvoTest-side baseline reproduction code.
Baseline reproduction should use the original upstream repositories or
Defects4J official tooling.

## Files

- `baselines.lock.json`: upstream repository URLs and commit hashes used for
  the comparisons.

## Policy

- Third-party baseline source code is not vendored in this package.
- EvoTest-side baseline reproduction code is not included.
- Baseline result files used for paper-table consistency checks are stored under
  `final_submission/results/baselines/`.

## References

- HITS: see the upstream HITS repository pinned in `baselines.lock.json`.
- ChatUniTest: see the upstream ChatUniTest repositories pinned in
  `baselines.lock.json`.
- Panta: see the upstream Panta repository pinned in `baselines.lock.json`.
- EvoSuite and Randoop: use the official Defects4J generator and bug-detection
  scripts.
