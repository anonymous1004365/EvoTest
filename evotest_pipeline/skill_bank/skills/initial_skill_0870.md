---
name: trailing-whitespace-local-name-validation
description: When validating JCR local names, ensure that names with trailing whitespace
  are rejected as invalid. The TG should test that Namespaces.isValidLocalName() returns
  false for local names ending with whitespace characters.
code_tags:
- NULL_CHECK
- STATE_COMPARISON
test_pattern: EXCEPTION_TEST
---

# trailing-whitespace-local-name-validation

## Instructions

# Trailing Whitespace in JCR Local Name Validation

## Instructions

- WHEN the TG encounters code that validates JCR local names or prefixes (e.g., `Namespaces.isValidLocalName(String)` or `Namespaces.isValidPrefix(String)`), especially in conjunction with `NameValidator`
- THEN the TG must test that names with trailing whitespace characters (spaces, tabs, newlines) are correctly rejected as invalid
  - Specifically, test that a local name like `"excerpt "` (with a trailing space) calls `Namespaces.isValidLocalName()` and expects a `CommitFailedException` from `NameValidator`
  - Also test that local names with leading whitespace are still rejected (already covered) and that names with only whitespace are rejected
  - The TG should use `assertThrows(CommitFailedException.class, () -> root.getTree("/test").addChild("excerpt "))` or similar to verify the exception is thrown
- Common pitfalls:
  - Testing only empty strings or null inputs but not trailing whitespace in an otherwise valid-looking name
  - Testing only prefix validation while ignoring local name validation paths
  - Assuming validation is done purely via regex without checking edge cases like trailing whitespace

### Example (Correct)
```java
// Test that trailing whitespace in local name is rejected
assertThrows(CommitFailedException.class, () -> {
    Tree test = root.getTree("/test");
    test.addChild("excerpt ");
    root.commit();
});
```

### Example (Incorrect — too narrow)
```java
// BAD: Only checks empty string, not trailing whitespace
assertThrows(CommitFailedException.class, () -> {
    Tree test = root.getTree("/test");
    test.addChild("");
    root.commit();
});
```