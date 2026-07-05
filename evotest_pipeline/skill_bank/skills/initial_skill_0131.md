---
name: non-numeric-version-string-exception
description: WHEN parsing version strings that contain non-numeric characters in numeric
  fields, THEN the test generator should verify that a NumberFormatException is properly
  thrown rather than silently swallowing it. This skill helps catch bugs where version
  parsing code fails to validate numeric version segments.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# non-numeric-version-string-exception

## Instructions

# Version String Numeric Validation

## Instructions

- WHEN the TG encounters code that parses a version string (e.g., `DefaultArtifactVersion`, `ComparableVersion`, or any version parsing logic) and extracts individual segments/components (e.g., major, minor, incremental, build number) by splitting on delimiters like ".", "-", or "_", and attempts to parse them as integers (e.g., `Integer.parseInt(...)` or equivalent)
- THEN the TG MUST write an exception test that:
  1. Creates a version string that contains non-numeric characters within a segment that is expected to be numeric (e.g., `"1.0.abc"`, `"2.3-beta"` where `beta` appears in a position parsed as an integer, or `"1.0.0-SNAPSHOT"` where `SNAPSHOT` is placed in a numeric slot)
  2. Constructs the version object (e.g., `new DefaultArtifactVersion(nonNumericVersion)`)
  3. Asserts that construction throws `NumberFormatException` (using `assertThrows(NumberFormatException.class, ...)`)
  4. Verifies the exception type is specifically `NumberFormatException`, not a generic `RuntimeException` or other broader type
- WHEN the version parsing class has getter methods (e.g., `getMajorVersion()`, `getMinorVersion()`, `getIncrementalVersion()`, `getBuildNumber()`, `getQualifier()`)
- THEN the TG MUST ALSO test that calling these getter methods on a non-numeric version string throws `NumberFormatException` — the exception may only be thrown lazily when a numeric method is invoked, not at construction time
- Common pitfalls to avoid:
  - **Testing only well-formed version strings**: Do NOT assume the code handles all inputs; always test with intentionally malformed version strings containing alphabetic characters in numeric positions
  - **Testing only one type of non-numeric input**: Test with various patterns like `"x"`, `"1.x"`, `"1.0.x"`, `"1.0.0-x"`, `"x.y.z"` to cover different parsing paths
  - **Missing the specific exception type**: `assertThrows(NumberFormatException.class, ...)` not just `assertThrows(Exception.class, ...)` — the contract should guarantee `NumberFormatException`
  - **Assuming exception is thrown eagerly at construction**: The bug may be that the constructor silently stores the non-numeric value but only later code (e.g., getters) attempts to parse it. Test both construction and method invocation.

## Examples

**Correct test (what the TG should write):**

```java
@Test
void testNonNumericVersionRepresentationReturnsANumberFormatException() {
    assertThrows(NumberFormatException.class, () -> new DefaultArtifactVersion("1.0.abc"));
    assertThrows(NumberFormatException.class, () -> new DefaultArtifactVersion("x.y.z"));
    assertThrows(NumberFormatException.class, () -> new DefaultArtifactVersion("1.0.0-SNAPSHOT"));
}

// Also test getter methods that may parse lazily
@Test
void testNonNumericMajorVersionGetterThrows() {
    DefaultArtifactVersion v = new DefaultArtifactVersion("abc.1.0");
    assertThrows(NumberFormatException.class, v::getMajorVersion);
}
```

**Incorrect test (too weak/insufficient):**

```java
// WRONG: Only tests well-formed string, misses non-numeric cases
@Test
void testVersionParsing() {
    DefaultArtifactVersion v = new DefaultArtifactVersion("1.0.0");
    assertEquals(1, v.getMajorVersion());
}

// WRONG: Catches generic Exception, not specific NumberFormatException
@Test 
void testNonNumericVersion() {
    try {
        new DefaultArtifactVersion("abc");
    } catch (Exception e) {
        // Too broad — won't catch if wrong exception type is thrown
    }
}

// WRONG: Assumes exception is thrown at construction, but buggy code may swallow it
@Test
void testNonNumericVersion() {
    // This might PASS even on buggy code if constructor doesn't throw
    assertThrows(NumberFormatException.class, () -> new DefaultArtifactVersion("x"));
}
```