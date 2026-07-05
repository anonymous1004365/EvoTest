---
name: host-class-import-awareness-for-injected-tests
description: WHEN generating test methods that will be injected into an existing host
  test class, inspect the host class's import statements and ensure all classes used
  are either already imported, covered by wildcard imports, or added as new imports.
  Use fully qualified names for classes in different packages.
code_tags:
- IMPORT_AWARENESS
- HOST_CLASS_INJECTION
- TEST_GENERATION
- PACKAGE_MISMATCH
test_pattern: STATE_TEST
evolution:
  active: true
  priority: 0
  evidence:
    added: 1
retrieval:
  applicable_tiers:
  - FAIL_ON_FIXED
  - FAIL_ON_BUGGY
  - COMPILE_FAIL
  transition_tags:
  - IMPORT_ERROR
  - COMPILATION_ERROR
  - PACKAGE_MISMATCH
  keywords:
  - import
  - host class
  - injection
  - Base64
  - missing symbol
  - compilation
  - fully qualified
  - package
---

WHEN the TG generates test methods for injection into a host test class: (1) read the host class's import statements, (2) for each class used in generated methods verify it is importable from existing imports, (3) if a class like java.util.Base64 is needed but not imported, either add the import or refactor to avoid the dependency (e.g., hardcode expected values), (4) use fully qualified names for classes in different packages (e.g., org.netpreserve.jwarc.cdx.CdxWriter instead of CdxWriter). Pay special attention to java.util.* vs explicit imports like java.util.Arrays, java.util.Collections.