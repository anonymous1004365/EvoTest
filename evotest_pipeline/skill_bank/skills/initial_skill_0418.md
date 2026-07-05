---
name: mock-stub-method-throws-not-implemented
description: When a mock/stub implementation of an interface method throws NotImplementedException
  (from org.apache.commons.lang), the test should verify this exception is thrown.
  This skill teaches how to test stub methods that deliberately throw "not implemented"
  to ensure they fail fast with the expected exception.
code_tags:
- STUB_METHOD_UNIMPLEMENTED
test_pattern: EXCEPTION_TEST
---

# mock-stub-method-throws-not-implemented

## Instructions

# Mock Stub Method Throws NotImplementedException

## Instructions

WHEN the TG encounters a mock/stub implementation class (e.g., `MockTableOperations`) that overrides an interface method (e.g., `deleteRows(String, Text, Text)`) and the method body is empty or consists solely of `throw new NotImplementedException()` (from `org.apache.commons.lang.NotImplementedException`), THEN the TG should write a test that:

1. **Calls the stub method with valid input parameters and asserts that it throws `NotImplementedException`.** The test should use `@Test(expected = NotImplementedException.class)` or `Assert.fail()` after the call with a catch clause for `NotImplementedException`.

2. **Sets up the preconditions properly** — create the necessary mock instance (e.g., `MockInstance`), get a connector, and create any required table before calling the method.

3. **Uses exactly the method signature parameters** — pass concrete values for each parameter (e.g., `new Text("1")` for Text parameters, a valid table name as a String).

4. **Common pitfalls to avoid**:
   - Do NOT assert a generic `RuntimeException` or `Exception` — assert specifically `NotImplementedException` from `org.apache.commons.lang`.
   - Do NOT call the method without expecting an exception — the stub will throw, so the test must catch or declare `@Test(expected=...)`.
   - Do NOT test with null parameters unless the method explicitly documents null-safety — use concrete valid values like `new Text("1")` and `new Text("2")`.
   - Do NOT forget to create the table first if the method requires it (some stubs check `exists(tableName)` before throwing).
   - Do NOT use `expected = Exception.class` (too broad) — use the exact `NotImplementedException.class`.

### Correct Example

```java
import org.apache.commons.lang.NotImplementedException;
// ...

@Test(expected = NotImplementedException.class)
public void testDeleteRowsNotImplemented() throws Exception {
    Instance instance = new MockInstance("test");
    Connector conn = instance.getConnector("user", "pass");
    TableOperations to = conn.tableOperations();
    to.create("test");
    to.deleteRows("test", new Text("1"), new Text("2"));
}
```

### Incorrect Example

```java
// WRONG: does not expect any exception, test will fail with NotImplementedException
@Test
public void testDeleteRows() throws Exception {
    Instance instance = new MockInstance("test");
    Connector conn = instance.getConnector("user", "pass");
    TableOperations to = conn.tableOperations();
    to.create("test");
    to.deleteRows("test", new Text("1"), new Text("2")); // throws silently, test fails
}
```

```java
// WRONG: catches Exception (too broad) without asserting it's NotImplementedException
@Test
public void testDeleteRowsWrong() throws Exception {
    Instance instance = new MockInstance("test");
    Connector conn = instance.getConnector("user", "pass");
    TableOperations to = conn.tableOperations();
    to.create("test");
    try {
        to.deleteRows("test", new Text("1"), new Text("2"));
        Assert.fail("Expected NotImplementedException");
    } catch (Exception e) {
        // Should be NotImplementedException specifically
        Assert.assertTrue(e instanceof NotImplementedException);
    }
}
```