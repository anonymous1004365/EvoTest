---
name: ant-pathmatcher-relative-path-exclude
description: WHEN the TG encounters file filters that use AntPathMatcher with include/exclude
  patterns, THEN it should test with relative paths (without leading slash) to ensure
  the exclude pattern correctly prevents file matching. Common pitfalls include only
  testing with absolute paths or paths starting with a leading '/'.
code_tags:
- BOUNDARY_CHECK
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# ant-pathmatcher-relative-path-exclude

## Instructions

# Ant PathMatcher Relative Path Exclude Filtering

## Instructions

- WHEN the TG encounters code that uses `org.apache.camel.util.AntPathMatcher` to match file paths against include/exclude patterns (e.g., `AntPathMatcherGenericFileFilter` or `AntPathMatcherFileFilter`)
- THEN the TG should write tests that verify both include AND exclude filtering behavior using **relative paths** (i.e., paths without a leading `/`) — not just absolute paths
- Specifically, the test should verify that when a file path like `"sometext/foo.txt"` is checked against:
  - An **include** pattern (e.g., `"**/*.txt"`) → should return `true` (file matches)
  - An **exclude** pattern (e.g., `"sometext/*.txt"`) → should return `false` (file is filtered out)
- **Common pitfall**: Testing only with absolute paths (e.g., `"/sometext/foo.txt"`) which may behave differently from relative paths due to how `AntPathMatcher.matchStrings()` handles leading slashes — always test with relative paths too
- **Another pitfall**: Only testing include but not exclude patterns, or only testing when the filter returns `true`, missing cases where files should be rejected
- The test should verify that adding an exclude pattern to a filter that previously included a file causes the filter to now reject that file, testing the state mutation of the filter's pattern list
- Use concrete examples:
  - Correct: Test `AntPathMatcherGenericFileFilter.accept()` with a relative path `"sometext/foo.txt"`, first with an include pattern `"**/*.txt"` alone (expect `true`), then after adding an exclude pattern `"sometext/*.txt"` (expect `false`)
  - Incorrect: Only testing `accept()` with the include pattern and a path like `"/sometext/foo.txt"` (leading slash), which may accidentally still match even after adding the exclude
- Use assertions that confirm the exact boolean result (e.g., `assertTrue(filter.accept(...))` and `assertFalse(filter.accept(...))`)