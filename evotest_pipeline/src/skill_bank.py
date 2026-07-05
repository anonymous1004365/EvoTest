"""SkillBank writer for the EvoTest replication pipeline."""

from __future__ import annotations

from pathlib import Path
import shutil
import yaml

from skill_model import Skill


def write_skill_bank(skills: list[Skill], output_dir: Path | str) -> None:
    if isinstance(output_dir, str):
        output_dir = Path(output_dir)

    bank_dir = output_dir / "skill_bank"
    skills_dir = bank_dir / "skills"
    if skills_dir.exists():
        shutil.rmtree(skills_dir)
    skills_dir.mkdir(parents=True, exist_ok=True)

    model_entries = []
    evolution_entries = []

    for skill in skills:
        skill_id = skill.id or "unknown"
        _write_skill_file(skills_dir / f"{skill_id}.md", skill)

        model_entries.append(
            {
                "name": skill.name,
                "description": skill.description,
                "code_tags": skill.code_tags,
                "test_pattern": skill.test_pattern,
            }
        )

        evolution_entries.append(
            {
                "name": skill.name,
                "focal_class": skill.focal_class,
                "focal_method": skill.focal_method,
                "confidence": skill.confidence,
                "source": {
                    "dataset": skill.source.dataset,
                    "bug_id": skill.source.bug_id,
                    "focal_method_idx": skill.source.focal_method_idx,
                },
            }
        )

    with (bank_dir / "_index_model.yaml").open("w", encoding="utf-8") as f:
        yaml.dump({"skills": model_entries}, f, allow_unicode=True, default_flow_style=False)

    with (bank_dir / "_index_evolution.yaml").open("w", encoding="utf-8") as f:
        yaml.dump({"skills": evolution_entries}, f, allow_unicode=True, default_flow_style=False)

    print(f"Written {len(skills)} skills to {bank_dir}")


def _write_skill_file(path: Path, skill: Skill) -> None:
    lines = [
        "---",
        f"name: {skill.name}",
        f"description: {skill.description}",
        f"code_tags: {skill.code_tags}",
        f"test_pattern: {skill.test_pattern}",
        "---",
        "",
        f"# {skill.name}",
        "",
        "## Instructions",
        "",
        skill.guidance.strip() if skill.guidance else "(no guidance)",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
