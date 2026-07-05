---
name: pretty-printer-output-after-mutation
description: When testing pretty printers that cache or build formatted output from
  mutable state (e.g., token lists, element lists), the TG should verify that modifying
  the source state after printing produces correct output, and that the printer captures
  the state at the time of printing, not a stale reference.
code_tags:
- STATE_MUTATION
test_pattern: STATE_TEST
---

# pretty-printer-output-after-mutation

## Instructions

# Pretty Printer Output Consistency After State Mutation

## Instructions

**WHEN** the TG encounters a pretty printer, formatter, or code generator that builds output by iterating over mutable state such as a list of tokens, elements, or children (e.g., `List<CtElement>`, `List<SpoonToken>`, `List<String>`):
- **THEN** the TG should write a test that:
  1. Creates the source object (e.g., a `CtElement`, AST node, or model)
  2. **Calls the printing method** (e.g., `printElement()`, `prettyPrint()`, `toString()`, `write()`) to produce a first output string
  3. **Mutates the underlying state** (e.g., adds/removes child elements, modifies tokens, clears a list)
  4. **Calls the printing method again** on the same printer instance to produce a second output string
  5. **Verifies** that the first and second outputs are different if and only if the mutation should affect the output (i.e., the printer reads the state at call time, not from a stale cache)
- **Common pitfalls:**
  - ❌ Only testing with a fresh printer for each scenario (misses bugs where printers reference mutable state they don't own)
  - ❌ Only testing output correctness without mutating state between calls (misses stale reference bugs)
  - ❌ Assuming the printer creates defensive copies of list parameters (it likely stores the reference directly)
  - ❌ Testing with only one type of mutation (e.g., only add, but not remove or clear)

## Examples

### ✅ Correct test pattern (Java-like pseudocode):
```java
// Create source element with one child
CtElement parent = factory.createClass("Parent");
CtElement child = factory.createMethod("childMethod");
parent.addChild(child);

// Create printer
PrettyPrinter printer = new DefaultPrettyPrinter(factory.getEnvironment());

// First print — should include the child
String firstOutput = printer.printElement(parent);
assertTrue(firstOutput.contains("childMethod"));

// Mutate state: remove the child from the parent's internal list
parent.removeChild(child);

// Second print — should NOT include the child
String secondOutput = printer.printElement(parent);
assertFalse(secondOutput.contains("childMethod"));
// The bug is if secondOutput still contains "childMethod" because
// the printer cached/stored a reference to the old list.
```

### ❌ Incorrect test pattern (misses the bug):
```java
// Only testing with two separate parent objects (no mutation between calls)
CtElement parent1 = factory.createClass("Parent1");
parent1.addChild(factory.createMethod("child1"));

CtElement parent2 = factory.createClass("Parent2");
// parent2 has no children

String output1 = printer.printElement(parent1);
String output2 = printer.printElement(parent2);
// This test passes even if the printer has a stale-reference bug,
// because no mutation happened on the same element between calls.
```

### ❌ Another incorrect test pattern (no back-to-back mutation):
```java
// Prints once, then creates a completely new printer for second print
// This doesn't exercise the cached/aliased reference path
PrettyPrinter printer1 = new DefaultPrettyPrinter(env);
String out1 = printer1.printElement(parent);

parent.removeChild(child);  // mutation

PrettyPrinter printer2 = new DefaultPrettyPrinter(env);
String out2 = printer2.printElement(parent);
// Bug may not trigger because printer2 doesn't hold a stale reference
```

## When This Skill Applies

This skill is most relevant when:
- The printer/formatting class stores references to mutable objects passed to it (e.g., `this.elements = input.getElements()` without defensive copying)
- The printer is designed to be reused (not single-use)
- The source object (AST, model, document) exposes methods that mutate its child/content structure after the printer has been initialized