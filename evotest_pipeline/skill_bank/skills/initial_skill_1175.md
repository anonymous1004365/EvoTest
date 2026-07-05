---
name: alternative-protocol-decode-path-validation
description: When a protocol decoder has multiple decoding paths (alternative parsing
  branches), test ALL paths including edge cases where alternative decoding produces
  null or unexpected results. This skill helps catch missing null checks and unvalidated
  results from alternative frame decoders.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- VALIDATION
- ALTERNATIVE_PROTOCOL_DECODING
test_pattern: EXCEPTION_TEST
---

# alternative-protocol-decode-path-validation

## Instructions

# Alternative Protocol Decode Path Validation

## Instructions

- WHEN the TG encounters a protocol decoder class that implements a `decode` method calling `getFrameDecoder()` (or similar factory/accessor methods that return alternative decoders like `new Tlt2hFrameDecoder()`), THEN it should write tests that exercise ALL available decoding paths, not just the primary one.

- WHEN the protocol uses multiple decoders (e.g., a default decoder and an alternative decoder), THEN tests MUST include at least one test case that triggers the alternative decoder path. For example, if a protocol decoder calls `pipeline.addLast(getFrameDecoder())`, verify that the alternative decoder returns a non-null result.

- WHEN testing alternative decoding paths, THEN the test should verify that the decoder does NOT throw a NullPointerException when the alternative decoder is used. Verify by passing data that exercises the alternative path and asserting no exception occurs during channelRead/decode.

- Common pitfalls:
  - Testing only the primary/default decoder path and assuming the alternative decoder works
  - Not providing test data that exercises the alternative decoder's specific logic
  - Not checking for null return values from alternative decoders before they are used downstream
  - Only testing happy paths and ignoring the case where an alternative decoder might internally fail

- For protocol decoder tests, include buffers with varying data lengths/content to trigger the alternative decoder's internal switching logic (e.g., different packet headers, incomplete data, boundary values).

- Example (correct): Test both decoding paths by sending data that triggers the alternative decoder:
```java
// Test data that triggers the alternative decoder path
byte[] altDecoderData = {0x01, 0x02, 0x03};
ByteBuf buf = Unpooled.wrappedBuffer(altDecoderData);
assertDoesNotThrow(() -> decoder.decode(null, null, buf));
```

- Example (incorrect — only tests primary path):
```java
// Only tests the default decoder — missing the alternative decoder path
byte[] standardData = {0x00, 0x01};
ByteBuf buf = Unpooled.wrappedBuffer(standardData);
Object result = decoder.decode(null, null, buf);
// Bug goes undetected because alternative decoder path is never exercised
```