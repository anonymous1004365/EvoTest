---
name: bug-data-json-lookup-by-key
description: When code looks up bug data from a JSON configuration file using a bug
  ID or index, test that the lookup logic correctly handles case sensitivity, key
  format mismatches, and returns the correct value even when the input uses a slightly
  different format than the stored keys.
code_tags:
- BEARS_BUG_DATA_LOOKUP
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# bug-data-json-lookup-by-key

## Instructions

# Bug Data JSON Lookup by Key

## Instructions

- WHEN the TG encounters code that reads bug metadata from a JSON file (like `bug_id_and_branch.json`) and looks up entries by an identifier key (e.g., `bugId`),
- THEN the TG should write a parametric test that iterates over ALL entries in the JSON data and verifies that **each entry is correctly found and returned** by the lookup function. Specifically:
  - Test that every `bugId` string in the JSON file can be successfully looked up and returns the corresponding `bugBranch`.
  - Test that the lookup is **case-sensitive** (e.g., `"Bears-1"` vs `"bears-1"` should NOT match).
  - Test that a **non-existent ID** returns a specific sentinel value (e.g., `None`, empty string, or raises an exception).
  - Include the actual bug IDs from the JSON file as test parameters, not just synthetic data.
- Common pitfalls to avoid:
  - ❌ Testing only with a single hardcoded ID instead of parameterizing over all IDs in the data.
  - ❌ Assuming the lookup is case-insensitive or does any key normalization.
  - ❌ Not testing the boundary case where the lookup key uses a slightly different format (e.g., different prefix capitalization, different separator).

### Correct Example (Abstract)
```python
# Given bug_data = [{"bugId": "Bears-1", "bugBranch": "some-branch"}, ...]
def test_lookup_all_ids():
    for entry in bug_data:
        result = lookup(entry["bugId"])
        assert result == entry["bugBranch"], f"Failed for {entry['bugId']}"

def test_lookup_case_sensitive():
    assert lookup("bears-1") is None  # not "Bears-1"
    assert lookup("BEARS-1") is None

def test_lookup_nonexistent():
    assert lookup("NonExistent-999") is None
```

### Incorrect Example (Abstract)
```python
# ❌ Only tests one ID, misses others
def test_lookup():
    assert lookup("Bears-1") == "some-branch"
    # Other IDs like Bears-2, Bears-3... are never tested
```

### Test Pattern
Use a **PARAMETRIC_TEST** (parameterized test) with the actual bug IDs extracted from the JSON configuration file as parameters. The test should verify the exact string returned by the lookup function matches the expected value from the JSON data for every entry.