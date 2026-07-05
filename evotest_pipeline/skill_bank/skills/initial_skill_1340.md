---
name: nosql-manager-connection-state-testing
description: Tests for NoSqlDatabaseManager must verify that connectAndStart and startup
  are properly called before writeInternal, and that calling writeInternal on an unconnected
  or closed connection throws AppenderLoggingException. Use this skill when testing
  manager lifecycle and connection state transitions.
code_tags:
- NULL_CHECK
- STATE_MUTATION
test_pattern: INTERACTION_TEST
---

# nosql-manager-connection-state-testing

## Instructions

# NoSQL Database Manager Connection State Testing

## Instructions

- WHEN the TG encounters a class extending `AbstractDatabaseManager` (like `NoSqlDatabaseManager`) that has lifecycle methods `startup()`, `connectAndStart()`, `writeInternal()`, and `commitAndClose()`
- THEN the TG should write a test that verifies `connectAndStart()` delegates to `provider.getConnection()`. Call `manager.connectAndStart()` on a manager created with `NoSqlDatabaseManager.getNoSqlDatabaseManager("name", 0, provider)` and verify via Mockito's `then(provider).should().getConnection()` that the provider was called.
- WHEN the TG encounters the `writeInternal(LogEvent)` method which checks `this.isRunning()` and `this.connection.isClosed()` before writing
- THEN the TG should write a test (named `testWriteInternalNotConnected01`) that creates a `NoSqlDatabaseManager` WITHOUT calling `startup()` or `connectAndStart()`, calls `manager.writeInternal(mock(LogEvent.class))`, and asserts that an `AppenderLoggingException` is thrown. Use `expectedException.expect(AppenderLoggingException.class)` from JUnit's `ExpectedException` rule.
- WHEN the TG encounters the `writeInternal(LogEvent)` method which also checks if the connection is explicitly closed
- THEN the TG should write a test (named `testWriteInternalNotConnected02`) that sets `given(connection.isClosed()).willReturn(true)`, calls `manager.startup()` and `manager.connectAndStart()`, then calls `manager.writeInternal(mock(LogEvent.class))`, and asserts that an `AppenderLoggingException` is thrown.
- Common pitfalls to avoid:
  - Do NOT forget to call `manager.startup()` before `connectAndStart()` — `startup()` sets the `running` flag to `true` via `AbstractDatabaseManager.startup()`, and `writeInternal` checks `this.isRunning()`.
  - Do NOT test only the null-connection case — also test the case where the connection exists but is explicitly closed (`connection.isClosed()` returns `true`).
  - Do NOT forget to set up `given(connection.isClosed()).willReturn(...)` in the Mockito `@Before` setup or in each test, as the mock's default behavior returns `false`.

### Correct Example
```java
@Test
public void testConnection() {
    try (final NoSqlDatabaseManager<?> manager = NoSqlDatabaseManager.getNoSqlDatabaseManager("name", 0, provider)) {
        assertNotNull("The manager should not be null.", manager);
        manager.connectAndStart();
        then(provider).should().getConnection();
        manager.commitAndClose();
    }
}

@Test
public void testWriteInternalNotConnected01() {
    try (final NoSqlDatabaseManager<?> manager = NoSqlDatabaseManager.getNoSqlDatabaseManager("name", 0, provider)) {
        expectedException.expect(AppenderLoggingException.class);
        manager.writeInternal(mock(LogEvent.class));
    }
}
```

### Incorrect Example (Missing startup call, not testing closed connection)
```java
// BAD: Does not test the case where connection.isClosed() returns true
@Test
public void testWriteInternalNotConnected() {
    try (final NoSqlDatabaseManager<?> manager = NoSqlDatabaseManager.getNoSqlDatabaseManager("name", 0, provider)) {
        // Missing: this only tests the null-connection write, not the closed-connection write
        expectedException.expect(AppenderLoggingException.class);
        manager.writeInternal(mock(LogEvent.class));
    }
}
```