---
name: compound-mapper-recursive-unmount
description: When testing the unmount/remove of request mappers from a compound mapper
  that may contain nested mappers (via IRequestMapperDelegate), verify that unmounting
  recursively traverses sub-mappers rather than only checking the top-level collection.
  Use this skill when testing any remove(N) or unmount(path) method on ICompoundRequestMapper
  or WebApplication where a request mapper wraps another mapper.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- SAFE_COPY
test_pattern: STATE_TEST
---

# compound-mapper-recursive-unmount

## Instructions

# Recursive Unmount of Nested/Delegating Mappers from Compound Mapper

## Instructions

- WHEN the TG encounters code that calls `remove(IRequestMapper)` or `unmount(String)` on a CompoundRequestMapper or WebApplication that uses IRequestMapperDelegate wrappers
  - THEN the TG must test that the remove/method correctly traverses through delegating mappers (IRequestMapperDelegate) to find and remove the underlying target mapper from nested compound mappers
  - The TG should verify the state after removal: the mapper should no longer be found via `mapper.mapRequest(request)` returning a non-null result
  - Concrete example: In CompoundRequestMapper/WebApplication, when a mapper `M` is registered inside a compound mapper, and that compound mapper is itself wrapped in an IRequestMapperDelegate, calling `compound.remove(M)` must recursively search through delegates (not just the top-level `mappers` list) to find the compound mapper containing M and remove M from it

- WHEN validating removal behavior:
  - THEN use `mapper.mapRequest(request)` to verify the mapper is still present before removal, and returns `null` (or a different result) after removal
  - Test with a concrete Request object that would match the mapper being removed
  - Example: Create a mock/fake IRequestMapper that responds to a specific scope, register it inside a nested CompoundRequestMapper wrapped by an IRequestMapperDelegate, then remove it — verify it is no longer reachable

- Common pitfalls to avoid:
  - Testing removal only on the top-level compound mapper without wrapping the inner compound mapper in an IRequestMapperDelegate
  - Not verifying the mapper was reachable *before* removal (precondition)
  - Using different Request objects for registration and verification that don't match the same scope/path
  - Assuming remove() checks `equals()` on the mapper directly without unwrapping delegates

## Correct Test Approach

**Setup**: Create a top-level CompoundRequestMapper. Inside it, add a nested CompoundRequestMapper containing a target mapper. Wrap the nested compound in an IRequestMapperDelegate. Then call `remove(targetMapper)` on the top-level compound. Verify the target mapper is no longer reachable via `mapRequest()`.

```java
// Correct: recursive unmount through IRequestMapperDelegate
IRequestMapper target = new TestMapper("/foo");
ICompoundRequestMapper nested = new CompoundRequestMapper();
nested.add(target);
IRequestMapperDelegate delegate = new RequestMapperDelegate(nested);
ICompoundRequestMapper top = new CompoundRequestMapper();
top.add(delegate);

Request request = new TestRequest("/foo");
assertNotNull("target should be reachable before removal", top.mapRequest(request));

top.remove(target);

assertNull("target should NOT be reachable after removal (recursive lookup through delegate)", top.mapRequest(request));
```

## Incorrect Test Approach (would miss the bug)

```java
// WRONG: Only tests top-level removal, not nested/recursive
IRequestMapper target = new TestMapper("/foo");
ICompoundRequestMapper top = new CompoundRequestMapper();
top.add(target);

top.remove(target);
assertNull("top-level removal works", top.mapRequest(new TestRequest("/foo")));
// This test passes even on buggy code because it doesn't exercise the recursive delegate unwrapping
```