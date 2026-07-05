"""Central path configuration for the final EvoTest pipeline.

All paths are resolved from EVOTEST_DATA_DIR by default.  The older
SKILL_MINING_DATA/SKILL_MINING_OUTPUT variables are also accepted for backward
compatibility with historical experiment commands.

Directory layout:
    $EVOTEST_DATA_DIR/
    ├── datasets/
    │   ├── gitbug-java/       # GitBug-Java repo clone
    │   ├── bears-benchmark/   # Bears repo clone
    │   └── bugs-dot-jar/      # Bugs.jar repo clone (with submodules)
    ├── cache/
    │   └── gitbug-repos/      # Cloned external repos for GitBug-Java
    ├── workspaces/            # Temporary git checkout workspaces
    └── output/                # Pipeline output (SkillBank, trajectories, etc.)
"""

import os
from pathlib import Path

# Base data directory
DATA_ROOT = Path(
    os.environ.get(
        "EVOTEST_DATA_DIR",
        os.environ.get("SKILL_MINING_DATA", "data"),
    )
)
TMP_ROOT = Path(os.environ.get("EVOTEST_TMP_DIR", str(DATA_ROOT / "tmp")))

# Dataset repos
GITBUG_REPO = Path(os.environ.get("GITBUG_REPO", str(DATA_ROOT / "datasets" / "gitbug-java")))
BEARS_REPO = Path(os.environ.get("BEARS_REPO", str(DATA_ROOT / "datasets" / "bears-benchmark")))
BUGSJAR_ROOT = Path(os.environ.get("BUGSJAR_ROOT", str(DATA_ROOT / "datasets" / "bugs-dot-jar")))

# Cache for cloned external repos (GitBug-Java needs to clone each project's repo)
GITBUG_CACHE = Path(os.environ.get("GITBUG_CACHE", str(DATA_ROOT / "cache" / "gitbug-repos")))

# Temporary workspaces for git checkouts during skill extraction
WORKSPACE_ROOT = Path(os.environ.get("WORKSPACE_ROOT", str(TMP_ROOT / "workspaces")))

# Git cache for skill agent
GIT_CACHE = Path(os.environ.get("GIT_CACHE", str(DATA_ROOT / "cache" / "git")))

# Output directory
OUTPUT_ROOT = Path(
    os.environ.get(
        "EVOTEST_OUTPUT_DIR",
        os.environ.get("SKILL_MINING_OUTPUT", str(DATA_ROOT / "output")),
    )
)
