---
name: decoding-protocol-handler-registration
description: When writing protocol decoder tests, ensure that the decoder is properly
  registered in the pipeline factory and that all alternative decoding paths are tested.
  This skill helps catch bugs where protocol handlers fail silently due to missing
  decoder registration or incorrect handler ordering.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
- VALIDATION
- TYPE_CONVERSION
test_pattern: INTERACTION_TEST
---

# decoding-protocol-handler-registration

## Instructions

# Protocol Decoder Handler Registration Skill

## Instructions

- WHEN the TG encounters a protocol decoder class that uses a pipeline factory to register message handlers (e.g., `ChannelPipeline`, `PipelineFactory`, `addLast`, `addFirst`)
- THEN the TG should verify that each expected decoder/handler is properly **registered in the pipeline** and that the **decoder's message type mapping** (e.g., frame decoder → handler decoder → handler) works end-to-end by testing the decoder with a realistic input binary/string message
- Include concrete examples: test with valid hex strings, valid ASCII payloads, invalid payloads, and edge cases like empty messages or messages with missing fields
- The test must verify that after decoding, the correct handler method is invoked and processes the message — if the decoder is not registered or the handler chain breaks, the test will fail via an unhandled message or an exception like `NoSuchElementException`, `IllegalStateException`, or `UnsupportedOperationException`

### Common Pitfalls
- Testing the decoder in isolation but not verifying the handler chain invokes the correct business method (e.g., decoding works but the handler is never called)
- Assuming that if a single decoding path works, all alternative paths (e.g., different device IDs, alternate frame formats) also work
- Using only String types in test messages when the decoder may expect `ByteBuf` or hex-encoded byte arrays
- Forgetting to register the decoder in the pipeline before calling `channelRead` or equivalent

### Correct Test Example
```java
@Test
public void testDecodeValidatesHandlerRegistration() {
    LaipacProtocolDecoder decoder = new LaipacProtocolDecoder();
    ChannelPipeline pipeline = Channels.pipeline();
    // Register the decoder and handler in correct order
    pipeline.addLast("decoder", decoder);
    pipeline.addLast("handler", new MyHandler());
    
    // Send a realistic message (e.g., hex string or byte array)
    String msg = "$$HQ1234567890,123456,000000,A,1234.5678,N,12345.6789,E,0.0,0.0,100.0,0,0,0,0,0,0,0,0,0*XX";
    decoder.decode(null, null, msg); // or pipeline.fireMessageReceived(msg)
    
    // Verify that the handler received the decoded message
    // (use mock/spy to verify interaction)
}
```

### Incorrect Test Example (missing registration check)
```java
@Test
public void testDecodeFailsSilently() {
    LaipacProtocolDecoder decoder = new LaipacProtocolDecoder();
    // BUG: No pipeline setup — decoder is never attached to a handler chain
    String msg = "$$HQ1234567890,123456,A*XX";
    decoder.decode(null, null, msg); // May succeed in isolation but crash in production
}
```