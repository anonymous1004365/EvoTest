---
name: fqdn-hostname-extraction-validation
description: When extracting a hostname from a fully qualified domain name (FQDN)
  via substring operations, test that FQDNs which look like raw IP addresses (e.g.
  "192.168.254.254") are handled correctly — the hostname should remain the full IP
  string rather than the first segment before the dot.
code_tags:
- NULL_CHECK
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# fqdn-hostname-extraction-validation

## Instructions

# FQDN Hostname Extraction Validation

## Instructions

- WHEN the TG encounters a method like `NetUtils.getHostnameFromFQDN(String fqdn)` which extracts a hostname by taking the substring before the first period (`.`), or any constructor/logic that uses such a method to derive a hostname field from an FQDN — e.g. `this.hostName = NetUtils.getHostnameFromFQDN(this.fqdnHostName)` — where the FQDN could potentially be a raw IP address string (e.g. `"192.168.254.254"`):

- THEN the TG should write a test where:
  1. The CanonicalHostName (or FQDN input) is set to an IP-like string containing dots, such as `"192.168.254.254"` or `"10.0.0.1"`.
  2. The test verifies that when the FQDN equals the IP address (i.e., hostname resolution failed or returned the IP textual representation), the extracted hostname is the **full IP string** (e.g. `"192.168.254.254"`), **not** just the first segment before the first dot (e.g. not `"192"`).
  3. This can be tested by mocking `InetAddress` to return an IP string from `getCanonicalHostName()` and `getHostAddress()`, constructing the location object, and asserting `getHostname()` equals the full IP address string.
  4. Also verify that `getFQDNHostname()` returns the raw IP string.

- Common pitfalls to avoid:
  - Testing only hostname-style FQDNs (e.g. `"worker2.cluster.mycompany.com"` or `"worker10"`) and forgetting the IP-as-FQDN case.
  - Assuming that an FQDN with dots always represents a multi-level domain name (it could be an IPv4 dotted-decimal string).
  - Using a real `InetAddress.getByName()` with an actual IP — the test MUST mock `getCanonicalHostName()` and `getHostAddress()` to return the same IP string to simulate the "hostname resolution failed" code path.

### Examples

**Correct test (this catches the bug):**
```java
@Test
public void testGetHostnameWithIPAddress() {
    InetAddress address = mock(InetAddress.class);
    when(address.getCanonicalHostName()).thenReturn("192.168.254.254");
    when(address.getHostName()).thenReturn("192.168.254.254");
    when(address.getHostAddress()).thenReturn("192.168.254.254");
    when(address.getAddress()).thenReturn(new byte[] {(byte) 192, (byte) 168, (byte) 254, (byte) 254});

    TaskManagerLocation info = new TaskManagerLocation(ResourceID.generate(), address, 54152);
    
    assertEquals("192.168.254.254", info.getHostname());
    assertEquals("192.168.254.254", info.getFQDNHostname());
}
```

**Incorrect test (does not catch the bug):**
```java
@Test
public void testGetHostnameWithFQDN() {
    InetAddress address = mock(InetAddress.class);
    when(address.getCanonicalHostName()).thenReturn("worker2.cluster.mycompany.com");
    when(address.getHostName()).thenReturn("worker2.cluster.mycompany.com");
    when(address.getHostAddress()).thenReturn("127.0.0.1");

    TaskManagerLocation info = new TaskManagerLocation(ResourceID.generate(), address, 19871);
    assertEquals("worker2", info.getHostname());
    // This works fine — the bug only manifests when the FQDN is an IP address with dots
}
```