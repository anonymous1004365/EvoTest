---
name: runtime-context-proxy-equality
description: When operators create proxy runtime contexts (e.g., ChainedRuntimeContext)
  that delegate to a parent context, test that each operator instance gets its own
  unique context object (different object identity) rather than sharing the same parent
  context reference.
code_tags:
- ARGUMENT_VALIDATION
- NULL_CHECK
- BOUNDARY_CHECK
- STATE_MUTATION
- CACHING_AND_CONVERTER_REGISTRY
- CLONE_MUTATION
test_pattern: STATE_TEST
---

# runtime-context-proxy-equality

## Instructions

# Verify Runtime Context Proxy Identity per Operator

## Instructions

- WHEN the code creates runtime context proxy objects (such as `StreamingRuntimeContext`) that wrap or delegate to another context object, and the builder/operator chain shares a parent context reference:
  - THEN the test MUST verify that each operator in a chain receives its own distinct `StreamingRuntimeContext` instance (different object identity), rather than sharing the same parent context object.
  - The test should:
    1. Build a chain of operators (e.g., `SourceStreamTask`, `OneInputStreamOperator`, `TwoInputStreamOperator`).
    2. After the chain completes initialization and opens, call `AbstractStreamOperator#getRuntimeContext()` on each operator.
    3. Assert that each returned `StreamingRuntimeContext` is a different object instance using `assertNotSame()` — e.g., `assertNotSame(sourceContext, oneInputContext)`.
    4. Also assert that the context downstream operators return is NOT the same object as the upstream operator's runtime context returned by `getEnvironment().getRuntimeContext()`.
  - Common pitfalls to avoid:
    - Testing only that the context is not null or that methods like `getJobId()` return expected values — this misses sharing bugs.
    - Testing only the context of one operator (e.g., only the source), not verifying distinctness across all operators in the chain.
    - Using `assertEquals` or `assertSame` which would pass accidentally if references happen to match by chance.

- Example of correct test code:
```java
// After chain initialization and open
StreamingRuntimeContext sourceContext = (StreamingRuntimeContext) sourceOperator.getRuntimeContext();
StreamingRuntimeContext oneInputContext = (StreamingRuntimeContext) oneInputOperator.getRuntimeContext();
StreamingRuntimeContext twoInputContext = (StreamingRuntimeContext) twoInputOperator.getRuntimeContext();

assertNotSame("Source and one-input operators must have different runtime contexts",
    sourceContext, oneInputContext);
assertNotSame("One-input and two-input operators must have different runtime contexts",
    oneInputContext, twoInputContext);
assertNotSame("Source operator context must differ from environment context",
    sourceContext, task.getEnvironment().getRuntimeContext());
```

- Example of incorrect test code (would NOT catch the bug):
```java
// This only checks a non-null value — misses sharing entirely
assertNotNull(sourceOperator.getRuntimeContext());
assertNotNull(oneInputOperator.getRuntimeContext());

// OR blindly assuming they are different without checking
StreamingRuntimeContext ctx = (StreamingRuntimeContext) sourceOperator.getRuntimeContext();
assertEquals(expectedJobId, ctx.getJobId());
```

- This skill applies when the test already sets up chained operators in a task and needs to verify runtime contexts are properly proxied/unique per operator.