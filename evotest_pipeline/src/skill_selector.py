"""
Skill selection based on CodeProfile tags and test_pattern.

Based on the matching policy from the design document:
- Double match (code_tags overlap and test_pattern match) has the highest priority.
- Code-tag overlap provides the next priority.
- test_pattern-only matches receive the lowest priority.
- Return top-K candidates; TG decides which ones to load.
"""

from __future__ import annotations

from typing import Optional
from skill_model import Skill, SkillSource


def match_skills(
    profile_tags: set[str],
    profile_pattern: str,
    skills: list[Skill],
    max_return: int = 20,
    exclude_bug_id: str = "",
) -> list[tuple[Skill, float]]:
    """
    Rule-based preselection using code_tags and test_pattern.

    Matching priority:
    1. Double match (code_tags overlap and test_pattern match): tag_overlap + 2.0 bonus
    2. code_tags-only match: tag_overlap
    3. test_pattern-only match: 0.5

    Args:
        profile_tags: code_tags inferred by CodeProfile
        profile_pattern: test_pattern inferred by CodeProfile
        skills: all skills in the SkillBank
        max_return: maximum number of candidates to return
        exclude_bug_id: bug id to exclude for source masking

    Returns:
        List of (skill, score) pairs sorted by descending score.
    """
    scored: list[tuple[Skill, float]] = []

    for skill in skills:
        # Skill masking: exclude skills from the current bug.
        if exclude_bug_id and skill.source.bug_id == exclude_bug_id:
            continue

        skill_tags = set(skill.code_tags)
        tag_overlap = len(skill_tags & profile_tags)

        if tag_overlap > 0 and skill.test_pattern == profile_pattern:
            # Double match: tag_overlap + 2.0 bonus.
            score = tag_overlap + 2.0
        elif tag_overlap > 0:
            # code_tags-only match: tag_overlap; larger is more relevant.
            score = float(tag_overlap)
        elif skill.test_pattern == profile_pattern:
            # test_pattern-only match: base score.
            score = 0.5
        else:
            # No match; discard.
            continue

        scored.append((skill, score))

    # Sort by descending score.
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:max_return]


def select_skills(
    code_tags: set[str],
    test_pattern: str,
    skills: list[Skill],
    max_selected: int = 10,
) -> list[str]:
    """
    Return top-K skill names for TG to choose from.

    Simplified match_skills wrapper that returns skill names instead of (skill, score) pairs.

    Args:
        code_tags: code_tags inferred by CodeProfile
        test_pattern: test_pattern inferred by CodeProfile
        skills: all skills in the SkillBank
        max_selected: maximum number of skill names to return

    Returns:
        Skill names sorted by relevance.
    """
    matched = match_skills(code_tags, test_pattern, skills, max_return=max_selected)
    return [skill.name for skill, _ in matched]


def load_skill_bank(bank_dir: str) -> list[Skill]:
    """
    Load all skills from a skill_bank directory.

    Read _index_model.yaml to obtain L1 metadata for all skills.
    Skill details (L2 guidance) are loaded by the caller on demand.

    Args:
        bank_dir: path to the skill_bank directory

    Returns:
        List of all skills.
    """
    import yaml
    from pathlib import Path

    bank_path = Path(bank_dir)
    index_path = bank_path / "_index_model.yaml"

    if not index_path.exists():
        return []

    with open(index_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Load the evolution index to obtain source information for skill masking.
    evolution_index_path = bank_path / "_index_evolution.yaml"
    source_map: dict[str, dict] = {}  # name -> {dataset, bug_id, focal_method_idx}
    if evolution_index_path.exists():
        with open(evolution_index_path, encoding="utf-8") as f:
            evo_data = yaml.safe_load(f) or {}
        for evo_entry in evo_data.get("skills", []):
            src = evo_entry.get("source", {})
            if src:
                source_map[evo_entry["name"]] = src

    skills = []
    for entry in data.get("skills", []):
        src = source_map.get(entry["name"], {})
        skills.append(Skill(
            id=entry["name"],  # Use the skill name as the id.
            name=entry["name"],
            description=entry["description"],
            guidance="",  # L2 guidance is loaded on demand.
            code_tags=entry.get("code_tags", []),
            test_pattern=entry.get("test_pattern", "STATE_TEST"),
            focal_class="",  # Not present in the L1 index.
            focal_method="",
            focal_method_sig="",
            confidence=0.8,  # Default value.
            source=SkillSource(
                dataset=src.get("dataset", ""),
                bug_id=src.get("bug_id", ""),
                focal_method_idx=src.get("focal_method_idx", 0),
            ),
        ))

    return skills


def filter_by_pattern(
    skills: list[Skill],
    test_pattern: str,
) -> list[Skill]:
    """Keep only skills with the specified test_pattern."""
    return [s for s in skills if s.test_pattern == test_pattern]


def filter_by_tags(
    skills: list[Skill],
    required_tags: set[str],
    min_overlap: int = 1,
) -> list[tuple[Skill, int]]:
    """
    Keep only skills whose code_tags overlap required_tags by at least min_overlap.

    Args:
        skills: list of skills
        required_tags: required tag set
        min_overlap: minimum required overlap, default 1

    Returns:
        List of (skill, overlap_count) pairs sorted by descending overlap.
    """
    result = []
    for skill in skills:
        overlap = len(set(skill.code_tags) & required_tags)
        if overlap >= min_overlap:
            result.append((skill, overlap))

    result.sort(key=lambda x: x[1], reverse=True)
    return result
