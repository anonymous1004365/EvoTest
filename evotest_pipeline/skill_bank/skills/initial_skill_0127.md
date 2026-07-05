---
name: bean-empty-string-null-assignment
description: When a bean property setter receives an empty string, the test should
  verify that the property is assigned null (not an empty string) to catch bugs where
  empty string validation is missing. Use this skill when testing deserialization
  or bean population from sources that may contain empty string values.
code_tags:
- ARGUMENT_VALIDATION
- NULL_CHECK
- BOUNDARY_CHECK
test_pattern: STATE_TEST
---

# bean-empty-string-null-assignment

## Instructions

# Bean Empty String to Null Assignment Validation

## Instructions

- WHEN the TG encounters a bean property assignment that processes input values coming from a structured data source (e.g., CSV parsing, JSON deserialization, or any line-based record parser that maps strings to bean properties via setters)
- THEN the TG should write a test that creates a bean instance, populates it via the setter method with an empty string `""`, and verifies that the resulting bean property value is `null` (not `""`)
- The test must use the actual bean class (e.g., `Bean2Cell` or any similar bean) and invoke the setter directly with an empty string, then assert that the getter returns `null`
- Common pitfalls to avoid:
  - Testing only non-empty string values (e.g., "123", "abc") and forgetting to test the empty-string boundary case
  - Assuming the bean setter will handle coercion automatically — this test explicitly verifies the coercion logic
  - Testing via a mock instead of the actual bean instance — the real bean setter behavior must be exercised
  - Asserting the property equals `""` or empty string — the correct expected value is `null`

### Correct Example (Java/JUnit 5):
```java
@Test
void assign_empty() {
    Bean2Cell bean = new Bean2Cell();
    bean.setMyProperty("");  // empty string input from parsed data
    assertNull(bean.getMyProperty());  // must be null, not ""
}
```

### Incorrect Example (misses the bug):
```java
@Test
void assign_non_empty() {
    Bean2Cell bean = new Bean2Cell();
    bean.setMyProperty("someValue");
    assertEquals("someValue", bean.getMyProperty());
    // Bug: empty string case is never tested, so the missing null-coercion is never caught
}
```

### Failure Expectation
On the buggy version, `bean.getMyProperty()` returns `""` (empty string) instead of `null`, causing downstream consumers of the bean to incorrectly see a non-null empty value. The test should fail with `expected: null but was: ""` (or similar assertion failure) on buggy code and pass on fixed code.