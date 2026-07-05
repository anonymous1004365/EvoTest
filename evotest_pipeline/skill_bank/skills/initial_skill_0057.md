---
name: fulltext-term-dot-character-filtering
description: When testing full-text search queries that involve terms containing dots
  (e.g., filenames like "file.txt"), the TG should verify that the dot character ('.')
  is NOT filtered out by `FullTextTerm.isFullTextCharacter()`. The bug occurs because
  '.' is accidentally stripped in buggy code, causing `jcr:contains(., 'file.txt')`
  queries to match nothing. This skill helps test that characters with special meaning
  in filenames survive the full-text term filtering pipeline.
code_tags:
- ARGUMENT_VALIDATION
- NULL_CHECK
- SAFE_COPY
- FULLTEXT_CHARACTER_FILTERING
test_pattern: PARAMETRIC_TEST
---

# fulltext-term-dot-character-filtering

## Instructions

# Full-Text Term Dot Character Filtering

## Instructions

- WHEN the TG encounters code in `FullTextTerm`'s constructor that filters characters using `isFullTextCharacter(c) || " +-:&/.".indexOf(c) >= 0` — specifically the dot character ('.') in the string `" +-:&/."`
- THEN the TG should write a test that creates `FullTextTerm` instances with text containing dots (e.g., `"file.txt"`, `"document.v2.final"`) and verify that:
  1. The `filteredText` field retains the dot character (e.g., `"file.txt"` remains `"file.txt"`)
  2. The `evaluate()` method correctly matches strings containing the dotted term
  3. A full end-to-end JCR query using `jcr:contains(., 'term.with.dots')` returns results for nodes whose names or properties match

- WHEN the TG is writing integration tests for `TraversingIndex` or `FullTextSearchImpl` with dotted full-text terms
- THEN the TG should use `TraversingIndexQueryTest` patterns: create child nodes with dotted names (e.g., `c.addChild("testFullTextTermNameFile.txt")`), commit the tree, and assert that `jcr:contains(., 'testFullTextTermNameFile.txt')` queries return exactly one result with the correct path

- Common pitfalls to avoid:
  - **Pitfall**: Testing only with simple alphanumeric terms (e.g., `"test123"`) — this misses the dot-character filtering bug entirely
  - **Pitfall**: Testing `FullTextTerm` in isolation but forgetting that the dot may also be filtered in upstream code like `FullTextSearchImpl.evaluate()` or `FullTextParser` — verify the full pipeline
  - **Pitfall**: Only testing the `evaluate()` method but not the `indexOf(filteredText)` logic — the bug may manifest as `filteredText` being correctly constructed but the evaluation incorrectly failing
  - **Pitfall**: Using `@Ignore("OAK-2050")` on the test — ensure the test is NOT ignored if the fix for OAK-2050 is being verified

### Correct Example (what the TG should write)

```java
// Test that dots in full-text search terms are preserved
@Test
public void testFullTextTermWithDot() throws Exception {
    Tree c = root.getTree("/").addChild("content");
    c.addChild("testFile.txt");
    c.addChild("simpleName");
    root.commit();
    
    // Query for a name containing a dot — should match exactly one node
    assertQuery("//*[jcr:contains(., 'testFile.txt')]",
            "xpath",
            ImmutableList.of("/content/testFile.txt"));
    
    // Query for a simple name without dots — should still work
    assertQuery("//*[jcr:contains(., 'simpleName')]",
            "xpath",
            ImmutableList.of("/content/simpleName"));
}
```

### Incorrect Example (common mistake)

```java
// BAD: Only tests simple alphanumeric terms, missing the dot-filtering bug
@Test
public void testFullTextTerm() throws Exception {
    Tree node = root.getTree("/").addChild("content");
    node.setProperty("jcr:mimeType", "text/plain");
    root.commit();
    // Only tests '/' character, does NOT test '.' in filenames
    assertQuery("//*[jcr:contains(., 'text/plain')]", "xpath",
            ImmutableList.of("/content"));
}
```