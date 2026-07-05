---
name: template-parameter-heterogeneous-type
description: When a codebase stores heterogeneous types (e.g., String and CtTypeReference)
  in the same parameter collection/registry, tests must exercise each distinct type
  path to reveal type-mismatch or ClassCastException bugs.
code_tags:
- VALIDATION
- STATE_MUTATION
- NULL_CHECK
- TEMPLATE_PARAMETER_HETEROGENEOUS_TYPES
test_pattern: PARAMETRIC_TEST
---

# template-parameter-heterogeneous-type

## Instructions

# Template Parameter Heterogeneous Type Testing

## Instructions

- WHEN the TG encounters code that stores or processes template/proxy parameters in a collection or registry (e.g., a `Map<String, Object>`, `List<Object>`, or custom parameter holder), and those parameters may be of different types (e.g., `String`, `CtTypeReference`, `Integer`, etc.):
  - THEN the TG should write a test that supplies parameters of **each distinct type** the system supports, and verify the buggy code handles every type without throwing a `ClassCastException`, `NullPointerException`, or silently producing incorrect output.
  - Include concrete examples: e.g., add one parameter of type `String` ("foo") and one parameter of type `CtTypeReference` (representing `int`), then call the method under test and assert the output/decorated result correctly reflects both parameters.

- WHEN the test exercises methods like `writeStartObject()`, `writeFieldName()`, `serialize()`, `decorate()`, or any method that iterates over parameters:
  - THEN the TG should assert that the output after processing each parameter type is correct. For example, a decorator that wraps each parameter in a wrapper element should produce the proper wrapped output for String parameters **and** for TypeReference parameters.

- WHEN the code selects/casts based on `instanceof` checks on parameters:
  - THEN the TG must verify that every branch of the `instanceof` cascade is covered by at least one test parameter. If a branch is missing (e.g., no parameter triggers a particular `instanceof` type), the bug may go unnoticed.

- **Common pitfalls to avoid**:
  - Testing only with `String` type parameters when the system also supports `CtTypeReference` parameters — this misses ClassCastException or logic-skip bugs.
  - Assuming all parameters in a collection are the same type — always include heterogeneous types in the test data.
  - Writing a test that passes but silently produces wrong output — always add an assertion on the final output content/structure, not just "no exception."

## Examples

### Correct test pattern (catching the bug)

```java
// Given a template with parameters of different types
ProxyTemplate proxyTemplate = ...
proxyTemplate.setSignature("wrap"); // the template method signature
proxyTemplate.addParameter("value", "hello");       // String type parameter
proxyTemplate.addParameter("someType", int.class); // CtTypeReference/Class type parameter

// When the template is rendered with a decorator
OutputStream out = new ByteArrayOutputStream();
JsonGenerator gen = new CBORGenerator(out, 0);
StreamingDecorators.TemplateDecorator decorator = new StreamingDecorators.TemplateDecorator(gen);
decorator.decorate(proxyTemplate.getSignature(), proxyTemplate.getParameters().values());

// Then both parameter types should be correctly rendered
// (without ClassCastException from assuming all params are String)
```

### Incorrect test pattern (missing the bug)

```java
// ❌ Testing only with String parameters — does not exercise the CtTypeReference path
ProxyTemplate proxyTemplate = ...
proxyTemplate.setSignature("wrap");
proxyTemplate.addParameter("value", "hello");
proxyTemplate.addParameter("name", "world");  // Both are String!

// This test would pass even in the buggy version, missing the heterogeneous type bug
```

### Another correct pattern

```java
// When the system stores parameters as Map<String, Object> with mixed types
Map<String, Object> params = new HashMap<>();
params.put("strParam", "testString");
params.put("typeParam", CtTypeReference.forClass(int.class));
params.put("numParam", 42);  // third type if supported

// Test must iterate all values and verify no exception occurs for any type
for (Object param : params.values()) {
    assertDoesNotThrow(() -> processor.process(param));
}
```