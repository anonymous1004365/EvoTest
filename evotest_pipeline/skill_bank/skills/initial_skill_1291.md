---
name: endpoint-string-parsing-validation
description: When parsing endpoint/host:port strings from status or configuration,
  test that both IPv4 and IPv6 addresses (including those with hostnames like "::1%eth0")
  are correctly handled without truncation or format errors. The core issue is that
  parsing logic may split or substring the host part incorrectly when the string contains
  zone IDs, percent-encoded characters, or hostname suffixes.
code_tags:
- PARSE_ERROR_HANDLING
- INPUT_PARSING
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# endpoint-string-parsing-validation

## Instructions

# Endpoint String Parsing Validation

## Instructions

- WHEN the TG encounters code that parses an endpoint or host:port string from a larger status/configuration string (e.g., splitting by `:` or extracting host and port from `[host]:port` or `host:port` format)
- THEN the TG should write a **PARAMETRIC_TEST** that tests multiple endpoint string formats including:
  - IPv4 addresses (e.g., `"192.168.1.1:9042"`)
  - IPv6 addresses with brackets (e.g., `"[::1]:9042"`)
  - IPv6 addresses with zone IDs and hostnames (e.g., `"::1%eth0:9042"` where `eth0` is a network interface name)
  - IPv6 addresses with brackets and zone IDs (e.g., `"[fe80::1%eth0]:9042"`)
  - Strings that contain a hostname appended to an IPv6 address (e.g., `"::1%lo:9042"`)
  - The test should verify that parsing produces the **correct host part** (e.g., `"::1"`) and **correct port part** (e.g., `9042`), even when the input contains extra characters after the IP address
  - Expect that on the **buggy** version, parsing code that uses simple `split(":")` or naive `lastIndexOf(":")` will produce **incorrect host**: either truncating the zone ID, including the port in the host, or mismatching the port value
  - Use `assertEquals("::1", host)` and `assertEquals(9042, port)` as the expected correct values for the buggy example

- Common pitfalls to avoid:
  - Testing only with simple IPv4 or bracket-enclosed IPv6 addresses without zone IDs/hostname suffixes
  - Assuming that `lastIndexOf(":")` is sufficient to find the port separator in IPv6 addresses
  - Using `String.split(":")` without considering that IPv6 addresses contain multiple colons
  - Not testing with zones/interface names that contain digits (e.g., `"eth0"`, `"lo"`)
  - Not testing with the specific malformed input that triggers the bug (e.g., `"127.0.0.1:0"` or `"::1%eth0:9042"` where the zone ID contains the word "eth")

### Correct test example (should catch the bug):
```java
@Test
public void testParseEndpointWithIPv6AndHostname() {
    String input = "::1%eth0:9042";
    // This should parse host="::1", port=9042
    // Buggy version might produce host="::1%eth0" or port=0
    Endpoint endpoint = Endpoint.parse(input);
    assertEquals("::1", endpoint.getHost());
    assertEquals(9042, endpoint.getPort());
}
```

### Incorrect test example (would NOT catch the bug):
```java
@Test
public void testParseEndpointIPv6() {
    String input = "[::1]:9042";
    // This passes on buggy code because brackets make parsing straightforward
    Endpoint endpoint = Endpoint.parse(input);
    assertEquals("::1", endpoint.getHost());
    assertEquals(9042, endpoint.getPort());
}
```