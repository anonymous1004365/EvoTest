---
name: proxy-interface-support-unannotated-filter
description: When implementing proxy-based argument resolution or lazy initialization
  for interfaces, the TG should test that interfaces without specific annotations
  (e.g., Spring `@Scope`, `@Component`) are correctly excluded from proxying. This
  helps catch filtering logic bugs where only annotation presence is checked but interface
  checks are omitted.
code_tags:
- BOUNDARY_CHECK
- NULL_CHECK
- VALIDATION
- INTERFACE_CHECK
- PROXY_PATTERN
- ARGUMENT_VALIDATION
test_pattern: INTERACTION_TEST
---

# proxy-interface-support-unannotated-filter

## Instructions

# Proxy Interface Support — Unannotated Interface Filtering

## Instructions

**WHEN** the TG encounters code that implements proxy creation or lazy initialization for interfaces (e.g., `ProxyFactoryBean`, `getObject()`, `isProxyTargetClass()`, or similar proxying logic) that checks for specific annotations (like `@Scope`, `@Component`, Spring namespace annotations) on input types:

- **THEN** the TG should write a test that verifies interfaces WITHOUT those annotations are NOT proxied/supported. Specifically:
  - Create a simple interface with NO annotations (plain `interface Foo { ... }`)
  - Pass a class implementing that interface (or the interface class itself) to the proxy-support check method
  - **VERIFY** that the method returns `false` (does not support) for the unannotated interface
  - **VERIFY** that the method returns `true` (supports) for an annotated interface/class (e.g., `@Scope("prototype")`, `@Component`, or Spring namespace beans)

- **Common pitfalls to avoid:**
  - Testing only annotated interfaces — the filter bug is precisely about *excluding* unannotated ones
  - Forgetting to test the positive case (annotated) alongside the negative case (unannotated)
  - Testing with classes instead of interfaces — the filtering logic may treat classes differently; both should be tested
  - Using mocks that bypass the actual filtering logic

- **Example (correct):**
```java
// Unannotated interface — should NOT be supported
interface MyUnannotatedInterface {
    String getValue();
}

// Annotated interface — should be supported
@Scope("prototype")
interface MyAnnotatedInterface {
    String getValue();
}

@Test
public void doesNotSupportUnannotatedInterface() {
    ProxyingHandlerMethodArgumentResolver resolver = new ProxyingHandlerMethodArgumentResolver();
    // Unannotated interface should not be proxied
    assertFalse(resolver.supportsParameter(new MethodParameter(... MyUnannotatedInterface.class ...)));
    // Annotated interface should be proxied
    assertTrue(resolver.supportsParameter(new MethodParameter(... MyAnnotatedInterface.class ...)));
}
```

- **Example (incorrect — only tests annotated case):**
```java
@Test
public void supportsInterface() {
    ProxyingHandlerMethodArgumentResolver resolver = new ProxyingHandlerMethodArgumentResolver();
    // Only tests annotated interface — misses the filtering bug!
    assertTrue(resolver.supportsParameter(new MethodParameter(... MyAnnotatedInterface.class ...)));
}
```