---
name: class-visit-filter-interface-conformance
description: When using ClassVisitFilter with an interface type, the visitObject method
  uses isAssignableFrom to check conformance. The trigger test verifies this works
  for String (a concrete class) but fails to test with an interface type where the
  object implements the interface indirectly. This skill teaches the TG to test ClassVisitFilter
  with interface types and objects that implement them.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- STATE_MUTATION
test_pattern: INTERACTION_TEST
---

# class-visit-filter-interface-conformance

## Instructions

# ClassVisitFilter Interface Conformance Testing

## Instructions

- WHEN the TG encounters a `ClassVisitFilter` being constructed with a `Class<?>` argument that could be an interface (e.g., `MarkerInterface.class`) AND the `visitObject(Object)` method uses `clazz.isAssignableFrom(object.getClass())`
- THEN the TG should write tests that verify the filter correctly identifies objects that implement the interface (including indirect implementation), and correctly rejects objects that do not. Specifically:
  - Create a test interface (e.g., `interface MarkerInterface { String getId(); }`)
  - Create a class that implements that interface (e.g., `class MarkedClass implements MarkerInterface { ... }`)
  - Create a class that does NOT implement the interface (e.g., a plain `Object` or a class extending something else without the interface)
  - Construct a `ClassVisitFilter(MarkerInterface.class)` and call `filter.visitObject(markedInstance)` — expect `true`
  - Call `filter.visitObject(unmarkedInstance)` — expect `false`
  - Also test with `filter.visitObject(null)` — this may throw `NullPointerException` due to `object.getClass()` being called on null, which is a separate null-safety concern to verify
- Common pitfalls:
  - Testing only with concrete classes like `String.class` and `Integer` values, missing the interface use case entirely
  - Not testing that `visitObject` correctly returns `true` for subclasses of the interface implementor
  - Assuming the test only needs to check the `visitStrings()` scenario — the actual bug manifests when the filter is used with an interface type and an object that implements it

### Correct example (what the TG should write):

```java
@Test
public void visitObjectWithInterface() throws Exception
{
    interface MarkerInterface {}
    class MarkedClass implements MarkerInterface {}
    class UnmarkedClass {}
    
    ClassVisitFilter filter = new ClassVisitFilter(MarkerInterface.class);
    assertTrue("should accept objects that implement the interface", 
               filter.visitObject(new MarkedClass()));
    assertFalse("should reject objects that do not implement the interface", 
                filter.visitObject(new UnmarkedClass()));
}
```

### Incorrect example (what the TG might mistakenly write):

```java
// Only testing with String.class (a concrete class) — misses the interface bug
@Test
public void visitStrings() throws Exception
{
    ClassVisitFilter filter = new ClassVisitFilter(String.class);
    assertTrue(filter.visitObject("a string"));
    assertFalse(filter.visitObject(123));
}
```