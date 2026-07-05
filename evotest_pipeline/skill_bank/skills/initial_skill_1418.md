---
name: validator-self-delegation-bug
description: Detects when a validator's leave method incorrectly delegates to enter
  instead of leave on the wrapped validator, causing double-enter calls and missed
  validation logic on node exit. Use when tests verify validator behavior involving
  both enter and leave lifecycle methods.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# validator-self-delegation-bug

## Instructions

# Validator Self-Delegation Bug in leave() Method

## Instructions

- WHEN the TG encounters a `Validator` or `MoveValidator` implementation where the `leave(NodeState before, NodeState after)` method body contains a call like `moveValidator.enter(before, after)` instead of `moveValidator.leave(before, after)`:
  - THEN the TG should write a state-based test that constructs a simple before/after `NodeState` pair, processes them through `EditorDiff.process(validator, before, after)`, and asserts that both `enter()` and `leave()` are called exactly once on the wrapped validator.
  - Include assertions that the `leave()` callback receives the correct arguments (the `before` and `after` states from the diff, not swapped).
  - Expect that on the buggy version, `leave()` will NOT be called on the wrapped validator (because the wrapper's `leave()` incorrectly calls `enter()` on the wrapped validator instead).
  
- WHEN the TG sees a delegation pattern where a validator wraps another validator and delegates lifecycle methods like `enter()`, `leave()`, `childNodeAdded()`, `childNodeChanged()`, `childNodeDeleted()`:
  - THEN the TG should check that each delegation method in the wrapper calls the **identically-named method** on the wrapped validator, NOT a differently named method.
  - Specifically verify that `leave()` delegates to `moveValidator.leave(before, after)` and NOT to `moveValidator.enter(before, after)`.

- WHEN the triggering test failure message contains "Unexpected move" or similar unexpected behavior:
  - THEN the TG should suspect a lifecycle method mis-delegation in the validator chain, particularly the `leave()` ↔ `enter()` confusion.

- **Common pitfalls to avoid:**
  - ❌ Assuming that identical parameter types means the delegation is correct. Two methods (`enter()` and `leave()`) can have the same signature `(NodeState before, NodeState after)` but completely different semantics.
  - ❌ Testing only `enter()` or only `childNodeAdded()` paths. A bug in `leave()` mis-delegation will only be exposed when the validator processes node changes that trigger the `leave()` path — test both.
  - ❌ Using a mock/expectation that only records `move()` calls without verifying `enter()` vs `leave()` call counts.

## Examples

**Correct test approach (catches the bug):**

```java
// Use a custom MoveValidator that records enter/leave calls
private static class RecordingMoveValidator extends DefaultMoveValidator {
    boolean enterCalled = false;
    boolean leaveCalled = false;
    
    @Override
    public void enter(NodeState before, NodeState after) {
        enterCalled = true;
    }
    
    @Override
    public void leave(NodeState before, NodeState after) {
        leaveCalled = true;
    }
}

@Test
public void testEnterAndLeaveAreBothCalled() throws CommitFailedException {
    NodeState before = createInitialNodeState();
    NodeState after = createModifiedNodeState();
    
    RecordingMoveValidator recordingValidator = new RecordingMoveValidator();
    MoveDetector detector = new MoveDetector(recordingValidator);
    
    CommitFailedException ex = EditorDiff.process(detector, before, after);
    if (ex != null) throw ex;
    
    assertTrue("enter() should have been called", recordingValidator.enterCalled);
    assertTrue("leave() should have been called", recordingValidator.leaveCalled);
    // On buggy version, leaveCalled would be false because leave() delegates to enter()
}
```

**Incorrect test approach (misses the bug):**

```java
// ❌ Only tests move() — doesn't verify enter/leave lifecycle
@Test
public void testMoveDetection() throws CommitFailedException {
    NodeState before = ...;
    NodeState after = ...;
    MoveExpectation exp = new MoveExpectation(ImmutableMap.of(...));
    MoveDetector detector = new MoveDetector(exp);
    EditorDiff.process(detector, before, after);
    exp.assertAllFound();
    // ❌ This test passes even if leave() is mis-delegated to enter()
}
```