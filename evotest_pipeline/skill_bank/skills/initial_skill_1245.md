---
name: query-string-parameter-null-check
description: When protocol decoders extract device identity or data from HTTP query
  string parameters, suspect that the code does not check for null before calling
  .get(0) on the parameter list, which can cause a NullPointerException if a required
  parameter is missing. Use this skill to test missing required parameters like UserName
  or LOC.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# query-string-parameter-null-check

## Instructions

# Query String Parameter Null Check

## Instructions

- WHEN the TG encounters a protocol decoder that uses `QueryStringDecoder` to extract parameters from an HTTP request URI (e.g., `decoder.getParameters().get("paramName").get(0)`)
- THEN the TG should write tests that pass HTTP requests with missing key query parameters to verify the decoder handles `null` gracefully:
  - If the parameter is used for device session lookup (e.g., `"UserName"`, `"id"`, `"imei"`), the decoder should return `null` (no position decoded) rather than throwing a NullPointerException.
  - If the parameter is used for data payload (e.g., `"LOC"`), the decoder should return `null` rather than throwing a NullPointerException.
- Use `DefaultHttpRequest` with `HttpMethod.GET` to construct HTTP requests, then pass them to `decode()` (or via the `request()` helper if available) to verify behavior.
- The test must check that the decoder does NOT throw an exception when each required parameter is individually missing. The expected result on the buggy version is a `NullPointerException`; on the fixed version, the decoder returns `null`.

### Common pitfalls to avoid:
- Testing only with valid, complete requests — this misses the null-handling bug entirely.
- Testing only one missing parameter — test each required parameter individually (e.g., UserName missing, LOC missing).
- Assuming missing parameters cause the decoder to return `null` on the buggy version — they cause an NPE instead.
- Forgetting to use the correct HTTP request construction (use `DefaultHttpRequest` with the URI containing the missing parameter).
- Using the `request()` helper with a raw string instead of building a proper `HttpRequest` object when testing missing parameters.

### Example (correct):
```java
// Tests that missing UserName parameter returns null instead of throwing NPE
PathAwayProtocolDecoder decoder = new PathAwayProtocolDecoder(new PathAwayProtocol());

// Missing UserName parameter
assertNull(decoder.decode(null, null, new DefaultHttpRequest(
        HttpVersion.HTTP_1_1, HttpMethod.GET, "/?Password=pass&LOC=$PWS,...")));

// Missing LOC parameter  
assertNull(decoder.decode(null, null, new DefaultHttpRequest(
        HttpVersion.HTTP_1_1, HttpMethod.GET, "/?UserName=name&Password=pass")));
```

### Example (incorrect — does not catch the bug):
```java
// Only tests the happy path — does not test missing parameters
verifyPosition(decoder, request("?UserName=name&Password=pass&LOC=$PWS,..."));
```

### Required imports:
```java
import org.jboss.netty.handler.codec.http.DefaultHttpRequest;
import org.jboss.netty.handler.codec.http.HttpMethod;
import org.jboss.netty.handler.codec.http.HttpVersion;
```