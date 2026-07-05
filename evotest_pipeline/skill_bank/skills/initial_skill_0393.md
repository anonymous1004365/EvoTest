---
name: osgi-service-bind-before-activate
description: ''
code_tags:
- SERVICE_BINDING_BEFORE_ACTIVATE
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# osgi-service-bind-before-activate

## Instructions

# OSGI Service Bind Before Activate

## Instructions

WHEN the TG encounters a Declarative Services component (annotated with
`@Component` or similar) that binds an external service via a `bind*` method
(e.g., `bindExtractedTextProvider`), and that bind method accesses fields that
are normally populated during the component's `activate()` method:

- THEN the TG MUST write a test that first calls the bind method directly
  (simulating the service being bound before `activate()` runs), then calls
  `activate()`, and verifies the component still works correctly.

- THEN the TG MUST specifically test the case where the bind method is called
  while the field(s) normally set by `activate()` are still `null`, and verify
  that NO `NullPointerException` or other exception is thrown.

- THEN the TG MUST verify that any internal data structure (e.g., a
  `Map<String, ExtractedTextCache>` or similar) that the bind method is supposed
  to update is correctly populated after both the bind call and the activate
  call have completed.

- Common pitfalls include:
  - Only testing with the service bound after `activate()` (the normal SCR lifecycle).
  - Forgetting that SCR can inject dependencies at any point — before, during, or
    after activation.
  - Assuming that the bind method is always called after `activate()` and not
    guarding against null fields in the bind method.
  - Not testing with a mock or stub service implementation for the bound service
    type (e.g., `PreExtractedTextProvider`).

### Correct Example (Java pseudo-code)

```java
@Test
public void preExtractedProviderBindBeforeActivate() throws Exception {
    // Create the service component instance directly (no SCR)
    var service = new MyService();

    // Create a mock of the bound service
    PreExtractedTextProvider mockProvider = mock(PreExtractedTextProvider.class);

    // 1. Bind the service BEFORE activate (opposite of normal order)
    service.bindExtractedTextProvider(mockProvider);

    // 2. Now call activate
    service.activate(/* component context */);

    // 3. Verify no exception occurred and the internal state is correct
    //    e.g., the provider was registered/stored properly
    assertNotNull(service.getExtractedTextCache());
    // Verify the bind was processed (e.g., the mock provider was stored)
}
```

### Incorrect Example (pitfall to avoid)

```java
// BAD: Only tests the normal lifecycle order
@Test
public void preExtractedTextProvider_normalOrder() throws Exception {
    var service = new MyService();
    service.activate(/* context */);  // activate first

    PreExtractedTextProvider mockProvider = mock(PreExtractedTextProvider.class);
    service.bindExtractedTextProvider(mockProvider); // bind after activate

    // This passes but misses the bug where bind is called before activate
    // The bug would only manifest when bind happens before activate
}
```

### Concrete values from the actual bug

- Component class: `LuceneIndexProviderService`
- Activate method: `activate(ComponentContext)` — initializes internal fields
- Bind method: `bindExtractedTextProvider(PreExtractedTextProvider)` — stores the
  provider into an internal data structure, but fails if called before `activate()`
  because the data structure is null
- Triggering test: `preExtractedProviderBindBeforeActivate()` in
  `LuceneIndexProviderServiceTest`
- Expected behavior: The bind method should guard against null fields and work
  regardless of whether `activate()` has been called yet