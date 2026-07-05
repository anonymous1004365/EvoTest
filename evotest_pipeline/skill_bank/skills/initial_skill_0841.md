---
name: serialization-clone-exception-handling
description: When cloning objects via serialization, always test with objects whose
  fields reference non-serializable classes and verify that the cloneObject method
  throws a WicketRuntimeException wrapping the original exception, not a generic RuntimeException.
code_tags:
- VALIDATION
- BOUNDARY_CHECK
- SERIALIZATION_CLONE_BUG
- EXCEPTION_HANDLING
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# serialization-clone-exception-handling

## Instructions

# Serialization-Based Cloning Exception Handling

## Instructions

- WHEN the code uses WicketObjects.cloneObject() (which internally uses serialization/deserialization to clone an object) or any similar serialization-based cloning mechanism
- THEN write a test that verifies the correct exception propagation when cloning fails. Specifically:
  1. Create an object whose serialization will fail — e.g., an object whose fields reference a non-Serializable inner class, or an object graph containing a non-serializable object that Wicket's session store tries to clone
  2. Call the cloneObject() method (or the method that internally triggers cloning, like processing a page with form components that reference non-serializable page maps)
  3. Catch the resulting exception and assert that it is a WicketRuntimeException (not just any RuntimeException), AND that its message contains "Internal error cloning object"
  4. Verify the cause chain preserves the root cause (typically a java.io.NotSerializableException referencing the non-serializable class name)

- Common pitfalls to avoid:
  - Testing cloneObject() with only objects that are trivially serializable (primitive wrappers, Strings) — these will never trigger the bug
  - Forgetting to test the clone path that goes through a complex object graph (like a Page with a Form that has DropDown components referencing objects that reference non-serializable types)
  - Assuming the exception will be a generic RuntimeException — the fix specifically changed the handler to wrap in a WicketRuntimeException, so the test must assert WicketRuntimeException
  - Testing clone success but not clone failure — both should be tested

### Correct example pattern

```java
// Given an object whose class contains a non-serializable field
public class MyNonSerializableField {
    private final Object nonSerializable = new Object() { }; // anonymous inner class - not Serializable
}

// When cloning the object, expect WicketRuntimeException
@Test
void cloneObject_shouldThrowWicketRuntimeException_whenObjectNotSerializable() {
    MyNonSerializableField obj = new MyNonSerializableField();
    try {
        WicketObjects.cloneObject(obj);
        fail("Expected WicketRuntimeException");
    } catch (WicketRuntimeException e) {
        assertThat(e.getMessage(), containsString("Internal error cloning object"));
        assertThat(e.getCause(), instanceOf(NotSerializableException.class));
    }
}
```

### Incorrect example pattern

```java
// BAD: Testing only with serializable objects — no exception path tested
@Test
void cloneObject_shouldCloneCorrectly() {
    String original = "hello";
    String cloned = (String) WicketObjects.cloneObject(original);
    assertEquals(original, cloned);
}
// This test passes even with the buggy code — it does nothing to verify the error handling path
```