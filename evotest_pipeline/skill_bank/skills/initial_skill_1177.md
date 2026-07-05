---
name: virtual-phone-decoder-attribute-handling
description: When writing protocol decoder tests that use virtual phone number attributes
  and channel handler context, ensure the mock channel properly returns these attributes.
  Without proper stub setup, the decoder silently returns null instead of decoding
  the message.
code_tags:
- VALIDATION
- BOUNDARY_CHECK
test_pattern: MOCK_TEST
---

# virtual-phone-decoder-attribute-handling

## Instructions

# Virtual Phone Decoder Attribute Handling

## Instructions

WHEN testing a protocol decoder class (such as `RaveonProtocolDecoder`) that is invoked through a ChannelHandlerContext pipeline and relies on a Channel's `attr()` method to retrieve device attributes (e.g., virtual phone numbers stored as `ChannelAttributeKey` values):

- THEN the test MUST stub the `Channel.attr(AttributeKey)` call to return an `Attribute` object, and stub that `Attribute.get()` call to return the expected device identifier (or `null` if the test scenario involves an unregistered device).
- THEN the test MUST invoke the decoder via `channelRead(ctx, msg)` where `ctx` is a mock `ChannelHandlerContext` that returns a mock `Channel` from `ctx.channel()`, NOT by calling the decoder method directly.
- Include a concrete test case where the channel attribute is set to a known virtual phone number (e.g., `"3514756002"`) and verify that the decoded result (e.g., the returned `DeviceSession` or position object) contains the correct attributes (e.g., device ID or protocol).
- Also test the case where the attribute is `null` or the device is unknown — verify that the decoder returns `null` (no device session could be created).

Common pitfalls to avoid:
- ❌ Calling the decoder's decode method directly (e.g., `decoder.decode(...)`) without going through the channel read pipeline — this misses bugs in how the decoder interacts with the channel's attribute system.
- ❌ Forgetting to stub `channel.attr(key).get()` — if the mock returns `null` by default, the test may silently pass on both buggy and fixed versions if the bug is in a different code path.
- ❌ Testing only non-null attribute cases without also testing the `null`/unregistered device scenario.

Example (correct):
```java
// Correct: pipeline invocation with mocked attributes
Channel channel = mock(Channel.class);
Attribute<Object> attr = mock(Attribute.class);
when(channel.attr(any(AttributeKey.class))).thenReturn(attr);
when(attr.get()).thenReturn("3514756002");
ChannelHandlerContext ctx = mock(ChannelHandlerContext.class);
when(ctx.channel()).thenReturn(channel);

RaveonProtocolDecoder decoder = new RaveonProtocolDecoder();
decoder.channelRead(ctx, someMessage);

// Verify that a DeviceSession was created and contains expected attributes
```

Example (incorrect):
```java
// Incorrect: Direct decode call without channel attribute mocking
RaveonProtocolDecoder decoder = new RaveonProtocolDecoder();
Object result = decoder.decode(channel, remoteAddress, someMessage);
// Result is null because the decoder couldn't get attributes from the unmocked channel
// And the test may not distinguish between "no device" and "decoding failed"
```