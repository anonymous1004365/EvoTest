---
name: output-registry-streaming-type-resolution
description: When testing output registry resolution for streaming result types, verify
  that the resolver correctly handles the full class hierarchy including supertypes.
  Apply this when tests assert type resolution for streaming outputs like StringListOutput.
code_tags:
- ARGUMENT_VALIDATION
- EXCEPTION_HANDLING
- NULL_CHECK
- OUTPUT_REGISTRY_RESOLUTION
test_pattern: STATE_TEST
---

# output-registry-streaming-type-resolution

## Instructions

# Output Registry Streaming Type Resolution

## Instructions

- WHEN the TG encounters an output registry that resolves command output types to factory resolvers, and one of the concrete output types extends or implements a parent type/interface via generics (e.g., `StringListOutput extends StreamingOutput<List<String>>` or similar)
- THEN the TG should test that the output registry correctly maps both the concrete type AND its relevant supertypes (e.g., both `StringListOutput` and `StreamingOutput` or the generic parameter type). The test should verify that passing the correct type to the resolution method returns a non-null, valid resolver instance.
- Include a test that passes the concrete output class (e.g., `StringListOutput.class`) to the registry's resolution method and asserts that the result is **not null** and is an instance of the expected factory type. On the buggy version, the resolution may return null or an incorrect type due to failure to traverse the full type hierarchy.
- Common pitfall: testing only the abstract parent type (e.g., `StreamingOutput.class`) without testing the specific concrete subtype that exercises the hierarchy traversal. Always test the concrete implementation class.
- Example correct test:
```java
// For a registry that resolves output types to command output factories:
OutputRegistry registry = new DefaultOutputRegistry();
CommandOutputFactory factory = registry.resolveOutputFactory(StringListOutput.class);
assertThat(factory).isNotNull();
assertThat(factory).isInstanceOf(StreamingStringListOutputFactory.class);
```
- Example incorrect test (incomplete):
```java
// ❌ Only tests the abstract parent type — does NOT exercise the concrete type hierarchy resolution
OutputRegistry registry = new DefaultOutputRegistry();
CommandOutputFactory factory = registry.resolveOutputFactory(StreamingOutput.class);
// This may pass on both versions without catching the bug
```