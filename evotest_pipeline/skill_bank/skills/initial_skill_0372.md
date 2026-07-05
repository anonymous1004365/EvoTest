---
name: regex-pattern-null-and-empty-handling
description: Teaches how to test RegExFilter for proper null/empty handling when building
  regex patterns from user options. Useful when writing tests for iterator configurations
  that accept optional regex match options like rowRegex, colfRegex, colqRegex, or
  valueRegex.
code_tags:
- ARGUMENT_VALIDATION
- NULL_CHECK
- BOUNDARY_CHECK
- REGEX_PATTERN_VALIDATION
test_pattern: EXCEPTION_TEST
---

# regex-pattern-null-and-empty-handling

## Instructions

# Regex Filter Pattern Null and Empty Handling

## Instructions

### WHEN the TG encounters a class that compiles `java.util.regex.Pattern` from optional options (e.g., options like "rowRegex", "colfRegex", "colqRegex", "valueRegex") that can be `null` or `""` (empty string)

- **THEN** the TG should write a test that validates:
  1. When an option is set to an empty string `""`, the iterator should NOT throw a `java.util.regex.PatternSyntaxException` during initialization.
  2. When an option is `null` (not set in the options map), the iterator should initialize without error.
  3. When an option contains an INVALID regex pattern (e.g., `"["`, `"*"`, `"\\"`), the iterator should throw a `java.util.regex.PatternSyntaxException`.

### Common pitfalls to avoid:
- **Pitfall 1**: Only testing one case (e.g., only null, only empty, or only valid regex). The TG must test ALL boundary cases: null, empty string, valid regex, and invalid regex.
- **Pitfall 2**: Assuming empty string is treated the same as null. The code may have different code paths for each (e.g., `null` may skip compilation entirely, while `""` may attempt `Pattern.compile("")`).
- **Pitfall 3**: Forgetting that the failure mode is a `PatternSyntaxException` thrown during `deepCopy` or `init` — the test must catch or expect this exception.
- **Pitfall 4**: Checking only rowRegex — the same issue applies to ALL regex options (colfRegex, colqRegex, valueRegex). A thorough test should cover each.

### Correct example approach:
```java
// Test that empty string does not throw PatternSyntaxException
@Test
public void testEmptyRowRegex() throws IOException {
  SortedKeyValueIterator<Key,Value> source = ...;
  RegExFilter filter = new RegExFilter();
  filter.init(source, Map.of("rowRegex", ""), new DefaultIteratorEnvironment());
  // Should complete without PatternSyntaxException
}

// Test that null regex does not throw PatternSyntaxException
@Test
public void testNullRowRegex() throws IOException {
  SortedKeyValueIterator<Key,Value> source = ...;
  RegExFilter filter = new RegExFilter();
  filter.init(source, Map.of("rowRegex", (String) null), new DefaultIteratorEnvironment());
  // Should complete without PatternSyntaxException
}

// Test that invalid regex throws PatternSyntaxException
@Test(expected = PatternSyntaxException.class)
public void testInvalidRowRegex() throws IOException {
  SortedKeyValueIterator<Key,Value> source = ...;
  RegExFilter filter = new RegExFilter();
  filter.init(source, Map.of("rowRegex", "["), new DefaultIteratorEnvironment());
}
```

### Incorrect example approach (what NOT to do):
```java
// ❌ BAD: Only tests one case, misses empty/null boundary
@Test
public void testRowRegexOnly() {
  RegExFilter filter = new RegExFilter();
  filter.init(source, Map.of("rowRegex", "abc.*"));
  // This only tests valid regex — does NOT catch the null/empty bug
}

// ❌ BAD: Catches Exception too broadly, misses PatternSyntaxException specifically
@Test
public void testEmptyRegex() {
  try {
    filter.init(source, Map.of("rowRegex", ""), env);
  } catch (Exception e) {
    // Wrong: should have passed without exception
    Assert.fail();
  }
}
```