---
name: alternative-protocol-decoding-validation
description: When testing protocol decoders with alternative decoding paths, test all branches including the fallback. The decoder processes frame bytes with different paths based on frame content, and the alternative path may fail (e.g., NPE) due to missing state or null checks.
code_tags: ['EXCEPTION_HANDLING', 'VALIDATION', 'NULL_CHECK', 'ALTERNATIVE_PROTOCOL_DECODING']
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoding-validation

## Instructions

# Alternative Protocol Decoding Validation

## Instructions

- WHEN the TG encounters a protocol decoder that has an alternative/fallback decoding path (e.g., when primary decoding fails and a secondary decode method is invoked), THEN the TG should write parametric tests that exercise ALL decoding paths, including the fallback. Specifically, craft input byte arrays/fluxes that trigger the alternative path.

- WHEN the alternative decoding path involves accessing or manipulating a `Channel` or connection state (e.g., writing back to the channel, checking channel attributes), THEN the TG should test with a `null` or mock `Channel` to verify that the decoder handles missing connection context gracefully (e.g., does not throw NullPointerException).

- The test should verify that for inputs triggering the alternative path, the decoder returns empty/error gracefully (e.g., returns `Flux.empty()`, returns `null`, or emits a well-formed error signal) rather than throwing an uncaught exception.

- Common pitfalls to avoid:
  - Testing only the primary/happy decoding path and assuming the alternative path works identically.
  - Forgetting to test with `null` channel or connection-less contexts where alternative decoding may be invoked.

### Example (Correct)
```java
// Test alternative path with null channel
@Test
public void testDecodeAlternativePathWithNullChannel() {
    Tr900ProtocolDecoder decoder = new Tr900ProtocolDecoder(null);
    ByteBuf buf = Unpooled.wrappedBuffer(new byte[]{...}); // input that triggers alternative path
    // Should not throw NPE; should return empty or handle gracefully
    assertDoesNotThrow(() -> {
        Flux<?> result = decoder.decode(null, null, buf);
        // Optionally verify result produces no items
    });
}
```

### Example (Incorrect)
```java
// BAD: Only tests primary path
@Test
public void testDecodePrimaryPath() {
    Tr900ProtocolDecoder decoder = new Tr900ProtocolDecoder(null);
    ByteBuf buf = Unpooled.wrappedBuffer(new byte[]{...}); // only primary path triggers
    // Never tests the alternative path where the bug manifests
}
```