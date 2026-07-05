---
name: array-index-out-of-bounds-null-element
description: When resolving property expressions against arrays or lists, a null element
  at the accessed index causes an unexpected NullPointerException instead of returning
  null. This skill teaches testing for null elements inside indexed collections.
code_tags:
- ARGUMENT_VALIDATION
- STATE_MUTATION
- BOUNDARY_CHECK
test_pattern: EXCEPTION_TEST
---

# array-index-out-of-bounds-null-element

## Instructions

# Array Index Out of Bounds with Null Element Access

## Instructions

**WHEN** the TG encounters code that resolves a property expression (e.g., `"array[0].property"`) against an array or `List` and the expression accesses an index that **exists** (i.e., the index is within bounds) but the **element at that index is `null`**:

- **THEN** the TG should write a test that:
  1. Creates an object with an array or list field containing at least one element that is `null`.
  2. Invokes the property resolver with an expression that accesses the index where the `null` element resides (e.g., `"array[0].someProperty"`).
  3. Verifies that the resolver **returns `null`** instead of throwing a `NullPointerException`.
  4. If the resolver has a `setValue()` variant, also test setting a value on a `null` element's property — this should also throw an appropriate exception (e.g., `NullPointerException` or `IndexOutOfBoundsException`) depending on expected semantics.

- **Common pitfalls to avoid:**
  - ❌ Testing only with arrays/lists where all elements are non-null — this misses the null-element edge case.
  - ❌ Assuming that an index access always succeeds if the index is within bounds — the null element at that index may cause cascading `NullPointerException`s.
  - ❌ Not distinguishing between "index does not exist" (out of bounds) and "index exists but element is null" — both are separate bugs but the fix for one does not cover the other.
  - ❌ Only testing read access (`getValue`) without also considering write access (`setValue`) to a null element's property.

**Example (correct):**
```java
// Bean with an array containing a null element
BeanWithArray bean = new BeanWithArray();
bean.setArray(new String[] { "first", null, "third" });

// Accessing a non-null element's property — should succeed
Object result1 = PropertyResolver.getValue("array[0].length()", bean);
assertNotNull(result1);

// Accessing a null element — should return null, not throw NPE
Object result2 = PropertyResolver.getValue("array[1].length()", bean);
assertNull(result2);
```

**Example (incorrect — misses the bug):**
```java
BeanWithArray bean = new BeanWithArray();
bean.setArray(new String[] { "first", "second", "third" });

// Only testing with all non-null elements — does not catch the null element bug
Object result = PropertyResolver.getValue("array[1].length()", bean);
assertNotNull(result);
```