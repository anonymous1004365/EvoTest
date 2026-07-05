---
name: alternative-decoding-path-type-handling
description: When a decoder or handler has an alternative decoding path (e.g., falling
  back to a different protocol), tests must send data that exercises both paths using
  the correct data types. This skill helps catch mismatches between expected types
  and actual types in alternative decoding branches.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
- ORDER_DEPENDENCY
test_pattern: PARAMETRIC_TEST
---

# alternative-decoding-path-type-handling

## Instructions

# Alternative Decoding Path Type Handling

## Instructions

- WHEN the TG encounters a protocol decoder (e.g., `AquilaProtocolDecoder`, `TotemProtocolDecoder`) that has multiple decoding branches based on device identifier, message format, or frame type:
  - THEN the TG should identify ALL alternative decoding paths in the `decode` method (e.g., paths that switch on a header byte, device type, or message ID).
  - For EACH alternative path, the TG should test with data that triggers that specific path AND verify the `Position` object has all expected fields set correctly.
  - Pay special attention when an alternative path extracts values using a **different parser or parsing mechanism** than the primary path (e.g., one path uses `parser.next()` and another uses a different parser API).
  - Verify that types of extracted values match what the position objects expect. For example, if one path extracts a numeric field via hex string parsing while another path extracts it as a direct integer, test both.

- WHEN the fix is in a protocol decoder that was previously using a **different protocol's decoder logic** (e.g., buggy code dispatches to a decoder for a different protocol before falling through to its own logic):
  - THEN the TG should test that the fix correctly handles a variety of protocol buffer types (e.g., both `String` types from one path and `CtTypeReference`-like parsed types from another).
  - Test at least one message that goes through the primary/fallback path AND at least one message that goes through the corrected/alternative path.

- WHEN a decoder method has conditional logic on device identity (e.g., `if (deviceId == null)` separating two decoding strategies):
  - THEN test BOTH branches: one test message that triggers the `null` (first-time/unknown) device path, and another test message for the identified device path.

- Common pitfalls:
  - Testing only one protocol decoding path (usually the primary path) and missing bugs in the alternative/fallback path
  - Assuming a protocol ID or header byte without verifying which path it triggers in the decoder
  - Not testing with the specific message format that exercises the fixed branch (e.g., only testing with a format that already succeeded before the fix)
  - Testing only String-type parameters and missing type mismatches with numeric/object type parameters

- Correct example (test with both paths, multiple data types):
  ```java
  // Test primary path (e.g., no device ID known yet)
  Object result1 = decoder.decode(null, channel, 
      new NetworkMessage("*HQ,1234567890,V1,123456..."));
  assertNotNull(result1);
  assertTrue(result1 instanceof Position);
  
  // Test alternative path (e.g., known device)
  Object result2 = decoder.decode(null, channel,  
      new NetworkMessage("*HQ,1234567890,V1,789012..."));
  assertNotNull(result2);
  ```

- Incorrect example (testing only one path with one type):
  ```java
  // Only tests the primary path — misses alternative path bug
  Object result = decoder.decode(null, channel, 
      new NetworkMessage("*HQ,1234567890,V1,123456..."));
  assertNotNull(result);
  ```