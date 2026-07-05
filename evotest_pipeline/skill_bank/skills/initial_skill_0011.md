---
name: thrift-deserialization-null-validation
description: When a class has a constructor that accepts a Thrift-generated object
  (e.g., TMutation, TKey), the TG must test that invalid/null fields in the Thrift
  object are validated and throw IllegalArgumentException. This skill applies to deserialization
  constructors that copy fields from Thrift types.
code_tags:
- VALIDATION
- TYPE_CONVERSION
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# thrift-deserialization-null-validation

## Instructions

# Thrift Deserialization Null Validation

## Instructions

- WHEN the TG encounters a constructor that accepts a Thrift-generated type parameter (e.g., `Mutation(TMutation tmutation)`, `Key(TKey tk)`), and that constructor directly copies fields from the Thrift object (e.g., `ByteBufferUtil.toBytes(tmutation.row)`)
- THEN the TG MUST write a test that:
  1. Creates a valid instance of the Thrift type
  2. Sets one critical field (e.g., `row`) to `null` using the Thrift setter
  3. Passes the invalid Thrift object to the constructor
  4. Expects `IllegalArgumentException.class` to be thrown
  5. Tests each field that is essential for the object's integrity (row, data, etc.)

- Common pitfalls to avoid:
  - Testing only the happy path (valid Thrift to Java object conversion) — the invalid/null path MUST also be tested
  - Only testing null `row` field — also test other critical fields that, if null, would cause NPE downstream
  - Using `assertThrows(NullPointerException.class)` instead of `IllegalArgumentException.class` — the test should expect `IllegalArgumentException` as the specific validation exception
  - Forgetting to attach `@Test(expected = IllegalArgumentException.class)` or use `assertThrows` — the test MUST declare the expected exception

### Correct Example

```java
// Mutation's TMutation constructor should reject null row
@Test(expected = IllegalArgumentException.class)
public void testThrift_Invalid() {
    Mutation m = new Mutation("r1");
    m.put("cf1", "cq1", new Value("v1"));
    TMutation tm = m.toThrift();
    tm.setRow((byte[]) null);
    new Mutation(tm);
}
```

### Incorrect Example (missing null validation, no exception expected)

```java
// BAD: Only tests the valid path, never tests what happens when
// the Thrift object has null fields
@Test
public void testThrift() {
    Mutation m = new Mutation("r1");
    TMutation tm = m.toThrift();
    Mutation m2 = new Mutation(tm);
    assertEquals(m.getRow(), m2.getRow());
}
```