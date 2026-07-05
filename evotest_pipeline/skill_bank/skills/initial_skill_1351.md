---
name: table-not-found-exception-throwing
description: When a Proxy test method operates on a non-existent table via the Accumulo
  proxy client, the test must expect a TableNotFoundException from the proxy Thrift
  layer. Use this skill to verify that proxy methods properly translate Accumulo's
  TableNotFoundException into the proxy Thrift exception.
code_tags:
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# table-not-found-exception-throwing

## Instructions

# TableNotFound Exception Throwing

## Instructions

- WHEN the TG is testing a proxy method that performs an operation on a table name that does not exist (e.g., a randomly generated UUID table name, or a deleted table)
- THEN the TG should verify that the proxy Thrift client throws `org.apache.accumulo.proxy.thrift.TableNotFoundException` when invoking operations like `openScanner`, `updateAndFlush`, `closeScanner`, etc. on a non-existent table
- The test should catch the exception explicitly using `@Test(expected = TableNotFoundException.class)` or a try-catch with `Assert.fail()`
- WHEN creating the test, use a unique non-existent table name, e.g. `UUID.randomUUID().toString()`, to avoid collisions with any existing tables
- Common pitfalls:
  - Testing with a table name that happens to exist (test becomes flaky or passes incorrectly)
  - Expecting `TException` or `Exception` instead of the specific `TableNotFoundException` — the fix is specifically about ensuring `TableNotFoundException` is thrown
  - Not importing `org.apache.accumulo.proxy.thrift.TableNotFoundException` properly
  - Looking for the exception from the wrong server/thrift layer — the exception wraps the Accumulo core `TableNotFoundException` into the proxy Thrift variant

### Correct Example
```java
@Test(expected = TableNotFoundException.class)
public void tableNotFound() throws Exception {
  String tableName = UUID.randomUUID().toString();
  // tableName does not exist, so operation must throw
  client.openScanner(tableName, new ScanOptions());
}
```

### Incorrect Example
```java
// BAD: Uses a table that might exist, or expects wrong exception type
@Test
public void tableNotFound() throws Exception {
  try {
    client.openScanner("users", new ScanOptions());
    fail("Should have thrown");
  } catch (TException e) {
    // wrong - should catch TableNotFoundException specifically
  }
}
```