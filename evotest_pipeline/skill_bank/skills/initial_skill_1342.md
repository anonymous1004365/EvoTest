---
name: bean-ognl-chain-method-selection
description: When writing tests for OGNL-style bean method invocation chains (e.g.,
  `beanInstance.methodA.methodB`), the TG should test that each method in the chain
  returns a compatible type for the next method invocation. The key risk is that the
  framework selects an incorrect overloaded method when the intermediate return type
  doesn't match expected types.
code_tags:
- NULL_CHECK
- TYPE_CONVERSION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# bean-ognl-chain-method-selection

## Instructions

# Bean OGNL Chain Method Selection

## Instructions

- WHEN the TG encounters an OGNL-style bean expression that chains multiple method calls (e.g., `getOther.getOther` or `getBean.getOther.doSomething`), where the intermediate method returns a type that is later used as the target for another method invocation
- THEN it should test with the exact chained expression as the bean method parameter, verifying that the **final output** is the result of the last method in the chain, NOT the toString() representation of an intermediate object
- Specifically, WHEN the bean expression is a dotted chain like `getOther.getOther` and the chain terminates at a method that returns a String, THEN the test should verify that the expression evaluates to the String value, not to the intermediate object's toString()

### Concrete example from this bug
The bug was in `BeanExpression` where a chain like `getOther.getOther` (where `getOther()` → `MyOtherReallyCoolBean`, and `.getOther()` → String "World") was incorrectly evaluating to the intermediate `MyOtherReallyCoolBean@hash` instead of the final String "World". The test should use:

```java
// CORRECT - verifies the full chain resolves properly
BeanExpression expr = new BeanExpression("bean", "getOther.getOther");
MyCoolBean bean = new MyCoolBean();
Exchange exchange = new DefaultExchange(context);
exchange.getIn().setBody(bean);
Object result = expr.evaluate(exchange, String.class);
assertEquals("World", result);
```

```java
// INCORRECT - only tests single method, not the chain
BeanExpression expr = new BeanExpression("bean", "getOther");
MyCoolBean bean = new MyCoolBean();
Exchange exchange = new DefaultExchange(context);
exchange.getIn().setBody(bean);
Object result = expr.evaluate(exchange, String.class);
assertEquals("MyOtherReallyCoolBean", result); // Wrong! Tests wrong level
```

- WHEN the chain involves methods that return different types (e.g., `MyCoolBean.getOther()` returns `MyOtherReallyCoolBean`, and `MyOtherReallyCoolBean.getOther()` returns `String`), THEN the test must verify the full chain resolves to the correct final type, not just any intermediate type
- Common pitfalls to avoid:
  - Testing only single-hop OGNL expressions (e.g., `getOther`) when the bug is in multi-hop chaining (e.g., `getOther.getOther`)
  - Assuming that if the first method works, the full chain will work — the method selection logic may differ for intermediate return types
  - Not checking what `toString()` of intermediate objects returns, which can mask the bug (the buggy output was `toString()` of the intermediate bean — a valid but wrong result)
  - Testing only with `String` return types — the bug may only manifest when intermediate types are custom domain objects