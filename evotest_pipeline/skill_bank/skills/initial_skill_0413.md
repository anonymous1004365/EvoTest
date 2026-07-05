---
name: null-token-equality-check
description: When a Credentials-like object wraps an AuthenticationToken that can
  be null, the test must verify that passing null toThrift() or similar serialization
  methods throws a NullPointerException or is handled correctly. This skill guides
  testing of null token serialization paths.
code_tags:
- NULL_CHECK
- VALIDATION
- EXCEPTION_HANDLING
test_pattern: EXCEPTION_TEST
---

# null-token-equality-check

## Instructions

# Null Token Serialization Test

## Instructions

- WHEN the TG encounters a class (such as `Credentials`) that wraps an `AuthenticationToken` field and has a method like `toThrift()` that serializes the token (e.g., via `token.getClass().getName()` or similar reflective operations)
- THEN the TG should write a test that:
  1. Creates an instance of the wrapper class (e.g., `Credentials`) with a **null token** (using a constructor or factory that permits null)
  2. Calls the serialization/Thrift conversion method (e.g., `toThrift()`)
  3. Asserts that the call throws a `NullPointerException` or appropriate exception indicating the null token was not handled

- Verify that the wrapper class is tested with both a valid `AuthenticationToken` and a `null` token, because the constructor may accept `null` tokens without failing, only to fail later during serialization

- Common pitfalls to avoid:
  - Testing only with valid tokens and not considering the null case
  - Assuming the constructor validates non-null tokens when it may not
  - Writing a test that catches `Exception` broadly — prefer asserting a specific exception type like `NullPointerException`
  - Not checking whether `NullToken` (a special sentinel class) is used instead of actual `null`

### Correct example (use as template):
```java
@Test(expected = NullPointerException.class)
public void testNullTokenToThrift() {
    Credentials creds = new Credentials("user", null);
    creds.toThrift();
}
```

### Incorrect example (pitfall to avoid):
```java
@Test
public void testToThrift() {
    // Only tests valid case, missing the null token case
    Credentials creds = new Credentials("user", new PasswordToken("pass"));
    assertNotNull(creds.toThrift());
}
```