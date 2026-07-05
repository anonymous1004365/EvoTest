---
name: intercept-data-ajax-parameter-filtering
description: When code captures request parameters for later replay (e.g., intercept
  data), ajax-specific parameters must be filtered out from both URL query parameters
  and post parameters to prevent the continued request from being treated as an ajax
  request. Use this skill when testing code that saves request state during an intercept/redirect.
code_tags:
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# intercept-data-ajax-parameter-filtering

## Instructions

# Intercept Data Should Strip Ajax Parameters

## Instructions

- WHEN the code captures request parameters (URL query params and/or post parameters) during an intercept/redirect to be replayed later  
- THEN the test MUST verify that ajax-specific parameters are stripped from both the saved URL and the saved post parameters  
- WHEN verifying URL query parameters, use `Url.getQueryParameter(name)` and assert the value is null for each ajax parameter  
- WHEN verifying post parameters, use `Map.get(name)` and assert the return value is null for each ajax parameter  
- Include assertions for at least `WebRequest.PARAM_AJAX` (`"wicket-ajax"`) and `WebRequest.PARAM_AJAX_BASE_URL` (`"wicket-ajax-baseurl"`)  
- Also check `WebRequest.PARAM_AJAX_REQUEST_ANTI_CACHE` (`"_"`) if present in the code  
- The test must exercise the intercept path by making an ajax request (with ajax parameters in the URL) and then inspecting the saved intercept data  
- Common pitfall: testing only that ajax parameters are absent from the post parameters but forgetting to also check URL query parameters, or vice versa  
- Common pitfall: asserting that the ajax parameters are missing from the overall request, rather than asserting they are missing from the *saved* intercept data structure  
- Common pitfall: forgetting to test with `PARAM_AJAX_REQUEST_ANTI_CACHE` (the `"_"` cache-busting parameter)

**Correct example:**
```java
// Issue an ajax request with ajax-specific parameters
tester.executeAjaxUrl(Url.parse("?" + WebRequest.PARAM_AJAX + "=true&" + 
    WebRequest.PARAM_AJAX_BASE_URL + "=/&" + 
    WebRequest.PARAM_AJAX_REQUEST_ANTI_CACHE + "=12345"));

// Verify the intercept data strips ajax parameters from URL
InterceptData data = InterceptData.get();
assertNull("PARAM_AJAX should be removed from saved URL",
    data.getOriginalUrl().getQueryParameter(WebRequest.PARAM_AJAX));
assertNull("PARAM_AJAX_BASE_URL should be removed from saved URL",
    data.getOriginalUrl().getQueryParameter(WebRequest.PARAM_AJAX_BASE_URL));

// Verify the intercept data strips ajax parameters from post parameters
assertNull("PARAM_AJAX should be removed from saved post params",
    data.getPostParameters().get(WebRequest.PARAM_AJAX));
assertNull("PARAM_AJAX_BASE_URL should be removed from saved post params",
    data.getPostParameters().get(WebRequest.PARAM_AJAX_BASE_URL));
```

**Incorrect example (missing URL parameter check):**
```java
tester.executeAjaxUrl(Url.parse("?" + WebRequest.PARAM_AJAX + "=true"));
InterceptData data = InterceptData.get();
// Only checks post parameters, misses URL query parameters
assertNull(data.getPostParameters().get(WebRequest.PARAM_AJAX));
// Missing: assertNull(data.getOriginalUrl().getQueryParameter(WebRequest.PARAM_AJAX));
```