---
name: join-list-with-null-elements
description: When a method joins a list of strings into a single string using a separator,
  test with null elements in the list to ensure nulls are skipped rather than corrupting
  the concatenation.
code_tags:
- ARGUMENT_VALIDATION
- STATE_MUTATION
- NULL_CHECK
test_pattern: PARAMETRIC_TEST
---

# join-list-with-null-elements

## Instructions

# Joining Strings With Null List Elements

## Instructions

- WHEN the TG encounters a `join(String separator, List<String> fragments)` or similar method that concatenates list elements into a single string with a separator
- THEN it should test with a list containing `null` elements to verify that `null` values are silently skipped rather than producing incorrect output such as dropping characters from adjacent elements
- Specifically, test with a list like `Arrays.asList("foo", null, "barbaz")` and verify that `join("-", list)` produces `"foo-barbaz"` on the fixed version, while the buggy version may produce incorrect output like `"foo-araz"` (corrupting characters adjacent to the null element)
- The test should assert that `String.join("-", "foo", null, "barbaz")` throws a `NullPointerException` (this is the standard JDK behavior), while the custom `Strings.join()` method should gracefully handle nulls by skipping them
- Do NOT test only with non-null strings — null elements in the list are the root cause of the bug, and the join method must handle them without corrupting adjacent data
- Common pitfalls: (1) Testing only with all non-null strings, which passes even on the buggy version; (2) Testing for a `NullPointerException` when the method should silently skip nulls; (3) Not testing with null elements in the *middle* of the list (not just at the end)

### Example (Correct test)

```java
@Test
public void testJoinWithNullElements() {
    // Null elements should be skipped, not corrupt adjacent text
    assertEquals("foo-barbaz", Strings.join("-", Arrays.asList("foo", null, "barbaz")));
    assertEquals("foo-barbaz", Strings.join("-", Arrays.asList(null, "foo", null, "barbaz", null)));
    assertEquals("", Strings.join("-", Arrays.asList((String) null)));
    assertEquals("", Strings.join("-", new ArrayList<String>()));
}
```

### Example (Incorrect — would NOT catch the bug)

```java
@Test
public void testJoin() {
    // Only tests with non-null elements — passes on BOTH buggy and fixed versions
    assertEquals("foo-bar-baz", Strings.join("-", Arrays.asList("foo", "bar", "baz")));
}
```