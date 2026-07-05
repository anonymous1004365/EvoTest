---
name: pageparameters-add-null-or-empty-name-validation
description: When testing PageParameters.add() which calls Args.notEmpty(name, "name"),
  the test must verify that null and empty string parameter names are rejected with
  IllegalArgumentException. This skill helps avoid missing validation coverage for
  the add() method that is commonly missed because add() is overloaded.
code_tags:
- ARGUMENT_VALIDATION
- NULL_CHECK
- EDGE_CASE_INPUT
test_pattern: EXCEPTION_TEST
---

# pageparameters-add-null-or-empty-name-validation

## Instructions

# PageParameters add() Null and Empty Name Validation

## Instructions

- WHEN the TG encounters a class named `PageParameters` that has an `add(String name, Object value)` method
- THEN the TG should test that passing `null` as the `name` parameter to `add(String name, Object value)` throws `IllegalArgumentException` with a message containing `"name"`.
  ALSO test that passing an empty string `""` as the `name` parameter to `add(String name, Object value)` throws `IllegalArgumentException` with a message containing `"name"`.

- WHEN the TG encounters a class named `PageParameters` that has an `add(String name, Object value, ...)` overloaded variant OR a `set(String name, Object value)` method OR any method that internally validates `name` using `Args.notEmpty(name, "name")`
- THEN the TG should test that all such methods also reject `null` and `""` for the `name` parameter with `IllegalArgumentException`. The `Args.notEmpty()` call inside the buggy `PageParameters.add()` method is the source that throws for null/empty values — but the test should be written at the public API level, calling the method directly.

- WHEN the TG writes a test for `PageParameters.add(String name, Object value)` where `name` is a named parameter name
- THEN the TG should include both `null` and empty string `""` as explicit test inputs for the name parameter, AND verify that the exception is thrown. Common pitfalls:
  * Only testing with valid non-null, non-empty name values
  * Testing `add(null, value)` but not testing `add("", value)` (or vice versa)
  * Forgetting to check the exception message contains "name"
  * Using `assertThrows` without catching the specific exception type `IllegalArgumentException`

**Correct example (JUnit 4 style):**
```java
@Test(expected = IllegalArgumentException.class)
public void addWithNullName()
{
    PageParameters params = new PageParameters();
    params.add(null, "someValue");
}

@Test(expected = IllegalArgumentException.class)
public void addWithEmptyName()
{
    PageParameters params = new PageParameters();
    params.add("", "someValue");
}
```

**Correct example (JUnit 5 style):**
```java
@Test
public void addWithNullName()
{
    PageParameters params = new PageParameters();
    assertThrows(IllegalArgumentException.class, () -> params.add(null, "someValue"));
}

@Test
public void addWithEmptyName()
{
    PageParameters params = new PageParameters();
    assertThrows(IllegalArgumentException.class, () -> params.add("", "someValue"));
}
```

**Incorrect example (missing empty string test):**
```java
@Test(expected = IllegalArgumentException.class)
public void addWithNullName()
{
    PageParameters params = new PageParameters();
    params.add(null, "someValue");
}
// Missing: test for add("", "someValue") which also throws IllegalArgumentException
```

**Incorrect example (wrong exception type):**
```java
@Test
public void addWithNullName()
{
    PageParameters params = new PageParameters();
    assertThrows(NullPointerException.class, () -> params.add(null, "someValue"));
    // Incorrect: Args.notEmpty throws IllegalArgumentException, not NullPointerException
}
```