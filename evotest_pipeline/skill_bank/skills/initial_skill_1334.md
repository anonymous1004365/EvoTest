---
name: creator-collector-verify-nondup-guard
description: When a method mutates object state based on a conditional validation
  check, the test must verify that state is NOT updated when validation fails. This
  skill applies when a 'verify' method changes from void to boolean return, and callers
  must guard state assignments with the return value.
code_tags:
- NULL_CHECK
- VALIDATION
test_pattern: STATE_TEST
---

# creator-collector-verify-nondup-guard

## Instructions

# CreatorCollector VerifyNonDup Guard Pattern

## Instructions

- WHEN the TG encounters a method that:
  1. Returns `boolean` (previously returned `void`) to indicate whether an operation should proceed
  2. Has call sites that unconditionally called the method and then performed state mutation (e.g., assigning `_propertyBasedArgs`, `_delegateArgs`, `_arrayDelegateArgs`)
  3. The method performs validation to decide if a new creator should replace an existing one (e.g., `verifyNonDup` deciding between explicit vs implicit creators)

- THEN the TG should write a **state test** that:
  1. Calls the "add" method (e.g., `addPropertyCreator`) multiple times with conflicting configurations (e.g., first an explicit creator, then an implicit one for the same property type index)
  2. Verifies that the SECOND call does NOT overwrite the state set by the FIRST call
  3. Specifically, check that when an explicit creator is set first and an implicit one is attempted second, the internal state (`_propertyBasedArgs`, etc.) retains the first creator's configuration

- Common pitfalls to avoid:
  - Testing only the happy path (single call) which would pass on both buggy and fixed versions
  - Not testing conflicting explicit/implicit creator registrations
  - Not verifying internal field state after the second call (e.g., checking that `_propertyBasedArgs` is not null but rather still contains the first creator's properties)
  - Only testing exception paths and missing the silent data corruption bug

- Example of correct test (fixed version behavior):
```java
// Test that an implicit creator does NOT override an explicit one
public void testExplicitCreatorNotOverwrittenByImplicit() {
    CreatorCollector collector = new CreatorCollector(null);
    AnnotatedWithParams explicitCreator = createExplicitCreator();
    SettableBeanProperty[] props1 = new SettableBeanProperty[] { ... };
    collector.addPropertyCreator(explicitCreator, true, props1);
    
    AnnotatedWithParams implicitCreator = createImplicitCreator();
    SettableBeanProperty[] props2 = new SettableBeanProperty[] { ... };
    collector.addPropertyCreator(implicitCreator, false, props2);
    
    // The state should still reference the explicit creator's properties
    assertEquals(props1, collector.getPropertyBasedArgs());
}
```

- Example of incorrect test (passes on both buggy and fixed, misses the bug):
```java
// BAD: Only tests a single registration
public void testSinglePropertyCreator() {
    CreatorCollector collector = new CreatorCollector(null);
    AnnotatedWithParams creator = createExplicitCreator();
    SettableBeanProperty[] props = new SettableBeanProperty[] { ... };
    collector.addPropertyCreator(creator, true, props);
    assertEquals(props, collector.getPropertyBasedArgs());
}
```