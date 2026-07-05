---
name: reconfiguration-monitor-state-reset
description: When a configuration monitor detects changes and triggers reconfiguration,
  the internal state (such as file lastModified) must be properly reset BEFORE reconfiguration
  begins to avoid re-triggering with stale timestamps. This skill helps the TG write
  tests that catch reconfiguration loops and state leakage.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- STATE_MUTATION
- CONCURRENCY
- VALIDATION
test_pattern: STATE_TEST
---

# reconfiguration-monitor-state-reset

## Instructions

# Reconfiguration Monitor State Reset

## Instructions

- WHEN the TG encounters a configuration reconfiguration mechanism (e.g., `FileConfigurationMonitor`, `reconfigure()` method triggered by a file watcher or poller)
- THEN it should verify that the monitor's internal state (e.g., `lastModified` timestamp, `fileLastModified` field) is properly updated or reset **before** the reconfiguration call, not after. Failing to reset state before reconfiguration can cause:
  - Stale timestamps that cause a second reconfiguration immediately after the first
  - Reconfiguration loops (infinite or unexpected)
  - The monitor detecting the same change multiple times

- The TG should test that:
  1. The monitor correctly detects a configuration file change (e.g., file modification).
  2. After `reconfigure()` completes, the monitor does NOT re-trigger with the same file timestamp.
  3. The `lastModified` timestamp is updated at the correct point in the reconfiguration flow (before reconfiguration), not lazily or after.

- **Common pitfalls to avoid:**
  - Testing only the happy path where reconfiguration succeeds once, without verifying idempotent behavior.
  - Assuming that a file's `lastModified` is always updated by the caller or OS before the next poll cycle.
  - Not resetting `isConfigurationModified()` state after a reconfiguration attempt, leading to repeated reconfigurations.

- **Correct example:**
  - Simulate a file change (modify timestamp), call `reconfigure()`, assert reconfiguration occurred, then call `reconfigure()` again with the same file state — assert that no second reconfiguration occurs (or that the config object reference is the same).

- **Incorrect example:**
  - Simulating a file change and calling `reconfigure()` once, asserting the config changed, but not verifying that a subsequent `reconfigure()` call does NOT trigger again with the same file timestamp — this misses the core bug of repeated reconfiguration.