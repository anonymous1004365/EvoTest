---
name: protocol-message-type-validation
description: When a protocol decoder constructs position objects and applies type-dependent value handling, test with all expected message types and verify that the correct parsing logic is applied for each type. This skill catches bugs where a value from a position message is incorrectly applied to a field in a non-matching message type.
code_tags: ['ARGUMENT_VALIDATION', 'TYPE_CONVERSION', 'VALIDATION']
test_pattern: PARAMETRIC_TEST
---

# protocol-message-type-validation

## Instructions

# Protocol Message Type Validation

## Instructions

- WHEN a protocol decoder processes multiple message types (e.g., position reports, status messages, alarm events, heartbeat) and conditionally sets fields on a position or device object based on the message type
- THEN write parametric tests that:
  1. Create sample protocol messages for each distinct message type the decoder supports
  2. For each message type, verify that only the fields relevant to that type are set, and fields relevant to other types remain at their default values (e.g., null, 0.0, false)
  3. Include messages where fields that should be mutually exclusive are set simultaneously, then verify no cross-contamination between types

- Concrete example for a message with deviceId, position (lat/lon/course/speed/time), and type-dependent attributes like ignition (for type=position) vs. battery level (for type=status):
  - The test should send a "position" type message with ignition=true and speed=50, then assert position.getSpeed() == 50 and position.getAttributes().get(Position.KEY_IGNITION) == true
  - The test should send a "status" type message with battery=80 and speed=0 (or absent), then assert position.getAttributes().get(Position.KEY_BATTERY) == 80 and position.getSpeed() (if default) == 0.0
  - The test should NOT see speed from one type leaking into the other

- Common pitfalls to avoid:
  - Testing only one message type (e.g., only "position" messages) while other types have different parsing logic
  - Assuming that all message types populate the same set of fields (e.g., assuming speed is always present)
  - Not testing the default/zero values of fields that should NOT be affected by a given message type
  - Forgetting to include type-identifying byte sequences or headers in test payload bytes

- Example (correct):
  ```
  // Test position type
  byte[] posMsg = createPositionMessage(deviceId, 12.34, 56.78, 90.0, 50, timestamp, true, 0);
  Position pos = decoder.decode(null, null, posMsg);
  assertEquals(50, pos.getSpeed(), 0.001);
  assertNotNull(pos.getAttributes().get(Position.KEY_IGNITION));
  
  // Test status type
  byte[] statusMsg = createStatusMessage(deviceId, 80, timestamp, "ok");
  Position status = decoder.decode(null, null, statusMsg);
  assertEquals(80, (int) status.getAttributes().get(Position.KEY_BATTERY));
  assertEquals(0.0, status.getSpeed(), 0.001); // speed should not change
  ```

- Example (incorrect — only tests one type):
  ```
  byte[] msg = createPositionMessage(deviceId, 12.34, 56.78, 90.0, 50, timestamp, true, 0);
  Position pos = decoder.decode(null, null, msg);
  assertEquals(50, pos.getSpeed(), 0.001);
  // No test for status/alarm/etc. message types — misses type-specific parsing bugs
  ```