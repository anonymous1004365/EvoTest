---
name: tilde-expansion-only-at-path-start
description: WHEN testing file path expansion methods that replace `~` with the user's
  home directory, verify that the tilde is ONLY expanded when it appears at the start
  of the path (e.g., `~/file.txt`), and NOT when it appears in the middle or end (e.g.,
  `test~file.txt` should remain unchanged).
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- PATH_PARSING
- TILDE_EXPANSION
- FILE_PATH
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
  - tilde
  - expand
  - home directory
  - path expansion
  - startsWith
  - file path
  - '~'
  - user.home
  - expandFileNames
  - SnowflakeFileTransferAgent
---

WHEN the focal method expands `~` (tilde) to the user's home directory in file paths: 1) Check if the method uses `path.startsWith("~")` (correct) or `path.contains("~")` / `path.replace("~", ...)` (buggy). 2) Write a test that creates a file with `~` in the middle of its name (e.g., `test~file.txt`), passes its absolute path to the expansion method, and verifies the result contains the exact same path without expanding the middle `~`. 3) Also test that `~` at the START of a path IS correctly expanded. 4) Also test that `~` at the END of a path is NOT expanded.