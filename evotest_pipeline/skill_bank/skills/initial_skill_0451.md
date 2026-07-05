---
name: type-safe-collection-iteration
description: When iterating over typed collections and calling processors with type-casted
  elements, test that all element types are properly handled — especially when the
  loop's type binding differs from the collection's actual generic types. This skill
  catches bugs where processors receive only the first matching type due to incorrect
  type checking in iteration logic.
code_tags:
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# type-safe-collection-iteration

## Instructions

# Type-Safe Collection Iteration with Processor Calls

## Instructions

WHEN the TG encounters code that iterates over a typed collection (e.g., `List<CtTypeReference<?>>`) and calls a processor method (e.g., `processOn` or `process`) with elements that are type-cast or type-checked to a narrower type (e.g., `CtTypeReference<String>`), THEN the TG should write a test that:

1. **Populate the collection with multiple types**: Add elements of different concrete types to the target collection — for example, add a `CtTypeReference<String>` AND a `CtTypeReference<Integer>` (or other distinct type) to ensure the iteration processes all elements, not just those matching the first type encountered.

2. **Verify all elements were processed**: After invoking the processing logic, assert that the processor was called for *each* distinct type added — not just the first one. The bug pattern is that the iteration uses a type check that prematurely stops or skips non-matching types.

3. **Expect incomplete processing on buggy version**: On the buggy version, the test should fail because only one type's elements are processed; on the fixed version, all types should be processed.

**Common pitfalls to avoid:**
- ❌ Testing with only a single type in the collection (e.g., only `String` type references) — this won't expose the bug because there's nothing to skip.
- ❌ Using the same type multiple times instead of genuinely distinct types — the bug is about type-check filtering, not count.
- ❌ Assuming the iteration order is deterministic and that the first type is the only one tested.
- ❌ Not checking all collection elements — verifying only one processor call instead of asserting for each distinct type.

**Correct example (good test):**
```java
// Setup: add two different types to a typed collection
List<CtTypeReference<?>> typeRefs = new ArrayList<>();
CtTypeReference<String> stringRef = factory.Type().stringType();
CtTypeReference<Integer> intRef = factory.Type().integerType();
typeRefs.add(stringRef);
typeRefs.add(intRef);

// Mock processor that records calls
TestProcessor processor = new TestProcessor();
someClass.processOn(typeRefs, processor);

// Verify BOTH types were processed (not just one)
assertEquals(2, processor.getProcessedTypes().size());
assertTrue(processor.getProcessedTypes().contains(stringRef));
assertTrue(processor.getProcessedTypes().contains(intRef));
```

**Incorrect example (bad test — won't catch bug):**
```java
// Only adds one type — cannot reveal the type-filtering bug
List<CtTypeReference<String>> typeRefs = new ArrayList<>();
typeRefs.add(factory.Type().stringType());
typeRefs.add(factory.Type().stringType()); // same type twice

someClass.processOn(typeRefs, processor);
assertEquals(2, processor.getProcessedCount()); // passes even if buggy
```