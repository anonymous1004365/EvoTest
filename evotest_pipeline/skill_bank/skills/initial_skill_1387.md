---
name: signal-event-definition-scope-mutation
description: When creating or reusing signal event definitions, the scope property
  is mutated without proper reset, causing state pollution across test runs. Apply
  this skill when tests encounter events that fire unexpectedly due to stale mutable
  state on static-like or cached objects.
code_tags:
- STATE_MUTATION
test_pattern: STATE_TEST
---

# signal-event-definition-scope-mutation

## Instructions

# Signal Event Definition Scope Mutation

## Instructions

- WHEN the TG encounters code that defines signal event definitions (e.g., `SignalEventDefinition` with a `scope` field) and these definitions are created from a shared process engine configuration or factory
- THEN the TG should test that the `scope` property on a `SignalEventDefinition` is correctly set per definition and not inadvertently mutated by subsequent operations. Specifically:
  1. Create a first signal event definition with `scope = "processInstance"` and verify `getScope()` returns `"processInstance"`.
  2. Create a second signal event definition or reuse the same object and set `scope = "global"` (the default).
  3. Verify that the first event definition still has `scope = "processInstance"` after the second is created.
  4. Expect that if the `scope` field is mutated (e.g., replaced or reassigned to a shared value), the first definition's scope changes incorrectly — this would expose the bug.
- Common pitfalls: Testing only the final state of the last created definition, or not checking that previous definitions retain their scope values. Also, avoid assuming that creating a new `SignalEventDefinition` with a fresh constructor guarantees isolation — the underlying factory or parser may return the same object or mutate shared state.

### Correct Example (catches the bug)
```java
SignalEventDefinition sigDef1 = (SignalEventDefinition) process.getDefinition(event1);
sigDef1.setScope("processInstance");

// ... later, another definition is parsed or created
SignalEventDefinition sigDef2 = (SignalEventDefinition) process.getDefinition(event2);
sigDef2.setScope("global");

// Verify scope of sigDef1 is NOT polluted
assertEquals("processInstance", sigDef1.getScope());
// If the bug is present, sigDef1.getScope() will now return "global"
```

### Incorrect Example (misses the bug)
```java
SignalEventDefinition sigDef1 = (SignalEventDefinition) process.getDefinition(event1);
sigDef1.setScope("processInstance");
// ... later ...
SignalEventDefinition sigDef2 = (SignalEventDefinition) process.getDefinition(event2);
sigDef2.setScope("global");

// Only checking the last definition's scope
assertEquals("global", sigDef2.getScope());
// This passes on both buggy and fixed, but does not detect the mutation on sigDef1
```