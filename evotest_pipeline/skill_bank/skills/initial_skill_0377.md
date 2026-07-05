---
name: resource-content-type-initialization
description: When a resource class accepts a content type parameter but fails to pass
  it to the parent constructor, the content type becomes null. This skill teaches
  how to test that content type parameters propagate correctly through resource constructors,
  especially for byte array resources.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# resource-content-type-initialization

## Instructions

# Resource Content Type Initialization

## Instructions

- WHEN the TG encounters a resource class (such as `ByteArrayResource` or any subclass of `AbstractResource`) that accepts a `contentType` String parameter in its constructor
- THEN the TG should write a test that:
  1. Constructs an instance of the resource by passing a non-null content type string (e.g., `"application/octet-stream"`) to the constructor
  2. Calls the method that returns or exposes the content type (e.g., `getContentType()` or inspecting the response's content type header)
  3. Asserts that the returned content type equals the original value passed to the constructor
  4. Specifically uses `assertEquals("application/octet-stream", resource.getContentType())` or the equivalent method

- WHEN the resource class accepts a `contentType` parameter but does not explicitly pass it to the parent class constructor via `super(contentType)`
- THEN the test should verify that the content type is not null and matches the expected value, because failing to chain the constructor leads to a null content type at runtime

- Common pitfalls to avoid:
  - Testing only that construction succeeds without verifying the content type value
  - Testing with `null` content type only (which may accidentally pass on the buggy version)
  - Testing the wrong method — ensure the test calls the actual method that returns the content type (e.g., `getContentType()` or the response's `getContentType()` on a `ResourceResponse`)
  - Forgetting to check the content type on the `ResourceResponse` object returned from the resource

### Correct Example

```java
@Test
public void contentType()
{
    ByteArrayResource resource = new ByteArrayResource("application/octet-stream", new byte[] {1, 2, 3});
    Assert.assertEquals("application/octet-stream", resource.getContentType());
}
```

### Incorrect Example (fails to detect the bug)

```java
@Test
public void contentType()
{
    ByteArrayResource resource = new ByteArrayResource("application/octet-stream", new byte[] {1, 2, 3});
    // Only checks that construction doesn't throw, but doesn't verify content type
    Assert.assertNotNull(resource);
}
```