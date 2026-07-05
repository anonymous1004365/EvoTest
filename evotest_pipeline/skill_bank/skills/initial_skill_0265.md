---
name: connection-pool-elide-masked-passwords
description: When collecting or proxying database connection properties (especially
  passwords) from a ConnectionPoolDataSource, elide (remove) "password" entries to
  prevent exposing credentials in metadata. Test that password properties are stripped
  while non-sensitive properties survive.
code_tags:
- STATE_MUTATION
- BOUNDARY_CHECK
test_pattern: STATE_TEST
---

# connection-pool-elide-masked-passwords

## Instructions

# Connection Pool Elide Masked Passwords

## Instructions

- WHEN the TG encounters code that copies or wraps HikariCp `PoolEntry` connection properties from a `ConnectionPoolDataSource` — specifically where a `Properties` object is populated from `ConnectionPoolDataSource.getPassword()` or from `ProxyConnection.getClientInfo()` — 
- THEN the TG should test that **"password" property keys are explicitly removed/elided** from the resulting properties collection, and that all non-sensitive properties are preserved.
- Include a test that:
  1. Sets up a mock `ConnectionPoolDataSource` that returns a `Properties` object containing both a `"password"` key with a non-null value and at least one non-sensitive property key (e.g., `"user"`, `"applicationName"`, `"_clientId"`).
  2. Exercises the property-collection logic (e.g., create a `PoolEntry` or `HikariProxyConnection` and call `getClientInfo()`).
  3. Asserts that the returned `Properties` does NOT contain the `"password"` key (i.e., `assertNull(props.get("password"))` or `assertFalse(props.containsKey("password"))`).
  4. Asserts that the non-sensitive property keys are still present in the result.
  5. Asserts that **no other properties are lost** — the non-sensitive entries must be fully preserved.

- **Common pitfalls:**
  - Adding the password as a nullable key and testing only null-password scenarios — the bug is that password is **never removed**, so test must set a non-null value for `"password"`.
  - Testing only that `getPassword()` on the `ConnectionPoolDataSource` is called, not that the password is actually **removed** from the `Properties` object returned by `getClientInfo()`.
  - Forgetting to include non-sensitive properties to verify they are not accidentally removed along with the password.
  - Testing on a proxy connection that is closed or invalid, causing early failure before the property-eliding logic runs.

- **Correct example:**
```java
@Test
public void testPasswordIsElidedFromClientInfo() throws SQLException {
    Properties originalProps = new Properties();
    originalProps.setProperty("password", "secret123");
    originalProps.setProperty("user", "admin");
    
    ConnectionPoolDataSource mockDs = mock(ConnectionPoolDataSource.class);
    when(mockDs.getPassword()).thenReturn("secret123");
    
    PoolEntry entry = ... // create PoolEntry with mockDs
    HikariProxyConnection conn = entry.createProxyConnection(...);
    // If the buggy code copies password into clientInfo without removal:
    Properties clientInfo = conn.getClientInfo();
    assertNull("password must be removed from clientInfo", clientInfo.get("password"));
    assertEquals("admin", clientInfo.get("user"));
}
```

- **Incorrect example (would pass on buggy code, should fail):**
```java
@Test
public void testPasswordIsElidedFromClientInfo() throws SQLException {
    Properties clientInfo = conn.getClientInfo();
    // BAD: only checks password is not null; does NOT check it's removed
    assertNotNull("password should be non-null", clientInfo.get("password"));
    // BAD: no assertion that non-sensitive keys survive
}
```