"""SkillBank search/read tools for final EvoTest runners.

This module intentionally contains only SkillBank loading, retrieval, and
tool-executor helpers.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover - surfaced at runtime with a clear error
    yaml = None


DEFAULT_SKILL_TOP_K = 10
STOP_TOKENS = {
    "the", "and", "for", "with", "this", "that", "from", "into", "when", "then",
    "java", "junit", "test", "tests", "method", "class", "public", "private",
    "protected", "static", "final", "void", "return", "new", "assert", "true",
    "false", "null", "string", "object", "value", "values", "should", "would",
    "could", "current", "fixed", "version", "generated", "suite", "focal",
}


def _tokenize(text: str) -> list[str]:
    raw = re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}|[0-9]+", text or "")
    tokens: list[str] = []
    for tok in raw:
        pieces = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", tok).replace("_", " ").split()
        tokens.extend(p.lower() for p in pieces if len(p) >= 3 and p.lower() not in STOP_TOKENS)
    return tokens


def _front_matter_and_body(text: str) -> tuple[dict[str, Any], str]:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end >= 0 and yaml is not None:
            raw = text[3:end].strip()
            try:
                meta = yaml.safe_load(raw) or {}
                if isinstance(meta, dict):
                    return meta, text[end + 4 :].lstrip()
            except Exception:
                pass
    return {}, text


def _load_skill_bank(skill_bank_dir: str) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required to load the SkillBank")
    bank_dir = Path(skill_bank_dir)
    skills_dir = bank_dir / "skills"
    index_path = bank_dir / "_index_model.yaml"
    if not bank_dir.exists() or not skills_dir.is_dir():
        raise FileNotFoundError(f"Skill bank not found or missing skills/: {skill_bank_dir}")

    index: dict[str, Any] = {}
    if index_path.exists():
        loaded = yaml.safe_load(index_path.read_text(encoding="utf-8", errors="replace")) or {}
        if isinstance(loaded, dict):
            index = loaded

    tag_registry: Any = None
    tag_registry_path = bank_dir / "code_tag_registry.json"
    if tag_registry_path.exists():
        try:
            tag_registry = json.loads(tag_registry_path.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            tag_registry = None

    index_entries: dict[str, dict[str, Any]] = {}
    for entry in index.get("skills", []) or []:
        if isinstance(entry, dict):
            name = str(entry.get("name") or entry.get("id") or "").strip()
            if name:
                index_entries[name] = entry
            sid = str(entry.get("id") or "").strip()
            if sid:
                index_entries[sid] = entry

    skills: dict[str, dict[str, Any]] = {}
    for path in sorted(skills_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        fm, body = _front_matter_and_body(text)
        display_name = str(
            fm.get("name")
            or fm.get("id")
            or path.stem
        ).strip()
        skill_id = str(fm.get("id") or path.stem).strip() or path.stem
        meta = dict(index_entries.get(skill_id) or index_entries.get(display_name) or {})
        meta.update({k: v for k, v in fm.items() if k not in meta or v})
        meta.setdefault("name", display_name)
        meta.setdefault("id", skill_id)
        meta.setdefault("file", str(path))
        haystack_parts = [
            skill_id,
            str(meta.get("name") or ""),
            str(meta.get("description") or ""),
            str(meta.get("summary") or ""),
            " ".join(str(x) for x in (meta.get("code_tags") or [])),
            " ".join(str(x) for x in (meta.get("tags") or [])),
            str(meta.get("test_pattern") or ""),
            body[:12000],
        ]
        haystack = "\n".join(haystack_parts)
        skills[skill_id] = {
            "name": skill_id,
            "title": str(meta.get("name") or display_name or skill_id),
            "id": skill_id,
            "file": str(path),
            "meta": meta,
            "body": body,
            "token_counts": _counts(_tokenize(haystack)),
        }

    if not skills:
        raise RuntimeError(f"No skills loaded from {skill_bank_dir}")
    print(f"[skill-bank] Loaded {len(skills)} skills from {skill_bank_dir}")
    code_tags = _build_code_tag_index(index, tag_registry, skills)
    if code_tags:
        print(f"[skill-bank] Loaded {len(code_tags)} code tags")
    return {"path": str(bank_dir), "index": index, "skills": skills, "code_tags": code_tags}


def _counts(tokens: list[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for tok in tokens:
        out[tok] = out.get(tok, 0) + 1
    return out


def _build_code_tag_index(index: dict[str, Any], registry: Any, skills: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    tags: dict[str, dict[str, Any]] = {}

    def add_tag(name: str, payload: Any = None) -> None:
        name = str(name or "").strip()
        if not name:
            return
        entry = tags.setdefault(name, {"name": name, "description": "", "count": 0, "skills": []})
        if isinstance(payload, dict):
            entry["description"] = str(
                payload.get("description")
                or payload.get("summary")
                or payload.get("meaning")
                or entry.get("description")
                or ""
            )
            aliases = payload.get("aliases") or payload.get("keywords") or []
            if aliases:
                entry["aliases"] = aliases
        elif isinstance(payload, str):
            entry["description"] = payload

    if isinstance(registry, dict):
        for key, value in registry.items():
            if key in {"tags", "code_tags"} and isinstance(value, (dict, list)):
                if isinstance(value, dict):
                    for tag, payload in value.items():
                        add_tag(tag, payload)
                else:
                    for item in value:
                        if isinstance(item, dict):
                            add_tag(item.get("name") or item.get("tag"), item)
                        else:
                            add_tag(str(item))
            else:
                add_tag(key, value)
    elif isinstance(registry, list):
        for item in registry:
            if isinstance(item, dict):
                add_tag(item.get("name") or item.get("tag"), item)
            else:
                add_tag(str(item))

    for entry in index.get("code_tags", []) or []:
        if isinstance(entry, dict):
            add_tag(entry.get("name") or entry.get("tag"), entry)
        else:
            add_tag(str(entry))

    for skill_name, skill in skills.items():
        meta = skill.get("meta") or {}
        for tag in meta.get("code_tags") or meta.get("tags") or []:
            add_tag(str(tag))
            tags[str(tag)]["count"] = int(tags[str(tag)].get("count") or 0) + 1
            if len(tags[str(tag)]["skills"]) < 20:
                tags[str(tag)]["skills"].append(skill_name)

    return tags


def _list_code_tags(bank: dict[str, Any], *, offset: int = 0, limit: int = 80, sort_by: str = "count") -> dict[str, Any]:
    rows = list((bank.get("code_tags") or {}).values())
    if sort_by == "name":
        rows.sort(key=lambda entry: str(entry.get("name") or ""))
    else:
        rows.sort(key=lambda entry: (-int(entry.get("count") or 0), str(entry.get("name") or "")))
    offset = max(0, int(offset))
    limit = max(1, min(200, int(limit)))
    page = rows[offset : offset + limit]
    return {
        "total": len(rows),
        "offset": offset,
        "limit": limit,
        "sort_by": sort_by,
        "code_tags": [
            {
                "name": entry.get("name"),
                "description": entry.get("description") or "",
                "count": entry.get("count") or 0,
                "example_skills": (entry.get("skills") or [])[:8],
            }
            for entry in page
        ],
    }


def _compact_skill_row(skill: dict[str, Any], score: float) -> dict[str, Any]:
    meta = skill.get("meta") or {}
    body = str(skill.get("body") or "")
    return {
        "name": skill.get("name"),
        "title": skill.get("title") or (skill.get("meta") or {}).get("name") or "",
        "score": round(score, 3),
        "description": meta.get("description") or meta.get("summary") or "",
        "code_tags": meta.get("code_tags") or meta.get("tags") or [],
        "test_pattern": meta.get("test_pattern") or "",
        "preview": re.sub(r"\s+", " ", body[:500]).strip(),
    }


def _score_skill(skill: dict[str, Any], query_tokens: list[str], query: str) -> float:
    counts = skill.get("token_counts") or {}
    if not query_tokens:
        return 0.0
    score = 0.0
    unique = set(query_tokens)
    for tok in unique:
        if tok in counts:
            score += 1.0 + min(4, counts[tok])
    meta = skill.get("meta") or {}
    name_text = " ".join(_tokenize(str(meta.get("name") or skill.get("name") or "")))
    desc_text = " ".join(_tokenize(str(meta.get("description") or meta.get("summary") or "")))
    tag_text = " ".join(_tokenize(" ".join(str(x) for x in (meta.get("code_tags") or meta.get("tags") or []))))
    pattern_text = " ".join(_tokenize(str(meta.get("test_pattern") or "")))
    for tok in unique:
        if tok in name_text:
            score += 6.0
        if tok in desc_text:
            score += 3.0
        if tok in tag_text:
            score += 2.0
        if tok in pattern_text:
            score += 4.0
        title = str(skill.get("title") or "").lower()
        desc = str(meta.get("description") or meta.get("summary") or "").lower()
        if len(tok) >= 4 and (tok in title or tok in desc):
            score += 2.0
    phrase = query.lower().strip()
    if phrase and len(phrase) >= 6:
        body = str(skill.get("body") or "").lower()
        if phrase in body:
            score += 8.0
    return score


def _search_code_tags(bank: dict[str, Any], query: str, *, top_k: int) -> list[dict[str, Any]]:
    query_tokens = _tokenize(query)
    rows: list[tuple[float, str, dict[str, Any]]] = []
    for name, entry in (bank.get("code_tags") or {}).items():
        text = " ".join([
            name,
            str(entry.get("description") or ""),
            " ".join(str(x) for x in (entry.get("aliases") or [])),
        ])
        counts = _counts(_tokenize(text))
        score = 0.0
        for tok in set(query_tokens):
            if tok in counts:
                score += 4.0 * counts[tok]
            if tok in name.lower():
                score += 6.0
        if query.strip().lower() == name.lower():
            score += 50.0
        if score > 0:
            rows.append((score, name, entry))
    rows.sort(key=lambda item: (-item[0], item[1]))
    return [
        {
            "name": name,
            "score": round(score, 3),
            "description": entry.get("description") or "",
            "count": entry.get("count") or 0,
            "example_skills": entry.get("skills") or [],
        }
        for score, name, entry in rows[: max(1, top_k)]
    ]


def _skills_for_code_tags(
    bank: dict[str, Any],
    code_tags: list[str],
    *,
    top_k: int,
    exclude_bug_key: str = "",
) -> list[dict[str, Any]]:
    wanted = {str(tag).strip().lower() for tag in code_tags if str(tag).strip()}
    exclude_norm = exclude_bug_key.lower().replace("-", "_")
    rows: list[tuple[float, str, dict[str, Any]]] = []
    for name, skill in (bank.get("skills") or {}).items():
        if exclude_norm and exclude_norm in str(name).lower().replace("-", "_"):
            continue
        tags = {
            str(tag).strip().lower()
            for tag in ((skill.get("meta") or {}).get("code_tags") or (skill.get("meta") or {}).get("tags") or [])
            if str(tag).strip()
        }
        hits = wanted & tags
        if hits:
            rows.append((20.0 * len(hits), name, skill))
    rows.sort(key=lambda item: (-item[0], item[1]))
    return [_compact_skill_row(skill, score) for score, _name, skill in rows[: max(1, top_k)]]


def _focal_query(record: dict[str, Any], focal_source: str, current_code: str, previous_context: str) -> str:
    parts = [
        str(record.get("project") or ""),
        str(record.get("class_name") or record.get("focal_class") or ""),
        str(record.get("method_name") or record.get("focal_method") or ""),
        focal_source[:12000],
        current_code[:6000],
        previous_context[-5000:],
    ]
    return "\n".join(parts)


def _search_skills(
    bank: dict[str, Any],
    query: str,
    *,
    top_k: int,
    exclude_bug_key: str = "",
    code_tags: list[str] | None = None,
) -> list[dict[str, Any]]:
    query_tokens = _tokenize(query)
    wanted_tags = {str(tag).strip().lower() for tag in (code_tags or []) if str(tag).strip()}
    if not wanted_tags and query_tokens:
        inferred = _search_code_tags(bank, " ".join(query_tokens[:60]), top_k=12)
        wanted_tags = {str(row.get("name") or "").strip().lower() for row in inferred[:6] if row.get("name")}
    scored: list[tuple[float, str, dict[str, Any]]] = []
    exclude_norm = exclude_bug_key.lower().replace("-", "_")
    for name, skill in (bank.get("skills") or {}).items():
        if exclude_norm and exclude_norm in str(name).lower().replace("-", "_"):
            continue
        score = _score_skill(skill, query_tokens, query)
        skill_tags = {
            str(tag).strip().lower()
            for tag in ((skill.get("meta") or {}).get("code_tags") or (skill.get("meta") or {}).get("tags") or [])
            if str(tag).strip()
        }
        tag_hits = sorted(wanted_tags & skill_tags)
        if tag_hits:
            score += 12.0 * len(tag_hits)
        if score > 0:
            scored.append((score, name, skill))
    scored.sort(key=lambda item: (-item[0], item[1]))
    rows = [_compact_skill_row(skill, score) for score, _name, skill in scored[: max(1, top_k)]]
    if len(rows) >= min(top_k, 3):
        return rows

    seen = {str(row.get("name") or "") for row in rows}
    fallback_tags = [str(tag) for tag in wanted_tags]
    fallback_rows = _skills_for_code_tags(bank, fallback_tags, top_k=top_k, exclude_bug_key=exclude_bug_key)
    for row in fallback_rows:
        if str(row.get("name") or "") not in seen:
            row["score"] = max(float(row.get("score") or 0.0), 1.0)
            row["fallback"] = "code_tag"
            rows.append(row)
            seen.add(str(row.get("name") or ""))
        if len(rows) >= top_k:
            return rows

    # Last-resort recall: return skills from the most populated tags so the
    # agent can still inspect the bank instead of seeing an empty result.
    popular_tags = [
        str(entry.get("name") or "")
        for entry in sorted((bank.get("code_tags") or {}).values(), key=lambda e: (-int(e.get("count") or 0), str(e.get("name") or "")))
        if entry.get("name")
    ][:8]
    for row in _skills_for_code_tags(bank, popular_tags, top_k=top_k, exclude_bug_key=exclude_bug_key):
        if str(row.get("name") or "") not in seen:
            row["score"] = max(float(row.get("score") or 0.0), 0.5)
            row["fallback"] = "popular_code_tag"
            rows.append(row)
            seen.add(str(row.get("name") or ""))
        if len(rows) >= top_k:
            break
    return rows


def _skill_tool_specs() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "list_skills",
                "description": "List the top SkillBank skills retrieved for this focal context.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "search_skills",
                "description": (
                    "Search the SkillBank by keywords and optional code tags. "
                    "Use behavior, API, exception, parser, boundary, state, or data-structure keywords."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Keywords or a short phrase describing the suspected bug behavior/path.",
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of skill summaries to return.",
                            "default": DEFAULT_SKILL_TOP_K,
                        },
                        "code_tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional code tags found through search_code_tags.",
                        },
                    },
                    "required": ["query"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "search_code_tags",
                "description": "Search SkillBank code tags by keyword before searching skills.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Keyword or behavior to map to code tags."},
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of code tags to return.",
                            "default": 20,
                        },
                    },
                    "required": ["query"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_code_tags",
                "description": (
                    "Browse the complete skillbank_tools code-tag vocabulary with pagination. "
                    "Use this when keyword search misses relevant tags."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "offset": {"type": "integer", "description": "Start offset in the tag list.", "default": 0},
                        "limit": {"type": "integer", "description": "Page size, capped at 200.", "default": 80},
                        "sort_by": {
                            "type": "string",
                            "enum": ["count", "name"],
                            "description": "Sort by frequency count or alphabetically.",
                            "default": "count",
                        },
                    },
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_skills_by_code_tags",
                "description": "Return skills associated with one or more exact skillbank_tools code tags.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code_tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Exact code tag names from list_code_tags/search_code_tags.",
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of skills to return.",
                            "default": DEFAULT_SKILL_TOP_K,
                        },
                    },
                    "required": ["code_tags"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_skill",
                "description": "Read the full content of one SkillBank skill by name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Skill name from list_skills/search_skills."}
                    },
                    "required": ["name"],
                    "additionalProperties": False,
                },
            },
        },
    ]


def _make_skill_executor(
    bank: dict[str, Any],
    initial_candidates: list[dict[str, Any]],
    *,
    top_k: int,
    exclude_bug_key: str,
    read_log: list[str],
) -> Any:
    def _exec(name: str, args: dict[str, Any]) -> str | None:
        if name == "list_skills":
            return json.dumps({"skills": initial_candidates}, ensure_ascii=False, indent=2, default=str)
        if name == "search_skills":
            query = str(args.get("query") or "")
            max_results = int(args.get("max_results") or top_k)
            max_results = max(1, min(30, max_results))
            code_tags = [str(x) for x in (args.get("code_tags") or [])]
            rows = _search_skills(
                bank,
                query,
                top_k=max_results,
                exclude_bug_key=exclude_bug_key,
                code_tags=code_tags,
            )
            return json.dumps({"query": query, "skills": rows}, ensure_ascii=False, indent=2, default=str)
        if name == "search_code_tags":
            query = str(args.get("query") or "")
            max_results = int(args.get("max_results") or 20)
            max_results = max(1, min(80, max_results))
            rows = _search_code_tags(bank, query, top_k=max_results)
            return json.dumps({"query": query, "code_tags": rows}, ensure_ascii=False, indent=2, default=str)
        if name == "list_code_tags":
            offset = int(args.get("offset") or 0)
            limit = int(args.get("limit") or 80)
            sort_by = str(args.get("sort_by") or "count")
            return json.dumps(_list_code_tags(bank, offset=offset, limit=limit, sort_by=sort_by), ensure_ascii=False, indent=2, default=str)
        if name == "get_skills_by_code_tags":
            tags = [str(x) for x in (args.get("code_tags") or [])]
            max_results = int(args.get("max_results") or top_k)
            max_results = max(1, min(50, max_results))
            rows = _skills_for_code_tags(bank, tags, top_k=max_results, exclude_bug_key=exclude_bug_key)
            return json.dumps({"code_tags": tags, "skills": rows}, ensure_ascii=False, indent=2, default=str)
        if name == "read_skill":
            wanted = str(args.get("name") or "").strip()
            skills = bank.get("skills") or {}
            skill = skills.get(wanted)
            if skill is None:
                lowered = wanted.lower()
                for skill_name, candidate in skills.items():
                    title = str(candidate.get("title") or (candidate.get("meta") or {}).get("name") or "")
                    if (
                        skill_name.lower() == lowered
                        or str(candidate.get("id") or "").lower() == lowered
                        or title.lower() == lowered
                    ):
                        skill = candidate
                        wanted = skill_name
                        break
            if skill is None:
                return f"Error: skill not found: {wanted}"
            read_log.append(wanted)
            meta = skill.get("meta") or {}
            body = str(skill.get("body") or "")
            payload = {
                "name": skill.get("name"),
                "title": skill.get("title") or meta.get("name") or "",
                "description": meta.get("description") or meta.get("summary") or "",
                "code_tags": meta.get("code_tags") or meta.get("tags") or [],
                "test_pattern": meta.get("test_pattern") or "",
                "content": body[:12000],
            }
            if len(body) > 12000:
                payload["truncated"] = True
                payload["note"] = "Skill content truncated to 12000 characters."
            return json.dumps(payload, ensure_ascii=False, indent=2, default=str)
        return None

    return _exec
