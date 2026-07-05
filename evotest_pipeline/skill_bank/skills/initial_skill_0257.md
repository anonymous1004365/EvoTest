---
name: socket-appender-protocol-null-check
description: When a SocketAppender is created with a protocol that is used to construct
  a socket factory, the protocol field must not be null. The TG should verify that
  null/nonexistent protocol values do not cause a NullPointerException during appender
  creation.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# socket-appender-protocol-null-check

## Instructions

# SocketAppender Protocol Null-Value Handling

## Instructions

- WHEN the TG encounters code that uses a `Protocol` enum (from `org.apache.logging.log4j.core.net.Protocol`) to select a TCP or SSL socket factory — for example, `Protocol.toName("value")` or passing a protocol string to `SocketAppender.newBuilder().setProtocol(...)` — and the protocol string might be null, empty, or unknown
- THEN the TG should write a test that invokes `SocketAppender.createAppender(...)` or builds a `SocketAppender` using `SocketAppender.newBuilder()` with a **non-existent or null protocol value** (e.g., `"nonexistent"`, `null`, or empty string), and verify that:
  1. The appender handles the case gracefully and throws a clear, descriptive exception (e.g., `IllegalArgumentException`, or the builder returns `null` without throwing NPE)
  2. No `NullPointerException` is thrown for user-supplied protocol values that do not match any known `Protocol` constant
- Include a test that passes **both valid and invalid protocol values**: valid values like `"TCP"`, `"SSL"`, and invalid values like `"NONEXISTENT"`, `null`, or `""`
- Common pitfalls:
  - Testing only with valid protocol values (e.g., `"TCP"` and `"SSL"`) but not with invalid/unknown values
  - Assuming that `Protocol.toName(str)` or any `valueOf` lookup returns a non-null value without checking if the input string is valid
  - Omitting the null input test case entirely
- Example correct test pattern (pseudo-code):
  ```java
  @Test
  public void testCreateAppenderWithInvalidProtocol() {
      assertThrows(IllegalArgumentException.class, () -> {
          SocketAppender.createAppender("invalidProtocol", ...);
      });
  }
  @Test
  public void testCreateAppenderWithNullProtocol() {
      assertThrows(IllegalArgumentException.class, () -> {
          SocketAppender.createAppender(null, ...);
      });
  }
  ```
- Example incorrect test pattern (too narrow):
  ```java
  @Test
  public void testCreateAppenderWithTCP() {
      // Only tests valid protocol — misses the NPE bug entirely
      SocketAppender appender = SocketAppender.createAppender("TCP", ...);
      assertNotNull(appender);
  }
  ```