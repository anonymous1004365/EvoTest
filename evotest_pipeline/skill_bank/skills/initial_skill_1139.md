---
name: alternative-protocol-decoding-path
description: When a protocol decoder has an alternative decoding path that relies on a fallback (e.g. String parsing), the TG should test with inputs that trigger that fallback path to ensure it handles atypical but valid parameters correctly.
code_tags: ['ALTERNATIVE_PROTOCOL_DECODING', 'VALIDATION']
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoding-path

## Instructions

# Alternative Protocol Decoding Path Validation

## Instructions

- WHEN the TG encounters a protocol decoder class (e.g. `FlexCommProtocolDecoder`) that extends a base decoder and contains a decoding method (e.g. `decode`) that processes a typed parameter (e.g. `Channel`, `SocketAddress`, `Object`), AND there exists an alternative/fallback decoding path that handles a different parameter type (e.g. method overloads for `String` vs `CtTypeReference` vs other types):
  - **THEN** the TG MUST write a parameterized test that passes each supported parameter type variant to the decoder. The test should verify that the correct decoding logic is invoked for each type.
  - **Identify the types** that the decoder's alternative path handles. Look for method overloads or type-checks (`instanceof`) in the decoding logic that branch on parameter type.
  - **Create test inputs** for each distinct type branch. For each input, invoke the decoder and assert that no exception is thrown and that the result contains expected decoded data.
  - **Verify** that the test passes on the fixed version and fails (or throws an unexpected exception) on the buggy version.
  - **Common pitfall**: Testing only one parameter type (e.g. only `String`) and missing the alternative branch (e.g. `CtTypeReference` or other object types). This leaves the alternative decoding path untested.
  - **Common pitfall**: Assuming the decoder always validates parameter types the same way — the bug may be that one branch lacks validation while another branch includes it. Test both.

## Example

Consider a protocol decoder with two decode methods: one that accepts `String` parameters via a template, and another that accepts `CtTypeReference<?>` parameters. The buggy version may have the alternative path (e.g. for `String`) that passes through without proper validation of the template parameter, causing a `ClassNotFoundException`.

**Correct test approach (parameterized):**

```java
@Test
public void testDecodeWithStringParameter() {
    FlexCommProtocolDecoder decoder = new FlexCommProtocolDecoder();
    // String parameter triggers the alternative path
    decoder.decode(channel, remoteAddress, "someStringParam");
    // Assert expected decoded result or that no exception is thrown
    assertNotNull(result);
}

@Test
public void testDecodeWithCtTypeReferenceParameter() {
    FlexCommProtocolDecoder decoder = new FlexCommProtocolDecoder();
    // CtTypeReference parameter triggers the normal path
    decoder.decode(channel, remoteAddress, someCtTypeReference);
    assertNotNull(result);
}
```

**Incorrect test approach (one-type only):**

```java
// BAD: Only tests the CtTypeReference path, missing the String alternative path
@Test
public void testDecode() {
    FlexCommProtocolDecoder decoder = new FlexCommProtocolDecoder();
    decoder.decode(channel, remoteAddress, someCtTypeReference);
    assertNotNull(result);
    // The test passes on buggy version too, missing the bug entirely
}
```