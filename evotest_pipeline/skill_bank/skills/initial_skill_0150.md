---
name: empty-object-array-message-format
description: WHEN a method accesses array elements by index (e.g., array[0]) without
  first checking array length, THEN tests must verify behavior when the array is empty
  (length 0) to prevent ArrayIndexOutOfBoundsException. This skill applies to any
  method that indexes into an array parameter, not just logging frameworks.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- STATE_MUTATION
- ARRAY_ITERATION
- VALIDATION
- EMPTY_ARRAY
- ARRAY_INDEX_ACCESS
test_pattern: EXCEPTION_TEST
retrieval:
  keywords: []
  boosted_tags: []
  suppressed_tags: []
  negative_triggers: []
  applicable_tiers: []
  transition_tags: []
---

# empty-object-array-message-format

## Instructions

# Empty Object Array in Logging Message Format

## Instructions

- WHEN the TG encounters a method that formats log messages using an `Object` array parameter (e.g., `Object[] params`), and the method accesses elements of that array by index
- THEN it MUST test with an **empty `Object` array** (`new Object[0]` or `{}`) being passed as the parameter
- Concrete behavior to verify: the method should handle `Object[0]` gracefully without throwing any exception; specifically, no `ArrayIndexOutOfBoundsException` should occur when the message pattern requires parameter substitution but no parameters are provided
- Common pitfalls:
  - Testing only with non-null, non-empty parameter arrays, missing the empty array edge case
  - Assuming that passing `null` as the parameter array is sufficient to cover the empty case — they are different paths
  - Only testing with `String` type message patterns that have no `{}` placeholders, missing the case where placeholders exist but no parameters are supplied
- Expected result on the buggy version: `ArrayIndexOutOfBoundsException` at index `-1` when the message pattern contains `{}` placeholders but the `Object[]` is empty
- The test should construct a message with placeholders (e.g., `"Hello {}"`) and call the logging method with an empty `Object[]` array, asserting that no exception is thrown

## Example

### Correct test (detects the bug)

```java
@Test
public void testMessageWithEmptyObjectArray() {
    final SimpleLogger logger = new SimpleLogger("test");
    // The message has a {} placeholder, but the parameter array is empty
    logger.info("Hello {}", new Object[0]);  // Should not throw ArrayIndexOutOfBoundsException
}
```

### Incorrect test (misses the bug)

```java
@Test
public void testMessageWithNullObjectArray() {
    final SimpleLogger logger = new SimpleLogger("test");
    // This tests null array, not empty array - different code path
    logger.info("Hello {}", (Object[]) null);  // This might work but still misses the empty array case
}
```