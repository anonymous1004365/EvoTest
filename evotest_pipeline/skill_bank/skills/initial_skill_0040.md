---
name: template-engine-log4j-api-backward-compatibility
description: When testing compatibility of template engines (like Apache Velocity)
  with log4j 1.2 API, verify that PatternLayout has a no-arg constructor or that the
  engine's runtime logging doesn't trigger NoSuchMethodError. This skill prevents
  failures from missing default constructors in bridge/compatibility layers.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- INHERITANCE_CHECK
test_pattern: EXCEPTION_TEST
---

# template-engine-log4j-api-backward-compatibility

## Instructions

# Template Engine log4j 1.2 API Backward Compatibility

## Instructions

- WHEN the TG encounters a class (such as `org.apache.log4j.PatternLayout`) that extends `org.apache.log4j.Layout` and is part of a log4j 1.2 compatibility/bridge API
- THEN the TG should check whether the class has ONLY a parameterized constructor (e.g., `PatternLayout(String pattern)`) and NO no-argument constructor. If so, the TG must write a test that exercises code paths where a third-party library (e.g., Apache Velocity) indirectly instantiates this class via reflection using a no-arg constructor.
  - Specifically, write a test that calls `Velocity.init()` followed by `Velocity.getTemplate("some/path")` and `template.merge(vContext, sw)` to trigger the full logging initialization path.
  - The test should expect a `NoSuchMethodError` (or verify it does NOT occur in the fixed version) with a message like `org.apache.log4j.PatternLayout.<init>()` indicating the missing no-arg constructor.
  - Also verify that the `Layout` abstract class correctly requires `ignoresThrowable()` to be implemented so that any subclass must provide it.
- Common pitfalls:
  - Testing only the `PatternLayout(String)` constructor directly (which works fine) while missing the reflective no-arg invocation from third-party engines like Velocity or Log4j's own configuration.
  - Assuming a no-arg constructor exists because log4j 1.2's original `PatternLayout` had one. In bridge APIs, the only constructor may be `PatternLayout(final String pattern)`.

Example test (correct approach):
```java
@Test
public void testVelocity() {
    Velocity.init();
    final VelocityContext vContext = new VelocityContext();
    vContext.put("name", new String("Velocity"));
    final Template template = Velocity.getTemplate("target/test-classes/hello.vm");
    final StringWriter sw = new StringWriter();
    template.merge(vContext, sw);
}
```

Incorrect approach (does NOT trigger the bug):
```java
@Test
public void testPatternLayoutDirect() {
    PatternLayout layout = new PatternLayout("%m%n"); // works fine, doesn't test reflection path
    LoggingEvent event = new LoggingEvent(...);
    String result = layout.format(event);
}
```