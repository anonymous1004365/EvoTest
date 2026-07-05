---
name: streaming-splitter-ioexception-resource-leak
description: When a streaming splitter (e.g. tokenize-based) encounters an I/O error
  on its input resource, the splitter must stop sending messages downstream immediately.
  This skill helps test that no partially-split messages are delivered after an IOException
  during streaming split processing.
code_tags:
- EXCEPTION_HANDLING
- RESOURCE_MANAGEMENT
- BOUNDARY_CHECK
test_pattern: EXCEPTION_TEST
---

# streaming-splitter-ioexception-resource-leak

## Instructions

# Streaming Splitter IOException Halts Message Delivery

## Instructions

WHEN the TG encounters code that uses a **streaming splitter** (e.g., `.split().tokenize("\n")` or `.split().streaming()`) with an input that can fail with an **IOException** (e.g., file reader, scanner, or other I/O resource):

- THEN the TG should verify that **no messages are delivered** to the downstream route after an IOException occurs during split processing.
- The test should use a **mock endpoint** at the split output (e.g., `mock:split`) to assert that **zero messages** are received.
- The test should configure the file/input URI to point to a file that forces an I/O error (e.g., a corrupt file or a file that triggers a `Scanner` `IOException`), and set `noop=true` and appropriate charset.
- The test should expect that the exchange is **not completed** (e.g., `mock:result` receives 0 messages) and that the **exception is not handled** by the splitter itself (i.e., it propagates to the error handler).
- Common pitfalls:
  - **Testing only success cases** where the input is valid and no IOException occurs — this misses the bug entirely.
  - **Assuming the splitter silently recovers** from I/O errors and continues sending messages — the bug is that partial messages may leak through.
  - **Using an in-memory message body** instead of a real I/O resource — the bug only manifests with actual file/stream I/O that can throw checked exceptions like `IOException`.
  - **Not configuring `noop=true`** — the file consumer may delete the file after reading, causing non-deterministic test failures.

### Correct Test Pattern (catches the bug)

```java
// Given: a route with a streaming splitter reading from a file that will cause IOException
// When: processing the file, the I/O error occurs mid-split
// Then: no messages should be delivered downstream
mockSplit.expectedMessageCount(0);
mockResult.expectedMessageCount(0);

template.sendBody("direct:start", "something");

assertMockEndpointsSatisfied();
```

### Incorrect Test Pattern (misses the bug)

```java
// ❌ Tests only a successful file — never exercises the I/O-error path
mockSplit.expectedMessageCount(3);  // assumes all lines are processed
mockResult.expectedMessageCount(1);

template.sendBody("direct:start", "valid,data,here\nline2,data,here\nline3,data,here");

assertMockEndpointsSatisfied();
// Doesn't test IOException scenario — bug remains undetected
```