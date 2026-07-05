# EvoTest Artifact Package

This package contains the code and lightweight result files needed to inspect
and reproduce the EvoTest experiments reported in the paper.

## Directory Layout

- `evotest_pipeline/`
  - EvoTest implementation for Defects4J generated-suite evaluation, Vanilla
    LLM evaluation, initial SkillBank construction, and GitBug-Java
    training/evolution.
  - `skill_bank/` contains the final evolved SkillBank snapshot used by the
    main EvoTest setting.
- `results/`
  - Lightweight result files.
  - Includes bug-level result tiers for no SkillBank, static SkillBank, and
    evolved SkillBank settings.
  - Includes RQ3 plotting scripts, source data, and generated figures.
- `baseline_references/`
  - Upstream baseline repository references and pinned commits.

## Environment

The scripts expect a Java/Defects4J environment and an OpenAI-compatible LLM
API endpoint. Configure paths outside the repository:

```bash
export EVOTEST_DATA_DIR=/path/to/data
export EVOTEST_OUTPUT_DIR="$EVOTEST_DATA_DIR/output"
export EVOTEST_TMP_DIR="$EVOTEST_DATA_DIR/tmp"
export D4J_HOME="$EVOTEST_DATA_DIR/defects4j"
export D4J_DATASET="$EVOTEST_DATA_DIR/defects4j_dataset.json"
export DEEPSEEK_API_KEY=...
```

## Main EvoTest Evaluation

Run the generated-suite evaluator with the included SkillBank:

```bash
python3 final_submission/evotest_pipeline/scripts/run_defects4j_generated_suite_eval.py \
  --all-bugs \
  --output "$EVOTEST_OUTPUT_DIR/d4j_evotest" \
  --workspace "$EVOTEST_TMP_DIR/d4j_evotest" \
  --skill-bank final_submission/evotest_pipeline/skill_bank \
  --max-attempts 10
```

For parallel execution, run shards with `--num-shards N --shard-index I` and
merge results by bug key.

## Vanilla LLM Evaluation

```bash
python3 final_submission/evotest_pipeline/scripts/run_vanilla_llm_defects4j_eval.py \
  --all-bugs \
  --output "$EVOTEST_OUTPUT_DIR/d4j_vanilla_llm" \
  --workspace "$EVOTEST_TMP_DIR/d4j_vanilla_llm"
```

This setting uses the same focal-method prompt format but disables tools,
SkillBank retrieval, and multi-attempt continuation.

## Initial SkillBank Construction

```bash
python3 final_submission/evotest_pipeline/scripts/build_initial_skillbank.py \
  --input /path/to/static_bug_records.json \
  --out-dir "$EVOTEST_OUTPUT_DIR/initial_skillbank"
```

## GitBug-Java Training and Evolution

```bash
python3 final_submission/evotest_pipeline/scripts/run_gitbug_sequential_training.py \
  --dataset-file /path/to/gitbug_java_cases.json \
  --initial-skill-bank /path/to/initial_skill_bank \
  --output-root "$EVOTEST_OUTPUT_DIR/gitbug_training" \
  --workspace-root "$EVOTEST_TMP_DIR/gitbug_training" \
  --batch-size 50 \
  --epochs 1
```

This workflow runs TG inference on each batch, runs case/global evolution
agents, and overwrites the working SkillBank at
`$EVOTEST_OUTPUT_DIR/gitbug_training/skill_bank` after each evolution step.
Batch logs, case reports, global evolution reports, and operation logs remain
under `$EVOTEST_OUTPUT_DIR/gitbug_training/batches/`.

## Results

See `results/README.md` for the result files. The key bug-level outputs are:

- `results/d4j_no_skillbank_results.json`
- `results/d4j_static_skillbank_results.json`
- `results/d4j_evolved_skillbank_results.json`
