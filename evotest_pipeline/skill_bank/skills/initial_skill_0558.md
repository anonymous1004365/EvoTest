---
name: invocation-argument-type-checking
description: When a method invocation returns a type expression (TypeAccess, TypeReference),
  ensure tests verify both result variables and direct method arguments. This catches
  bugs where the internal representation confuses type accesses with method arguments.
code_tags:
- VALIDATION
- NULL_CHECK
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# invocation-argument-type-checking

## Instructions

# Invocation Argument Type Checking

## Instructions

- WHEN the TG encounters code that processes method invocation arguments and builds AST nodes (e.g., `CtInvocation`, `CtTypeAccess`, `CtTypeReference`), specifically when determining whether a given node should be treated as a **type access** (e.g., `CtTypeAccess`) vs. a **value expression** (e.g., `CtInvocation` for `String.format(...)`)
- THEN the TG should write a **parametric test** that verifies the following:
  1. Create a code snippet where a **method invocation is passed as an argument** — for example: `sink(String.format(...))` — and verify that the outer invocation's argument **is a `CtInvocation`**, NOT a `CtTypeAccess` or `CtTypeReference`.
  2. For both the **method argument position** and the **result variable assignment**, assert the correct `CtElement` subclass using `assertTrue(argument instanceof CtInvocation)` or `assertThat(argument, instanceOf(CtInvocation.class))`.
  3. Include both: (a) one case where the argument is a simple type reference (like `String.class` or a generated type parameter), and (b) another case where the argument is a method call (like `String.format(...)`).
  4. Verify that `CtTypeAccess` nodes are **not** created for statements that are clearly method invocations. A common failure sign is that `getArguments()` contains a `CtTypeAccess` where a `CtInvocation` is expected.
- Common pitfalls to avoid:
  - ❌ Testing only the **return type**/result variable and ignoring the **argument list** of the outer invocation.
  - ❌ Assuming that all generated arguments are `CtTypeReference` or `CtTypeAccess` — the bug manifests specifically when a **method call** argument is incorrectly wrapped as a type reference.
  - ❌ Relying solely on `toString()` output instead of checking the actual runtime type of the argument with `instanceof`.

### Correct Example (catches the bug)
```java
// Buggy version reports argument as CtTypeAccess instead of CtInvocation
CtInvocation outerInvocation = ...; // from: sink(String.format("hello %s", name))
List<CtExpression<?>> args = outerInvocation.getArguments();
assertEquals(1, args.size());
// The argument should be a CtInvocation (String.format(...)), not a CtTypeAccess
assertTrue("Argument should be a CtInvocation, got: " + args.get(0).getClass(),
    args.get(0) instanceof CtInvocation);
```

### Incorrect Example (misses the bug)
```java
// ❌ This only checks the outer invocation, not the argument type
CtInvocation outerInvocation = ...;
assertNotNull(outerInvocation);
assertEquals("sink", outerInvocation.getExecutable().getSimpleName());
// ❌ Missing: check that the argument is a CtInvocation, not a CtTypeAccess
```

### Concrete test structure
```java
@Test
public void testArgumentOfAInvocationIsNotATypeAccess() {
    String code = "class X { void m() { sink(String.format(\"hello %s\", \"world\")); } }";
    CtClass<?> type = launcher.addInputResource(...).buildModel().getAllTypes().iterator().next();
    CtMethod<?> method = type.getMethodsByName("m").get(0);
    CtInvocation<?> outer = method.getBody().getStatement(0); // sink(...)
    CtExpression<?> arg = outer.getArguments().get(0);
    // 🚨 MUST be CtInvocation, not CtTypeAccess
    assertTrue("argument of sink() should be invocation, not: " + arg.getClass(),
        arg instanceof CtInvocation);
}
```