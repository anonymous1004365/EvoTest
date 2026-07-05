---
name: swagger-resource-not-found-handling
description: When a Swagger/OpenAPI resource endpoint is expected to return an HTTP
  404 for non-existent resources but fails to do so, this skill teaches the TG to
  test that the endpoint returns a properly handled error response (404) instead of
  throwing an exception or returning an unexpected status.
code_tags:
- SWAGGER_RESOURCE_NOT_FOUND_HANDLING
test_pattern: EXCEPTION_TEST
---

# swagger-resource-not-found-handling

## Instructions

# Swagger Resource Not Found Handling

## Instructions

- WHEN the TG encounters a `SwaggerResource` class (or similar Swagger/OpenAPI resource handler) that has a method for serving Swagger documentation (e.g., `getSwagger()`, `swaggerJson()`, etc.)
- THEN the TG should write a test that:
  1. Creates an instance of the Swagger resource endpoint class
  2. Calls the method that serves Swagger documentation with a path/resource identifier that does NOT exist (e.g., a random UUID, unknown resource path)
  3. Verifies that the response is an HTTP 404 (not found) status code, NOT an exception thrown
  4. Verifies that the response body or error message is appropriate for a "not found" scenario

- Common pitfalls:
  - ❌ **Testing only the happy path** (requesting a valid Swagger resource and checking success)
  - ❌ **Assuming the method returns null** — the bug may be that the method returns null or throws an uncaught exception instead of returning a proper 404 response
  - ❌ **Expecting an exception** — the correct behavior is to return a properly formed 404 response, not throw an exception or return an unexpected status
  - ❌ **Not testing with an invalid/unknown resource identifier** — only testing with valid known paths

- Example (correct):
  ```java
  @Test
  public void testNotFound() {
      SwaggerResource resource = new SwaggerResource(apiService);
      // Use a path/resource that does not exist
      Response response = resource.getSwagger("nonexistent-resource-id");
      // Should return 404, not throw an exception
      assertEquals(404, response.getStatus());
      // Optional: verify response entity contains error description
      assertNotNull(response.getEntity());
  }
  ```

- Example (incorrect — only tests happy path):
  ```java
  @Test
  public void testGetSwagger() {
      SwaggerResource resource = new SwaggerResource(apiService);
      Response response = resource.getSwagger("valid-resource");
      assertEquals(200, response.getStatus());  // Only tests success
  }
  ```