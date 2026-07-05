---
name: string-cutleadingonprefix-edge-cases
description: Tests for the Strings.cutLeadingOnPrefix method should verify behavior
  when the input string does not start with the prefix, and should return the original
  string unchanged in that case.
code_tags:
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# string-cutleadingonprefix-edge-cases

## Instructions

# String.cutLeadingOnPrefix: Return Original When No Match

## Instructions

- WHEN the TG encounters a call to `Strings.cutLeadingOnPrefix(String, String)` or similar utility methods that conditionally strip a prefix from a string
- THEN it should write parametric tests using `@ParameterizedTest` with `@CsvSource` or `@MethodSource` that verify:
  - When the input string does NOT start with the given prefix, the method must return the **original string unchanged** (not null, not an empty string, not a modified version)
  - When the input string IS null, the method should return null
  - When the prefix IS null or empty, the method should return the original string
  - The test should assert the result using `assertEquals(expected, actual)`

- **Common pitfalls to avoid**:
  - Testing only the happy path where the prefix matches (e.g., `cutLeadingOnPrefix("onclick", "on")` returning `"click"`)
  - Forgetting to test the case where no prefix match occurs — this is where the bug likely lives (e.g., the method might incorrectly return null or empty string when there is no prefix match)
  - Not testing null inputs — many utility methods have hidden null-handling bugs
  - Not testing empty string inputs — empty strings often trigger edge-case logic errors

### Correct test example:

```java
@ParameterizedTest
@CsvSource({
    "onclick, on, click",
    "click, on, click",       // no prefix match → original string
    "'', on, ''",             // empty input → empty string
    "onclick, '', onclick",   // empty prefix → original string
    "onclick, null, onclick", // null prefix → original string
    "null, on, null"          // null input → null
    ", on, "                  // null input → null (implicit null)
})
void cutLeadingOnPrefix(String input, String prefix, String expected) {
    assertEquals(expected, Strings.cutLeadingOnPrefix(input, prefix));
}
```

### Incorrect test (missing edge cases):

```java
// BAD: Only tests positive match case
@Test
void cutLeadingOnPrefix()
{
    assertEquals("click", Strings.cutLeadingOnPrefix("onclick", "on"));
    // Missing: what happens when prefix doesn't match?
    // Missing: null inputs
    // Missing: empty inputs
}
```