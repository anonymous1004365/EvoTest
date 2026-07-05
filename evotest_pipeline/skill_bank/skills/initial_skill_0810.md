---
name: trailing-separator-in-string-joiner
description: Detects bugs where string joining logic appends trailing separators (e.g.,
  trailing comma, space, or other characters) when iterating over collections. Use
  when concatenating elements with a separator in a loop.
code_tags:
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# trailing-separator-in-string-joiner

## Instructions

# Trailing Separator in String Joiner

## Instructions

- WHEN the TG encounters code that joins/concatenates strings from a collection by appending a separator character (e.g., `','`, `' '`, `';'`, `'&'`) in each iteration of a loop (e.g., `for (String s : items) { buf.append(s).append(','); }`),
  - THEN it should test the output string for an unexpected trailing separator character.
  - The test must verify that the resulting string does NOT end with the separator character.
  - For example, if the code joins `["a", "b"]` with `','`, the expected output is `"a,b"`, NOT `"a,b,"`.
  - Common patterns to test: iterating over query parameters (joining with `&`), path segments (joining with `/`), or any list of strings joined by a delimiter.
  - Use an assertion like `assertFalse(result.endsWith(","))` or `assertEquals("a,b", result)` to detect the bug.
  - **Common pitfalls**: The TG might test with a single element (which hides the bug since no trailing separator appears), or might not check the string end at all. Always test with **at least two elements** to expose the trailing separator. Also, avoid testing with an empty collection (which may produce an empty string and pass incorrectly). Use exactly 2 or 3 elements to clearly see the trailing separator bug.

- Correct test pattern (catches the bug):
```java
StringJoiner joiner = new StringJoiner(",");
joiner.append("a");
joiner.append("b");
assertEquals("a,b", joiner.toString()); // fails if output is "a,b,"
```

OR

```java
StringBuilder sb = new StringBuilder();
String[] items = {"a", "b"};
for (String s : items) {
    sb.append(s).append(',');
}
String result = sb.toString();
assertFalse("Should not have trailing comma", result.endsWith(","));
assertEquals("a,b", result); // fails on buggy version
```

- Incorrect test pattern (misses the bug):
```java
// Testing with only one element — hides the bug
StringBuilder sb = new StringBuilder();
sb.append("a").append(',');
assertEquals("a,", sb.toString()); // passes on both buggy and fixed
```

- WHEN the code uses `StringBuilder.append()` in a loop with a separator, also check that:
  1. The separator is not appended after the last element (or removed after the loop).
  2. Test with non-empty collection of size >= 2.
  3. Verify the exact expected string, not just a substring match.