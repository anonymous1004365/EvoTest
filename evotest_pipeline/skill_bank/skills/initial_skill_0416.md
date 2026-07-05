---
name: ct-element-metadata-state-validation
description: When testing metadata operations on CtElements in Spoon, validate that
  annotation metadata state is properly cleared, reset, and preserved across clone/modify
  operations. Use this skill to catch bugs where metadata is incorrectly inherited,
  duplicated, or not cleaned up after element transformations.
code_tags:
- VALIDATION
- NULL_CHECK
- STATE_MUTATION
test_pattern: STATE_TEST
---

# ct-element-metadata-state-validation

## Instructions

# CtElement Metadata State Validation

## Instructions

- WHEN the code under test manipulates element metadata (putMetadata, getMetadata, getAllMetadata, or similar metadata accessors) on Spoon CtElements (CtType, CtMethod, CtField, CtParameter, etc.)
- THEN the test MUST verify that metadata state transitions are correct by:
  1. Testing that metadata set on one element does NOT leak to another element (e.g., a type's metadata should not appear on its methods or fields)
  2. Testing that clearing or resetting metadata works: after removing a metadata key, `getMetadata` for that key returns null
  3. Testing that metadata is properly preserved after clone/copy operations if applicable
  4. Testing that metadata uses correct key types and value types — e.g., test with both String keys and custom key objects (like CtTypeReference) as metadata keys

- Include concrete assertions that would fail on the buggy version:
  - `assertNull(element.getMetadata(key))` after clearing
  - `assertNull(element.getMetadata(key))` on a child element when metadata was only set on the parent
  - Use `assertThat(element.getAllMetadata().size(), is(expectedSize))` to verify exact metadata count

- Common pitfalls to avoid:
  - Testing only that metadata CAN be set and retrieved (happy path) without testing isolation between elements
  - Testing only String keys when custom key types (like CtTypeReference) are also used in production
  - Not testing the null/cleared state — assuming a metadata key always exists if set once
  - Testing metadata on one element type only (e.g., only CtType) when the same API exists on all CtElement subtypes

- Example of a GOOD test pattern:
  ```java
  // Good: tests isolation AND clearing AND key type variety
  CtType<?> type = factory.Type().get("MyClass");
  CtMethod<?> method = type.getMethodsByName("foo").get(0);
  
  Object key1 = "myKey";
  Object key2 = factory.Type().createReference("java.util.List");
  
  // Set on type only
  type.putMetadata(key1, "value1");
  type.putMetadata(key2, "value2");
  
  // Verify isolation: child should NOT see parent's metadata
  assertNull("Metadata leaked to child element", method.getMetadata(key1));
  assertNull("Metadata leaked to child element", method.getMetadata(key2));
  
  // Verify clear
  type.putMetadata(key1, null);
  assertNull("Metadata not cleared", type.getMetadata(key1));
  ```
- Example of a BAD test pattern:
  ```java
  // Bad: only tests happy path, String key only, no isolation check
  CtType<?> type = factory.Type().get("MyClass");
  type.putMetadata("key", "value");
  assertEquals("value", type.getMetadata("key")); // passes even with buggy code
  ```