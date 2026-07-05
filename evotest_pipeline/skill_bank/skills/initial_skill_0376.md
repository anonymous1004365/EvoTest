---
name: alternative-protocol-decoding-validation
description: When a protocol decoder has alternative/branching decoding paths (e.g., different decoders for different message types), the TG should explicitly test coverage of each alternative path. This skill helps detect bugs where a secondary decoding path incorrectly handles or ignores parameter types.
code_tags: ['ALTERNATIVE_PROTOCOL_DECODING']
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoding-validation

## Instructions

# Alternative Protocol Decoding Path Validation

## Instructions

- WHEN the TG encounters a protocol decoder class that has multiple alternative decoding paths or branches (e.g., different decoders for different message types, different parameter types, or different command formats)
- THEN the TG should write tests that explicitly exercise each branching alternative, not just the primary/default path. Specifically:
  - Identify the conditions that determine which decoding path is selected (e.g., parameter type, message prefix, command structure)
  - Create separate test data for each distinct branch/alternative
  - For each test input, verify that the decoder returns a correctly decoded result without throwing unexpected exceptions
  - Pay special attention to branches that involve type checking, type conversion, or type-based dispatch (e.g., `instanceof` checks, type parameter handling, or generic type resolution)
- Common pitfalls to avoid:
  - Testing only the most common or default decoding path while ignoring alternatives
  - Assuming that if one path works, all paths work (they may have different type handling logic)
  - Not testing edge cases at the boundaries between different decoding alternatives
  - Using only String-type parameters when the decoder also handles other types (e.g., CtTypeReference, numeric types, or protocol-specific types)
- Example: For a decoder that dispatches based on parameter type (String vs. CtTypeReference), the TG should test:
  - Correct: Test with a String parameter to exercise one path, AND test with a CtTypeReference parameter to exercise the other path, verifying both produce correct results.
  - Incorrect: Testing only with String parameters and assuming the CtTypeReference path works identically.