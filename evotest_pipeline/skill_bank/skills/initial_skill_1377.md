---
name: field-default-to-null-npe-in-getter
description: WHEN a CLI-option class has a Wrapper-type field (like Password password
  = new Password("secret")) that JCommander sets to null when the option is not provided,
  and a getter accesses that field's inner .value without null-checking the outer
  field first, THEN test that the getter returns null when the option is omitted,
  to avoid NPE or returning a stale default. Covers the case where the default value
  was removed (changed to null) but the getter still assumes non-null access.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
test_pattern: STATE_TEST
---

# field-default-to-null-npe-in-getter

## Instructions

# Field Default-to-Null NPE in Getter

## Instructions

**WHEN** the TG encounters a class that:
- Has a field of a wrapper/inner-type class (e.g., `Password password`) that is annotated with `@Parameter` for CLI parsing via JCommander
- The field's initial value was changed FROM a non-null constructor call (e.g., `new Password("secret")`) TO `null` (e.g., `Password password = null`)
- There is a getter method that accesses `field.value` (or any inner field of the outer wrapper) AFTER a null check on `field` itself — BUT the null check was on the inner `.value` instead of on the outer field reference

**THEN** the TG should write a test that:
1. Creates a new instance of the class (e.g., `ClientOpts args = new ClientOpts()`)
2. Calls the getter method (e.g., `args.getToken()`) WITHOUT invoking any CLI parsing first (i.e., default state)
3. Asserts that the result is `null` using `assertNull(…)`
4. On the buggy version, the assertion will fail because the getter accesses `password.value` when `password` is `null`, causing an NPE — OR the getter returns a non-null `PasswordToken` because it falls through to the inner-field branch

**Concrete example from this bug:**
- Class: `org.apache.accumulo.core.cli.ClientOpts` (method `getToken()`)
- Bug: `password` was changed from `new Password("secret")` to `null`. The `getToken()` method checked `if (password.value == null)` instead of `if (password == null)`, so when `password` is `null`, accessing `password.value` throws NPE. (The test failure shows `expected null, but was:<PasswordToken@...>` — meaning the code returned a non-null token instead of null.)
- Correct test: `assertNull(args.getToken())` where `args` is a `new ClientOpts()` with no CLI arguments parsed

**Common pitfalls to avoid:**
- Testing only after JCommander `.parse(...)` has been called, which may set `password` to a non-null value, hiding the null-initial-value bug
- Checking `field.value == null` in the test rather than checking that the outer `field` itself may be null
- Only testing the default constructor field value (e.g., `"secret"`) without considering that it might have been changed to `null` by a later commit
- Not asserting `assertNull` on the return value of the getter when no CLI arguments are provided

**Correct test example:**
```java
@Test
public void testGetTokenReturnsNullWhenNoPasswordProvided() {
    ClientOpts args = new ClientOpts();
    assertNull("getToken() should return null when no password is provided", args.getToken());
}
```

**Incorrect test example (WRONG — would not catch the bug):**
```java
@Test
public void testGetToken_afterParse() {
    ClientOpts args = new ClientOpts();
    JCommander jc = new JCommander(args);
    jc.parse("-p", "foo");
    assertNotNull(args.getToken()); // This works because JCommander sets password to non-null
}
// Missing: testing the default (no-parse) state
```