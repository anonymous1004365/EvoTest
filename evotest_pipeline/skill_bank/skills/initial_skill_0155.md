---
name: file-message-body-stream-consumption
description: When testing endpoints that consume file messages, the body may be a
  stream that can only be read once. Tests should verify that browsing or dumping
  messages as XML still returns the body content even after it has been consumed by
  the route.
code_tags:
- VALIDATION
- RESOURCE_MANAGEMENT
- STATE_MUTATION
test_pattern: STATE_TEST
---

# file-message-body-stream-consumption

## Instructions

# File Message Body Stream Consumption Test

## Instructions

- WHEN writing tests for endpoints (File, SEDA, or JMS) that use `BrowsableEndpoint` methods like `browseAllMessagesAsXml()` or `browseRangeMessagesAsXml()`, or methods like `MessageHelper.dumpAsXml()` that read the message body
- THEN ensure the test accounts for the fact that file/seda message bodies can be **stream-based** (e.g., `InputStream`) and may be consumed/drained by the route processor before the browsing method reads them — make the test verify that the body content is still accessible
- Specifically, when a route reads the body via `in.body` (which consumes the stream), THEN test that calling the browsing/dump method **after** route completion still returns the body content (not empty or null)
- Use `MockEndpoint` to assert that the body was received correctly by the route, AND independently call the management/browsing method to assert that the body content is also present in the XML output
- Common pitfall: Testing only that the route processed the body (via mock assertions) without separately checking that the managed endpoint/browsing methods can still produce the body content in XML form after stream consumption
- Common pitfall: Using `in.body` in a route without preserving the original message body (e.g., via `org.apache.camel.util.MessageHelper.resetStreamCache()` or similar)
- Correct approach: After the route has consumed the body, invoke `browseAllMessagesAsXml(true)` or `dumpAsXml()` and assert the output contains the expected body content string (e.g., assert `out.contains("Hello")`)

### Example (correct):
```java
// Route body consumes stream
from(fileEndpoint).to(mockEndpoint);

// After exchange completes, invoke JMX browsing
String out = (String) mbeanServer.invoke(name, "browseAllMessagesAsXml",
    new Object[]{true}, new String[]{"java.lang.Boolean"});
assertNotNull("Should have XML", out);
assertTrue("Should contain the body", out.contains("Hello World"));
```

### Example (incorrect — only checks mock, not the browseable output):
```java
from(fileEndpoint).to(mockEndpoint);
// ✓ mock endpoint receives body
mockEndpoint.assertIsSatisfied();
// ✗ Does not verify that browseAllMessagesAsXml returns the body content
// If the stream was consumed, the XML dump may be empty/missing the body
```