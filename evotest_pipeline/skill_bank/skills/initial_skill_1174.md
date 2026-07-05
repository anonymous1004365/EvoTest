---
name: protocol-decoder-alternative-path
description: WHEN testing protocol decoders with multiple parsing paths or message
  formats, THEN ensure each alternative format/prefix/type is tested individually.
  This skill catches bugs where one message format works but an alternative format
  fails due to path-specific logic errors.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
test_pattern: PARAMETRIC_TEST
---

# protocol-decoder-alternative-path

## Instructions

# Protocol Decoder Alternative Path Testing

## Instructions

**WHEN** the TG encounters a protocol decoder class that has multiple message formats, types, prefixes, or alternative parsing paths (e.g., checking if a message starts with different prefixes like ">", "+", "$", etc., or has multiple modes/types like position reports, alerts, heartbeats, etc.):

- **THEN** the TG should write a **parametric test** that tests **each distinct message format/path** with its own representative hex/string message.
- **THEN** the test should verify that each message type **decodes into the correct subclass/type** of result (e.g., `Position` vs `Command` vs `Alert`) or that the correct fields are populated (e.g., `position.getValid()` is `true`/`false` as expected).
- **THEN** the test should include at least one message per distinct alternative path — do NOT rely on a single test message covering all paths.
- **THEN** the test should be designed so that if **one path is broken** (e.g., returns wrong type, throws exception, or returns null), the test fails with a clear error.

**Common pitfalls to avoid:**

- ❌ Testing only one message format and assuming all paths work identically.
- ❌ Using a single test method that only sends one message variant.
- ❌ Testing with the wrong expected type (e.g., expecting `Position` when the decoder returns a `Command` for that format).
- ❌ Not testing edge-case message types (e.g., empty messages, heartbeat-only, alerts without location data).
- ❌ Hard-coding expected values that are implementation-specific rather than format-specific.

**Correct example (parametric test with multiple messages):**

```java
@Test
public void testDecode() throws Exception {
    T800xProtocolDecoder decoder = new T800xProtocolDecoder(null);
    
    // Test position report format (starts with ">")
    Position position = (Position) decoder.decode(null, null, 
        ByteBufUtil.hexDump(">0131123456789..."));
    assertNotNull(position);
    assertTrue(position.getValid());
    assertEquals(48.123, position.getLatitude(), 0.001);
    
    // Test alert/command format (starts with "+")
    Command command = (Command) decoder.decode(null, null, 
        ByteBufUtil.hexDump("+RESP:GTSET,..."));
    assertNotNull(command);
    assertEquals(Command.TYPE_ALARM, command.getType());
    
    // Test heartbeat/keepalive format (starts with "$")
    Object heartbeat = decoder.decode(null, null, 
        ByteBufUtil.hexDump("$..."));
    assertNotNull(heartbeat);
    // Heartbeat may return null or a special type — verify explicitly
}
```

**Incorrect example (single-path only):**

```java
@Test
public void testDecode() throws Exception {
    T800xProtocolDecoder decoder = new T800xProtocolDecoder(null);
    
    // BUG: Only tests position format, misses broken alternative paths
    Position position = (Position) decoder.decode(null, null, 
        ByteBufUtil.hexDump(">0131123456789..."));
    assertNotNull(position);
    assertEquals(48.123, position.getLatitude(), 0.001);
}
```