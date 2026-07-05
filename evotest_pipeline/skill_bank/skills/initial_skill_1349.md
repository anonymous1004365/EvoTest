---
name: one-indexed-pageable-argument-validation
description: When a Pageable argument resolver supports one-indexed pages (e.g., Spring
  Data's OneIndexedPageableHandlerMethodArgumentResolver), the test generator should
  verify that PagedResourcesAssembler correctly converts such page values to zero-indexed
  page numbers when building pagination links, and should test with an initial page
  value of 1 as well as page value 1 with size 1.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# one-indexed-pageable-argument-validation

## Instructions

# One-Indexed Pageable Argument Validation

## Instructions

- WHEN the TG encounters a `PagedResourcesAssembler` that constructs pagination links (e.g., calls `createLinkForSingleResource`, `appendPageParameter`, or builds `Link` objects from `Pageable` metadata), and the codebase contains a `OneIndexedPageableHandlerMethodArgumentResolver`
- THEN the TG MUST write a parametric test that:
  1. Configures a Spring MVC `MockHttpServletRequest` and `RequestContextHolder` to simulate a request with `page=1` and `size=1` as query parameters
  2. Creates a `PageableHandlerMethodArgumentResolver` (or `OneIndexedPageableHandlerMethodArgumentResolver` if available) and resolves the `Pageable` from the request, ensuring the resolver uses `oneIndexedParameters=true`
  3. Constructs a `PagedResourcesAssembler` (e.g., `new PagedResourcesAssembler<Object>(handlerMethodArgumentResolver, null)`), passing the resolver as the argument
  4. Creates a `PageImpl` (e.g., `new PageImpl<>(Collections.singletonList("first"), pageable, 20L)`) — with total elements > size so that next/prev links are generated
  5. Calls `assembler.toResources(page)` and verifies that the resulting `PagedResources` contains pagination `Link` objects with correct `page` numbers in their `href` values
  6. Specifically asserts that the **first page link** (self or first) uses `page=1` (not `page=0`), the **next page link** uses `page=2`, and there is **no previous page link**
  7. The test should expect that on the buggy version, the pagination links are built with `page=0` for the first page (zero-indexed), or the test fails with an `AssertionError`/`Exception` because the links reference incorrect page numbers

- Common pitfalls to avoid:
  - **Using `page=0` in the request**: The resolver treats `page=1` as the first page in one-indexed mode; `page=0` is not valid
  - **Testing only with `page=1` and large size**: The bug manifests specifically when `page=1` and `size=1` cause incorrect link generation; also test `page=1` with `size=1` to force next-page calculation
  - **Forgetting to set `RequestContextHolder`**: The `PagedResourcesAssembler` reads the current request from `RequestContextHolder` to build absolute URLs; the test must set up a mock request with `RequestContextHolder.setRequestAttributes(new ServletRequestAttributes(request))`
  - **Asserting only presence of links, not their correct `href` values**: The bug is in the numeric `page` parameter value, not the existence of links; assert the exact `href` string (e.g., `Link("http://localhost/api?page=1&size=1", "first")`)

- Correct example:
```
MockHttpServletRequest request = new MockHttpServletRequest();
request.setServletPath("/api");
request.addParameter("page", "1");
request.addParameter("size", "1");
RequestContextHolder.setRequestAttributes(new ServletRequestAttributes(request));

PageableHandlerMethodArgumentResolver resolver = new PageableHandlerMethodArgumentResolver();
resolver.setOneIndexedParameters(true);
Pageable pageable = resolver.resolveArgument(null, null, webRequest, null);

PagedResourcesAssembler<Object> assembler = new PagedResourcesAssembler<>(resolver, null);
PageImpl<Object> page = new PageImpl<>(Collections.singletonList("first"), pageable, 20L);
PagedResources<Object> resources = assembler.toResources(page);

assertThat(resources.getLink("first")).isPresent();
assertThat(resources.getLink("first").get().getHref()).contains("page=1");
assertThat(resources.getLink("next")).isPresent();
assertThat(resources.getLink("next").get().getHref()).contains("page=2");
```

- Incorrect example to avoid:
```
// BUGGY: uses page=0 in request, expects page=0 in links — misses the one-indexed conversion
MockHttpServletRequest request = new MockHttpServletRequest();
request.addParameter("page", "0");
request.addParameter("size", "1");
// ... assembler creates links with page=0, test passes on buggy version, fails to catch the bug
```