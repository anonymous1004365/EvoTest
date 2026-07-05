---
name: endpoint-parsing-hostname-status-separator
description: When parsing endpoint strings that combine hostname/URL segments with
  status or label information, test that the parsing correctly handles cases where
  the hostname itself contains the separator character (e.g., periods, colons, or
  slashes). The TG should verify that only the intended separator (e.g., the last
  colon, the first slash) is used to split between the hostname and the status, not
  any separator occurring within the hostname itself.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- STATE_MUTATION
- ENDPOINT_PARSING_URL_DECODING
test_pattern: PARAMETRIC_TEST
---

# endpoint-parsing-hostname-status-separator

## Instructions

# Endpoint Parsing: Hostname/Status Separator Collision

## Instructions

### WHEN the TG encounters:
- A method that parses an endpoint string by splitting on a delimiter (e.g., `:` , `/`, `|`) where one segment represents a hostname/URL and another segment represents a status/label/type.
- The method uses `String.split()` or `String.substring()` to extract the two parts from a single input string.
- The hostname/URL portion may naturally contain the same delimiter character (e.g., an IPv6 address `[::1]` contains colons, a dotted hostname like `host.example.com` contains periods, or a URL path contains slashes).

### THEN the TG should:
1. **Test with hostnames that contain the separator character** — for instance, if the split character is `:`, test with input like `"host:8080:status"` or `"hostname:status"` where the hostname is an IPv6-like address containing colons. Verify that only the **last** (or **first**, as intended by the spec) occurrence of the delimiter is used as the split point, not an arbitrary one.
2. **Write a parametic test** that passes a variety of inputs including:
   - Simple endpoint with no separator collision: `"hostname:status"` → hostname=`"hostname"`, status=`"status"`
   - Endpoint where hostname itself contains the separator: e.g., if parsing on `:`, use `"host.sub.domain:status"` or `"[::1]:status"` → the hostname should be `"host.sub.domain"` not `"host"`, and status=`"status"`
   - Endpoint with multiple separators and trailing/leading whitespace
3. **Assert the exact decomposed parts** — verify that the hostname portion and the status/label portion are correctly identified, and that no characters from one leak into the other.
4. **Expect specific failure modes on the buggy version**: The buggy code will likely return an incorrect hostname (truncated) when the hostname contains the delimiter, causing `equals()` or `contains()` assertions to fail, or resulting in `ArrayIndexOutOfBoundsException` if the split produces fewer/more parts than expected.

### Common pitfalls to avoid:
- ❌ Testing only with simple inputs where the hostname has no separator collision (e.g., only `"simplehost:active"`), missing the case where the hostname itself contains the delimiter.
- ❌ Using `String.split(delimiter)` without limiting the number of parts (e.g., `split(":")` instead of `split(":", 2)`) — this causes the hostname to be truncated if it contains the delimiter.
- ❌ Forgetting to trim whitespace from each part after splitting.
- ❌ Assuming the hostname is always a simple DNS name without delimiters like `.`, `:`, or `/`.

### Examples:

**Correct test (parametrized, JUnit 5 style):**
```java
@ParameterizedTest
@CsvSource({
    "myhost,UP",
    "my.host.com,UP",
    "[::1],UP",
    "host:8080,UP"
})
void testParseEndpointCorrectlyWithHostnameContainingDelimiter(String hostname, String status) {
    String input = hostname + ":" + status;
    // The expected behavior: only the LAST colon is the separator
    // hostname should be the full hostname, status should be "UP"
    Endpoint endpoint = NodesStatus.parseEndpoint(input);
    assertEquals(hostname, endpoint.getHostname());
    assertEquals(status, endpoint.getStatus());
}
```

**Incorrect test (missing the separator-collision case):**
```java
// ❌ BAD: Only tests simple hostnames without delimiter collision
@Test
void testParseEndpointSimple() {
    Endpoint endpoint = NodesStatus.parseEndpoint("localhost:UP");
    assertEquals("localhost", endpoint.getHostname());
    assertEquals("UP", endpoint.getStatus());
    // Misses the bug entirely when hostname is like "my.host.com:UP"
    // The buggy code would return "my" as the hostname instead of "my.host.com"
}
```

### When writing the test:
- Use `@ParameterizedTest` (JUnit 5) or `@RunWith(Parameterized.class)` (JUnit 4) to cover multiple cases concisely.
- For each input, explicitly verify both the hostname part AND the status part are extracted correctly.
- Also test edge cases like empty hostname (`":UP"`), empty status (`"hostname:"`), and inputs with extra whitespace (`" hostname : UP "`).