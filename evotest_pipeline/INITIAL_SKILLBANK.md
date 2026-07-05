# Initial SkillBank Construction

The final pipeline exposes one public builder for the initial SkillBank:

```bash
export EVOTEST_DATA_DIR=/data
export EVOTEST_OUTPUT_DIR=/data/output
export EVOTEST_TMP_DIR=/data/tmp
export LLM_API_KEY=...
export LLM_API_URL=https://api.deepseek.com
export SKILL_MODEL=deepseek-chat

python scripts/build_initial_skillbank.py \
  --input /data/output/focal_method_dataset_static_nongitbug.json \
  --out-dir /data/output/initial_skillbank \
  --workers 8 \
  --max-steps-s1 80 \
  --max-steps-s2 100 \
  --compress-every-s1 10 \
  --compress-every-s2 15 \
  --timeout 240 \
  --max-retries 1 \
  --finalize-rounds 1 \
  --resume
```

The builder:

1. processes each non-evaluation focal-method record;
2. runs fixed-version Phase A to select code tags and test-pattern metadata;
3. extracts one candidate skill from static bug/fix/test evidence;
4. applies parser normalization to well-formed skills embedded in noisy model
   outputs;
5. retries unresolved records for a bounded number of rounds;
6. writes the finalized `skill_bank/`.

GitBug-Java rows are excluded by the shared loader because GitBug-Java is used
for later training/evolution, not for the static bootstrap bank.

## Input Contract

The builder expects a focal-method dataset JSON with either a top-level
`focal_methods` array or a plain array.

Recommended fields:

- `dataset`, `bug_id`, `project`;
- `focal_class`, `focal_method`, `focal_method_sig`, `focal_file`;
- `fixed_code`, `buggy_code`, `diff`;
- `failing_test_class`, `failing_test_method`, `test_patch`;
- `clone_url`, `buggy_version`, `fixed_version`.

If `clone_url` is present, code tools can checkout the repository versions.  If
only inline `fixed_code`/`buggy_code` snippets are present, the builder
materializes a minimal checkout for the focal file so read/search tools still
work.

## Output Contract

The finalized output directory contains:

- `skill_bank/skills/*.md`;
- `skills_latest.json`;
- `summary.jsonl`;
- `progress.json`;
- `code_tags_registry.json`;
- `build_report.json`;
- `DONE` when all rows are resolved.

For auditability, first-pass evidence is retained under:

```text
<out-dir>/internal/first_pass/
```

This internal directory includes first-pass trajectories and records.  It is not
a separate user-facing step.

Do not overwrite the finalized initial SkillBank.  For sequential training,
copy it into the training output directory as the working `skill_bank/`; each
evolution step updates that working SkillBank in place while preserving the
per-batch reports and operation logs.
