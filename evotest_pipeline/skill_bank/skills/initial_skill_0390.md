---
name: authorization-exception-propagation-in-hybrid-mapping
description: WHEN testing code where exceptions may be caught and swallowed by a broad
  catch block (e.g., 'catch (Exception e) { e.printStackTrace(); }'), THEN verify
  that domain-specific exceptions are properly propagated to the caller and not silently
  consumed. Test that the method throws the expected exception type when invalid input
  is provided.
code_tags:
- VALIDATION
- EXCEPTION_HANDLING
- EXCEPTION_PROPAGATION
- CATCH_BLOCK
- ERROR_HANDLING
test_pattern: INTERACTION_TEST
retrieval:
  keywords: []
  boosted_tags: []
  suppressed_tags: []
  negative_triggers: []
  applicable_tiers: []
  transition_tags: []
---

# authorization-exception-propagation-in-hybrid-mapping

## Instructions

# Authorization Exception Propagation in Hybrid Page Mapping

## Instructions

### WHEN the TG encounters a method that processes hybrid page requests (like `AbstractBookmarkableMapper.processHybrid(PageInfo, Class, PageParameters, int)`) and there is an authorization strategy that throws a `RestartResponseAtInterceptPageException` for certain page classes:

- THEN the TG should write a test that verifies the `RestartResponseAtInterceptPageException` is propagated through the method call without being caught or wrapped
- Use a stub subclass of `AbstractBookmarkableMapper` that overrides the abstract methods (e.g., `AbstractBookmarkableMapperStub`) to isolate the test to `processHybrid()` behavior
- Configure the application with an `AbstractPageAuthorizationStrategy` that throws a `RestartResponseAtInterceptPageException` for the specific page class under test
- Call `processHybrid()` with a new `PageInfo()`, the authorized-against page class, null page parameters, and a render count of 0
- Assert that the method throws the expected `RestartResponseAtInterceptPageException` — the test should not catch it silently

### Common pitfalls:
- Testing only with page classes that are successfully authorized (passing cases), neglecting the authorization failure case
- Assuming exceptions thrown during authorization are always wrapped in a generic exception like `PageExpiredException` — they should propagate as-is
- Not creating a proper stub implementation of `AbstractBookmarkableMapper` that allows `processHybrid()` to be exercised in isolation
- Forgetting to call `tester.getApplication().getSecuritySettings().setAuthorizationStrategy(...)` or an equivalent test application factory method

### Correct example:
```java
// Configure an application that throws RestartResponseAtInterceptPageException for EmptyPage
@Override
protected WebApplication newApplication()
{
    return new MockApplication()
    {
        @Override
        protected void init()
        {
            super.init();
            getSecuritySettings().setAuthorizationStrategy(
                new AbstractPageAuthorizationStrategy()
                {
                    @Override
                    protected <T extends Page> boolean isPageAuthorized(Class<T> pageClass)
                    {
                        if (pageClass == EmptyPage.class)
                        {
                            throw new RestartResponseAtInterceptPageException(getHomePage());
                        }
                        return true;
                    }
                });
        }
    };
}

// Test that the exception propagates through processHybrid
@Test
public void testProcessHybridWithAuthorizationException()
{
    AbstractBookmarkableMapperStub mapper = new AbstractBookmarkableMapperStub();
    mapper.processHybrid(new PageInfo(), EmptyPage.class, null, 0);
}
```

### Incorrect example — catches the exception silently or tests only the happy path:
```java
@Test
public void testProcessHybridWithAuthorization()
{
    AbstractBookmarkableMapperStub mapper = new AbstractBookmarkableMapperStub();
    try {
        mapper.processHybrid(new PageInfo(), AuthorizedPage.class, null, 0);
    } catch (RestartResponseAtInterceptPageException e) {
        // Bad: silently catching instead of letting it propagate
    }
    // Bad: testing only a page that is successfully authorized, missing the authorization failure path
}
```