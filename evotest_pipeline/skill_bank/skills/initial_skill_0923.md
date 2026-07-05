---
name: yaml-generator-auto-close-stream
description: When a YAML/JSON generator wraps an OutputStream, verify that the auto-close
  behavior for the underlying target stream can be disabled. Tests should confirm
  that closing the generator does not close the user-provided stream when the generator
  is configured with JSONGenerator.Feature.AUTO_CLOSE_TARGET disabled.
code_tags:
- VALIDATION
test_pattern: STATE_TEST
---

# yaml-generator-auto-close-stream

## Instructions

# YAML Generator OutputStream Auto-Close Behavior

## Instructions

- WHEN the TG encounters a YAML or JSON generator (e.g., `YAMLGenerator`, `JsonGenerator`) that wraps a user-provided `OutputStream` via a `IOContext` or similar factory method (e.g., `_createGenerator(Writer, IOContext, ...)` or `createGenerator(OutputStream, ...)`)
- THEN the TG should write a test that:
  1. Creates a `ByteArrayOutputStream` (the "target" stream)
  2. Creates/binds a `YAMLGenerator` (or similar generator) using that stream
  3. Configures the generator to have the `AUTO_CLOSE_TARGET` feature **disabled** (`JsonGenerator.Feature.AUTO_CLOSE_TARGET`, or the generator's own equivalent feature such as `YAMLGenerator.Feature` if it has one)
  4. Calls `generator.close()` to close the generator
  5. Verifies that the underlying `ByteArrayOutputStream` is **NOT closed** after the generator closes (e.g., by writing to it and checking that no `IOException` is thrown — call `baos.write(42)`; if it throws `IOException("Stream closed")` the stream was incorrectly closed)

- The test should use the factory output method that writes to the user's stream (e.g., `writeValue(generator, ...)` or `writeStartObject()` / `writeEndObject()`) to produce some output before closing.

- Common pitfalls to avoid:
  - **Testing only with `AUTO_CLOSE_TARGET` enabled (default)**: The bug only manifests when auto-close is **disabled** — the generator closes the stream regardless of the feature setting.
  - **Testing only `close()` without producing output first**: Some generators lazily initialize the stream and may not properly attach the auto-close behavior until output is written.
  - **Testing only `flush()` or other methods**: The key is verifying the stream is still open after `close()` is called on the generator.
  - **Forgetting that `close()` may be called multiple times or via try-with-resources**: The test should explicitly call `close()` once and then verify the stream state.

### Example (correct):

```java
// Correct: verifies stream remains open when AUTO_CLOSE_TARGET is disabled
ByteArrayOutputStream baos = new ByteArrayOutputStream();
JsonFactory factory = new YAMLFactory();
YAMLGenerator generator = (YAMLGenerator) factory.createGenerator(baos);
generator.disable(JsonGenerator.Feature.AUTO_CLOSE_TARGET);
generator.writeStartObject();
generator.writeEndObject();
generator.close();
// After close, the stream should still be open
baos.write(42); // must not throw IOException("Stream closed")
```

### Example (incorrect — will miss the bug):

```java
// Incorrect: doesn't disable auto-close or doesn't check stream state after close
ByteArrayOutputStream baos = new ByteArrayOutputStream();
YAMLGenerator generator = (YAMLGenerator) factory.createGenerator(baos);
generator.writeStartObject();
generator.writeEndObject();
generator.close();
// Missing: verification that baos is still usable
// Also missing: disabling AUTO_CLOSE_TARGET
```