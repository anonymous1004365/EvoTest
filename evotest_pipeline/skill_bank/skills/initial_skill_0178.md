---
name: mutable-thread-context-stack-tostring
description: When testing ThreadContextStack implementations that wrap a mutable list,
  verify that toString() reflects the current contents of the underlying list rather
  than using the default Object.toString() representation.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
test_pattern: STATE_TEST
---

# mutable-thread-context-stack-tostring

## Instructions

# Mutable ThreadContextStack toString Must Reflect Contents

## Instructions

- WHEN the TG encounters a class that implements `ThreadContextStack` (or similar collection-like interface) by delegating to an internal `List` field (e.g., `private final MutableThreadContextStack` wrapping a `List<String>`)
- THEN the TG should verify that `toString()` on the wrapper returns a string representation of the **contained elements**, not the default `Object.toString()` (e.g., something like `ClassName@hash`).
  - Specifically, after adding elements to the stack via `push()` / `addAll()`, assert that `stack.toString()` returns a string that contains the **actual added values**, such as `"[]"` for an empty stack or `"[value1, value2]"` for a populated one.
  - Do NOT assume that `toString()` is inherited from `AbstractCollection` or correctly delegated — the bug is that the wrapper's `toString()` simply returns the default `Object.toString()` output instead of delegating to the underlying list.
- WHEN the TG is asserting on the string output of a collection wrapper, use assertions like:
  - `assertEquals("[]", stack.toString())` — NOT `assertTrue(stack.toString().contains("MutableThreadContextStack"))`
  - The expected format should match the `List.toString()` format (square brackets with comma-separated elements).
- Common pitfalls to avoid:
  - ❌ Testing only the `push()`/`pop()`/`peek()` behavior without checking `toString()`
  - ❌ Asserting that `toString()` contains the class name (which the default `Object.toString()` also would)
  - ❌ Using `assertNotNull(stack.toString())` — this always passes even when the output is `"ClassName@hash"`
  - ✅ Always verify that `toString()` output matches the expected `List.toString()` format for the underlying contents.

### Correct test example
```java
@Test
public void testToStringShowsListContents() {
    final MutableThreadContextStack stack = new MutableThreadContextStack();
    stack.push("value1");
    stack.push("value2");
    // toString() must show list-style contents, not Object.toString()
    assertEquals("[value1, value2]", stack.toString());
}
```

### Incorrect test example
```java
@Test
public void testToStringShowsListContents() {
    final MutableThreadContextStack stack = new MutableThreadContextStack();
    stack.push("value1");
    stack.push("value2");
    // WRONG: This only checks that toString() is non-null, not that it shows contents
    assertNotNull(stack.toString());
    // WRONG: This checks for class name, but still passes with buggy Object.toString()
    assertTrue(stack.toString().contains("MutableThreadContextStack"));
}
```