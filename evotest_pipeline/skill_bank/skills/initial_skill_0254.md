---
name: lowercase-function-array-type-handling
description: Tests for functions like LOWER() that process property values must handle
  both single-value (STRING) and multi-value (STRINGS) types correctly. When the function
  branches on p.getType().isArray(), the test must cover both branches with concrete
  data.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- STATE_MUTATION
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# lowercase-function-array-type-handling

## Instructions

# Skill: Testing Functions That Branch on Array vs Single-Value Property Types

## Instructions

- WHEN the TG encounters a `PropertyValue` processing function (e.g., `LowercaseImpl.currentProperty()`) that checks `p.getType().isArray()` and branches into two separate code paths:
  - One branch calls `p.getValue(STRINGS)` (multi-value / array) and transforms each element
  - The other branch calls `p.getValue(STRING)` (single value) and transforms the single string
- THEN the TG MUST write a test that exercises BOTH branches, by creating JCR nodes with:
  - A multi-valued STRINGS property (using `Type.STRINGS`), e.g., `node.setProperty("prop", ImmutableList.of("ValueA", "ValueB"), Type.STRINGS)`
  - A single-valued STRING property (using `Type.STRING` implicitly), e.g., `node.setProperty("prop", "ValueC")`
  - Then querying with `lower(@prop)` in the WHERE clause and asserting the correct path matches

- The bug is that the array branch uses `p.getValue(STRINGS)` and `PropertyValues.newString(lowerCase)` which may fail on arrays if `PropertyValues.newString` cannot handle the Iterable type for array properties. Verify the correct behavior by checking that both:
  1. `lower(@prop) = 'valuea'` matches the node with multi-valued prop `["ValueA", "ValueB"]`
  2. `lower(@prop) = 'valuec'` matches the node with single-valued prop `"ValueC"`

- Common pitfalls:
  - Testing only single-value STRING properties with `lower()` and assuming it works for arrays
  - Using `Type.STRINGS` to set multi-valued properties but querying with a predicate that expects a single lowercased value from the array
  - Not using `Type.STRINGS` explicitly when setting multi-valued properties (the property will default to single-value)

- Correct example (test both single and multi-valued):
```java
@Test
public void testLowercaseOnArrays() throws Exception {
    Tree c = root.getTree("/").addChild("content");
    // Multi-valued STRINGS property
    c.addChild("multi").setProperty("prop",
        ImmutableList.of("ValueA", "ValueB"), Type.STRINGS);
    // Single-valued STRING property  
    c.addChild("single").setProperty("prop", "ValueC");
    root.commit();

    assertQuery("//*[lower(@prop) = 'valuea']", "xpath",
        ImmutableList.of("/content/multi"));
    assertQuery("//*[lower(@prop) = 'valuec']", "xpath",
        ImmutableList.of("/content/single"));
}
```

- Incorrect example (only tests single-value, misses the array bug):
```java
@Test
public void testLowercaseOnArrays() throws Exception {
    Tree c = root.getTree("/").addChild("content");
    // Only tests single-value STRING
    c.addChild("single").setProperty("prop", "ValueC");
    root.commit();
    assertQuery("//*[lower(@prop) = 'valuec']", "xpath",
        ImmutableList.of("/content/single"));
    // MISSING: test for STRINGS array properties!
}
```