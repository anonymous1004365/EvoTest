---
name: nested-choice-filter-matched-propagation
description: WHEN building tests for routes that use nested choice/when/otherwise
  blocks, THEN test that the FILTER_MATCHED exchange property from inner filters does
  not incorrectly propagate outward to affect outer choice routing decisions.
code_tags:
- NULL_CHECK
- VALIDATION
- NESTED_CHOICE_FILTER_PROPAGATION
test_pattern: STATE_TEST
---

# nested-choice-filter-matched-propagation

## Instructions

# Nested Choice Filter-Matched Propagation

## Instructions

**WHEN** the code under test contains a `choice()` block (with `when()` clauses and an `otherwise()` clause) that is nested inside another `choice()` block's `otherwise()` clause — i.e., a nested choice structure like `choice().when(cond1).to(A).otherwise().choice().when(cond2).to(B).end().end()`:

- **THEN** the test MUST verify that `Exchange.FILTER_MATCHED` property set by filters inside the nested `choice()` block does NOT propagate to the outer `choice()` block's routing decisions.
- **THEN** write a test that sends a message matching only the innermost condition (e.g., `cond2`) and verify that the message reaches the innermost destination (e.g., `direct:b`), while the outer `otherwise()` clause correctly routes.
- **THEN** write a test that sends a message matching `cond1` (the outer `when()` condition) and verify it goes to `direct:a`, while also verifying that messages not matching `cond1` but not matching `cond2` go to any final fallback destination.
- **THEN** the test should verify message counts (e.g., `MockEndpoint.expectedMessageCount(1)`) on each endpoint to confirm no messages are lost or misrouted.
- **THEN** use `mock:endpoint` style endpoints (e.g., `mock:low`, `mock:high`, `mock:other`) to assert which route each test message takes.
- **THEN** avoid testing only a single routing path — test ALL branches of the nested choice structure to catch propagation bugs.
- **THEN** include edge cases where the outer `when()` condition is false and the nested `otherwise()` fallback is the path taken.

**Common pitfalls:**
- ❌ Testing only the "happy path" where the outer `when()` matches, without testing the nested choice branch.
- ❌ Assuming that FILTER_MATCHED is scoped locally within each choice block (it is not — it is an exchange-level property that persists across nested processors unless explicitly cleared).
- ❌ Using only a single message type or single route — the bug manifests specifically with two different message bodies matching different branches of nested choices.

**Example (correct approach):**
```java
@Test
public void testNestedChoice() throws Exception {
    MockEndpoint mockLow = getMockEndpoint("mock:low");
    MockEndpoint mockHigh = getMockEndpoint("mock:high");
    MockEndpoint mockOther = getMockEndpoint("mock:other");
    
    mockLow.expectedMessageCount(1);
    mockHigh.expectedMessageCount(1);
    mockOther.expectedMessageCount(1);
    
    // Message matching outer when (cond1 true)
    template.sendBody("direct:start", "<low val=\"2000\"/>");
    // Message matching nested when (cond1 false, cond2 true)
    template.sendBody("direct:start", "<high val=\"2000\"/>");
    // Message matching neither (falls through to otherwise)
    template.sendBody("direct:start", "<medium val=\"2000\"/>");
    
    assertMockEndpointsSatisfied();
}
```

**Example (incorrect approach):**
```java
@Test
public void testOnlyOuterBranch() throws Exception {
    // ❌ Only tests one path — misses the nested choice bug entirely
    MockEndpoint mockLow = getMockEndpoint("mock:low");
    mockLow.expectedMessageCount(1);
    template.sendBody("direct:start", "<low val=\"2000\"/>");
    assertMockEndpointsSatisfied();
}
```