---
name: ognl-method-return-null-body-check
description: When using OGNL method invocations on the message body that return null,
  the body should NOT be replaced with the null result. This skill teaches how to
  test that null-returning OGNL methods leave the body unchanged.
code_tags:
- NULL_CHECK
- STATE_MUTATION
test_pattern: STATE_TEST
---

# ognl-method-return-null-body-check

## Instructions

# OGNL Method Return Null Body Preservation

## Instructions

- WHEN the TG encounters a method that uses OGNL expressions to invoke methods on the message body (e.g., `${body.doSomething()}`) where the invoked method could return `null`
- THEN it should write a test that:
  1. Sets up a message body with a POJO that has a method returning `null` (e.g., `public String doSomething() { return null; }`)
  2. Sends the message through a route that applies the OGNL expression via `.setBody().ognl("request.body.doSomething()")` (or equivalent simple/OGNL expression)
  3. Verifies that the body is **NOT** replaced with `null` — it should still contain the original POJO instance
  4. Optionally verify that a second OGNL access (e.g., `request.body.otherField`) still works correctly on the unchanged body
- WHEN the test expects that a null-returning OGNL method should leave the body unchanged
- THEN the test should assert that the body is not null and is an instance of the original POJO class
- The test should verify that the message body retains its original value after invoking a method that returns null via OGNL, rather than being overwritten with null

**Common pitfalls to avoid:**
- Testing only with methods that return non-null values — the bug specifically manifests when the invoked method returns null
- Assuming the body is replaced with the null result — the correct behavior is to keep the original body
- Not testing with a POJO that has both a null-returning method and other accessible fields to verify the body is intact

**Correct test example:**
```java
public class FooService {
    public String doSomething() { return null; }
}

route.setBody().ognl("request.body.doSomething()");
// After processing, body should still be the FooService instance, not null
assertNotNull(result.getBody());
assertTrue(result.getBody() instanceof FooService);
```

**Incorrect test example:**
```java
// This tests only with non-null return values, missing the bug
public class FooService {
    public String doSomething() { return "hello"; }
}
// The bug only manifests when the method returns null
```