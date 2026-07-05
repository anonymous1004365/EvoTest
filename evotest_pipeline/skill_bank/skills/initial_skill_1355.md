---
name: protocol-frame-decoder-factory-fallback
description: When a protocol decoder uses a factory method to create frame decoders
  and an alternative/fallback path exists, test both paths to ensure the correct frame
  decoder type is used. This helps catch bugs where an incorrect decoder (e.g., line-based)
  is used instead of the intended one (e.g., fixed-length).
code_tags:
- VALIDATION
- STATE_MUTATION
- PROTOCOL_FRAME_DECODER_FACTORY
test_pattern: STATE_TEST
---

# protocol-frame-decoder-factory-fallback

## Instructions

# Protocol Frame Decoder Factory Fallback Test

## Instructions

WHEN the TG encounters a protocol decoder class that has a **factory method** (typically named `createFrameDecoder` or similar) which can return different types of frame decoders (e.g., `LineBasedFrameDecoder`, `FixedLengthFrameDecoder`, `DelimiterBasedFrameDecoder`, etc.) based on configuration flags or protocol identifiers, and that factory contains an **alternative/fallback path** (e.g., `if (hasFlag)` → one decoder, `else` → another decoder):

- THEN the TG should write a **state test** that:
  1. Creates an instance of the protocol decoder with the configuration that triggers the **alternative/fallback path** (the path that is NOT the primary one).
  2. Calls the `createFrameDecoder()` factory method (or equivalent).
  3. Asserts that the returned decoder is of the **expected type** (e.g., `assertTrue(decoder instanceof FixedLengthFrameDecoder)`).
  4. Also asserts that the decoder has the expected **configuration** (e.g., correct frame length, correct delimiter).

- Common pitfalls to avoid:
  - ❌ Testing only the **primary** path (e.g., only testing the LineBasedFrameDecoder) and ignoring the fallback path.
  - ❌ Only verifying that the decoder is non-null, without checking its **specific type** or **configuration parameters**.
  - ❌ Assuming that because one path works, the other path also produces a correctly configured decoder.

**Incorrect test example** (too weak — only checks primary path):
```java
TmgProtocolDecoder decoder = new TmgProtocolDecoder(new Protocol("tmg"));
FrameDecoder frameDecoder = decoder.createFrameDecoder();
assertNotNull(frameDecoder);
```

**Correct test example** (tests both paths, checks type and configuration):
```java
@Test
public void testCreateFrameDecoderForFixedLength() {
    // Setup: initialize protocol decoder with the flag that triggers the fallback path
    Protocol protocol = new Protocol("tmg", /* flags with the alternative bit */);
    TmgProtocolDecoder decoder = new TmgProtocolDecoder(protocol);
    
    // Act
    FrameDecoder frameDecoder = decoder.createFrameDecoder();
    
    // Assert: verify the decoder is the expected type with correct configuration
    assertTrue("Expected FixedLengthFrameDecoder", 
               frameDecoder instanceof FixedLengthFrameDecoder);
    FixedLengthFrameDecoder fixedDecoder = (FixedLengthFrameDecoder) frameDecoder;
    // Verify the frame length is as expected (e.g., 4 bytes, 10 bytes, etc.)
    // (Exact value depends on the protocol specification)
}

@Test
public void testCreateFrameDecoderForLineBased() {
    // Setup: initialize with default/no flag
    Protocol protocol = new Protocol("tmg");
    TmgProtocolDecoder decoder = new TmgProtocolDecoder(protocol);
    
    // Act
    FrameDecoder frameDecoder = decoder.createFrameDecoder();
    
    // Assert: verify the decoder is line-based
    assertTrue("Expected LineBasedFrameDecoder", 
               frameDecoder instanceof LineBasedFrameDecoder);
}
```

WHEN the TG sees that the protocol decoder's factory method has a conditional branch that **modifies a shared/instance state** (e.g., sets a field like `this.frameLength = X` or `this.useLineBased = false`) differently depending on the path taken:

- THEN the TG should also test that **post-conditions** on the protocol decoder object are correct after calling the factory method for each path.
- Verify that:
  - Fields that are set in one path are **not** also set (or set incorrectly) in the other path.
  - No **stale state** from a previous call leaks into the next call (e.g., calling the factory twice with different flags).

**Example of state mutation check:**
```java
@Test
public void testFrameDecoderStateIsConsistent() {
    // Test fallback path
    TmgProtocolDecoder decoder = new TmgProtocolDecoder(/* fallback flag */);
    FrameDecoder fallbackDecoder = decoder.createFrameDecoder();
    
    // Verify the decoder's internal state matches expectations
    assertEquals(4, decoder.getFrameLength()); // example assertion
    assertTrue(fallbackDecoder instanceof FixedLengthFrameDecoder);
}
```