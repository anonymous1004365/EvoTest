---
name: abstract-factory-ignore-null-results
description: WHEN a method delegates to an abstract factory method that may return
  null, THEN test that the parent method handles null gracefully and forwards it,
  rather than silently ignoring null or failing without a proper message. Applies
  to template method patterns where subclasses override factory methods.
code_tags:
- STATE_MUTATION
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# abstract-factory-ignore-null-results

## Instructions

# Abstract Factory Methods: Do Not Silently Ignore Null Returned by Abstract/Delegate Method

## Instructions

**WHEN** a method calls an abstract or overridable factory/creation method that returns a value (e.g., a template method pattern where a protected abstract method is called), **THEN** write a test that provides a mock/subclass implementation of that factory method that returns `null`, and verify that the calling method either:
- Throws the appropriate exception (e.g., `IllegalArgumentException`, `NullPointerException` with a clear message), or
- Properly propagates the null as a valid result (i.e., forwarding null instead of replacing it).

**Common pitfalls to avoid**:
- **Testing only the "happy path"** where the factory method returns a valid non-null object. This misses the case where the factory method returns null.
- **Assuming the parent method handles null internally** without actually testing it. Many bugs arise when a developer assumes the abstract method never returns null.
- **Not providing a concrete test implementation** — use an anonymous subclass or mock framework to override the factory method to return null.
- **Testing the concrete implementation** instead of the abstract class's template method behavior.

**Concrete example** (from a decoder framework):
- In a protocol decoder, a template method calls `getTagLength()` or a similar abstract factory method to determine how to parse a field.
- The bug: When the abstract method returns `null`, the template method silently discards the null and proceeds with an incorrect default, leading to wrong parsing.
- The fix: The template method should either propagate the null (return null) or throw an appropriate exception when the abstract method returns null.

**Correct test approach**:
```java
@Test
public void testDecodeWithNullResultFromAbstractMethod() {
    // Given: a concrete subclass that overrides the factory method to return null
    MyDecoder decoder = new MyDecoder() {
        @Override
        protected SomeResult getSomeResult(Channel channel, SocketAddress addr, Object msg) {
            return null; // simulate edge case where factory method returns null
        }
    };
    // When: the template decode method is called
    // Then: it should throw an exception or return null, but not silently proceed
    assertThrows(NullPointerException.class, () -> {
        decoder.decode(null, null, someInput);
    });
}
```

**Incorrect test approach** (happy-path only):
```java
@Test
public void testDecodeNormal() {
    // Only tests the non-null case — misses the bug entirely
    MyDecoder decoder = new MyConcreteDecoder();
    Object result = decoder.decode(null, null, validInput);
    assertNotNull(result);
}
```

**What the test should verify on the buggy version**: Calling the template method when the abstract/overridable factory method returns `null` produces an incorrect result (silently proceeds with wrong data) instead of throwing an exception or returning null. The test should **fail on the buggy version** and **pass on the fixed version**.