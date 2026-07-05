---
name: duplicate-type-variable-validation
description: When extracting generic type information, duplicate type variable bindings
  can cause InvalidTypes errors. Test that duplicate values in a HashMap with the
  same type variable key produce valid type information rather than an InvalidTypes
  exception.
code_tags:
- TYPE_CONVERSION
- VALIDATION
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# duplicate-type-variable-validation

## Instructions

# Duplicate Type Variable Validation

## Instructions

WHEN the TG encounters code that extracts type information from generic types (e.g., using `TypeExtractor` or similar utilities to analyze `TypeInformation` from generic classes like `HashMap`, `List`, etc.):

- THEN the TG should test that adding a value with the **same generic type variable** used for the key does **not** produce an `InvalidTypes` exception.

- Include tests with generic classes where the same type variable (e.g., `K` or `V`) is used both as a key type and a value type in a mapping structure like `HashMap<K, V>`.

- Specifically test the following scenario:
  - Create a generic class (e.g., `DuplicateValue`) that extends or uses a parameterized type such that a type variable is reused in a position where the type extractor might incorrectly treat it as conflicting (e.g., `HashMap<K, K>` or a HashMap where duplicate type bindings exist).
  - Call the type extraction method (e.g., `TypeExtractor.createTypeInfo(...)`) passing an instance of this generic class.
  - Assert that **no exception is thrown** and that valid `TypeInformation` is returned.

- Common pitfalls to avoid:
  - ❌ Testing only with `HashMap<K, V>` where `K` and `V` are distinct types — this misses the duplicate binding bug.
  - ❌ Testing only with concrete types (e.g., `HashMap<String, String>`) without going through the generic type extraction path.
  - ❌ Assuming the type extractor handles all type variable reuse correctly without testing it.
  - ❌ Using `assertNotNull` only — also use `assertThat(...)` on the returned `TypeInformation` to verify it has the correct structure (e.g., `TypeInformation.of(HashMap.class)`).

### Correct Example

```java
public class DuplicateValue<K> extends HashMap<K, K> {}

@Test
public void testDuplicateValue() {
    TypeInformation<?> ti = TypeExtractor.createTypeInfo(DuplicateValue.class);
    // Should NOT throw InvalidTypesException
    assertThat(ti, is(TypeInformation.of(HashMap.class)));
}
```

### Incorrect Example (what might happen without this test)

```java
// This test only checks distinct types - doesn't catch the duplicate binding bug
public class DistinctTypes<K, V> extends HashMap<K, V> {}

@Test
public void testDistinctTypes() {
    TypeInformation<?> ti = TypeExtractor.createTypeInfo(DistinctTypes.class);
    // This passes even with the bug, so it doesn't guard against it
    assertThat(ti, is(TypeInformation.of(HashMap.class)));
}
```

### Additional Guidance

- If a nested structure has the duplicate binding pattern, also test nested cases (e.g., `DuplicateValueNested` that wraps the duplicate pattern inside another generic class).
- The bug manifests as an `InvalidTypesException` with a message containing "Type of TypeVariable ..." — the test should verify that this exception is **not** thrown.
- Use `@SuppressWarnings("unchecked")` if raw types are involved in the test setup.