---
name: null-url-db-connection-span-reporting
description: When handling database connection tracing with potentially null URLs,
  the TG should test that span reporting does not throw exceptions when the connection
  URL is null. This is critical for JDBC interceptors that create spans based on connection
  metadata.
code_tags:
- ARGUMENT_VALIDATION
- NULL_CHECK
- BOUNDARY_CHECK
test_pattern: EXCEPTION_TEST
---

# null-url-db-connection-span-reporting

## Instructions

# Null URL Database Connection Span Reporting

## Instructions

- WHEN the TG encounters code that creates OpenTracing spans for database connections, and the connection URL might be null (e.g., when no URL is provided in the JDBC connection or DataSource),
- THEN the TG should write a test that:
  1. Creates a JDBC connection or DataSource with a **null URL** (or omits setting the URL entirely)
  2. Executes a SQL statement through the traced connection
  3. Verifies that **no exception is thrown** (no NullPointerException, no IllegalArgumentException) during span creation/reporting
  4. Verifies that exactly **one span** is reported (not zero, not more than one) even with the null URL
  5. Verifies the span contains no unexpected error tags

- The test must verify that the tracing interceptor **gracefully handles** the null URL case, for example by using an empty string or a placeholder URL like `"jdbc:unknown://"` instead of throwing an exception.

- **Common pitfalls to avoid:**
  - Testing only with valid, non-null URLs — the null URL case is the specific edge case that triggers the bug
  - Writing a test that accidentally avoids the null URL path by setting a dummy value (e.g., `"jdbc:h2:mem:test"`)
  - Forgetting to check that spans are actually created (the bug might silently skip span creation when URL is null)
  - Using `assertThrows` expecting an exception — the fix should make the code NOT throw

### Example (Correct Approach)
```java
// Create a traced connection with null URL
DataSource dataSource = ... // e.g., P6DataSource with null URL
Connection connection = dataSource.getConnection(); 
Statement statement = connection.createStatement();
try {
    statement.execute("SELECT 1");
} catch (Exception e) {
    // Some DBs may throw when URL is null, focus on span reporting
}
// Verify span was reported without errors
assertThat(tracer.finishedSpans()).hasSize(1);
```

### Example (Incorrect Approach)
```java
// ❌ Using a valid URL — misses the bug entirely
DataSource dataSource = new P6DataSource(realDataSource);
Connection connection = dataSource.getConnection();
// ... works fine but doesn't test null URL
```