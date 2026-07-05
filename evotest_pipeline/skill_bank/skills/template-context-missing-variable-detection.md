---
name: template-context-missing-variable-detection
description: When a method populates a template rendering context (VelocityContext,
  Map model) and templates reference variables, cross-reference template variable
  usage against context.put() calls to identify missing variables. Write tests that
  assert each template-referenced variable is present in the context after preparation.
code_tags:
- TEMPLATE_RENDERING
- CONTEXT_POPULATION
- STATE_TEST
- VELOCITY
test_pattern: STATE_TEST
evolution:
  active: true
  priority: 0
  evidence:
    added: 1
retrieval:
  applicable_tiers:
  - BUG_DETECTED
  - PASS_BOTH
  transition_tags: []
  keywords:
  - template
  - context
  - put
  - Velocity
  - FreeMarker
  - missing variable
  - prepareReport
---

WHEN the TG encounters a method that populates a template rendering context via context.put(key, value) calls, AND template files (.vm, .html, .ftl) reference variables: THEN (1) identify all variable names in template files, (2) cross-reference against context.put() calls, (3) write tests verifying each referenced variable is present after preparation, (4) for boolean/conditional variables test both default and enabled values, (5) verify total context key count matches expectations. Common pitfall: only testing the happy path where all variables are present.