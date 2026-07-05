---
name: unknown-endpoint-type-lookup
description: Teaches the TG to test getEndpoint(String, Class<T>) with an unknown/nonexistent
  endpoint URI, verifying that NoSuchEndpointException is properly thrown. Use this
  skill when parameterized endpoint lookups with type conversion exist in CamelContext
  implementations.
code_tags:
- BOUNDARY_CHECK
- STATE_MUTATION
- VALIDATION
- ENDPOINT_LOOKUP_BY_TYPE
- EXCEPTION_HANDLING
- NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# unknown-endpoint-type-lookup

## Instructions

# Unknown Endpoint Type Lookup

## Instructions

**WHEN** the TG encounters a `CamelContext` implementation (e.g., `DefaultCamelContext`) that provides a typed endpoint lookup method with signature:

```java
public <T extends Endpoint> T getEndpoint(String name, Class<T> endpointType)
```

where the method internally calls `getEndpoint(name)` and then casts/converts the result to the requested `endpointType`:

```java
Endpoint endpoint = getEndpoint(name);
return endpointType.cast(endpoint);
```

**THEN** the TG MUST write an exception test that:

1. Creates a fresh `CamelContext` instance (e.g., `DefaultCamelContext` or `SpringCamelContext` with minimal setup).
2. Calls `getEndpoint(String, Class)` with a **nonexistent/unknown URI** (e.g., `"unknown:foo"` or `"unknownEndpoint"`) and a valid endpoint subtype (e.g., `DirectEndpoint.class`, `HttpEndpoint.class`, or any known `Endpoint` subclass).
3. **Verifies** that calling `getEndpoint(String, Class)` with a non-existent URI throws a **`NoSuchEndpointException`**.
4. Uses JUnit's `assertThrows` or `@Test(expected=...)` to assert the exception type.

**Example — CORRECT test (bug-detecting):**

```java
@Test
public void testGetEndPointByTypeUnknown() {
    CamelContext context = new DefaultCamelContext();
    assertThrows(NoSuchEndpointException.class, () -> {
        context.getEndpoint("unknown:foo", DirectEndpoint.class);
    });
}
```

**Example — INCORRECT test that would NOT catch the bug:**

```java
@Test
public void testGetEndPointByTypeUnknownWeak() {
    CamelContext context = new DefaultCamelContext();
    // Only calls getEndpoint(String) — does NOT exercise the typed overload
    assertThrows(NoSuchEndpointException.class, () -> {
        context.getEndpoint("unknown:foo");
    });
}
```

**Common pitfalls to avoid:**

- ❌ Testing `getEndpoint(String name)` **without** the `endpointType` parameter — this tests the wrong method and does not exercise the typed lookup branch.
- ❌ Testing with a valid/known URI (e.g., `"direct:start"`) — this will succeed and never trigger the unknown-endpoint path.
- ❌ Using a mock or spy for the context that overrides `getEndpoint` — the bug is in the real implementation's interaction between `getEndpoint(String)` and `getEndpoint(String, Class)`.
- ❌ Forgetting to import/use `NoSuchEndpointException` from `org.apache.camel`.
- ❌ Running the test against a context that already has the endpoint registered — the test must use a clean context with an unresolvable URI.

**Why this matters:** Without this test, a regression where `getEndpoint(String, Class)` silently returns `null` (because it catches exceptions from `getEndpoint(name)` or the type cast) or fails to throw an exception for unknown endpoints would go undetected. The typed overload must always propagate the `NoSuchEndpointException` from the underlying untyped lookup.