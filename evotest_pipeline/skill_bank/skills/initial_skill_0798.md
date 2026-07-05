---
name: load-balancer-uneven-tablet-migration-count
description: WHEN testing a load balancer's getMigrations() method for uneven tablet
  distribution across servers, THEN verify that the total number of migration operations
  computed from the result list does not exceed the actual number of excess tablets.
  This skill covers integer division and remainder logic for computing how many tablets
  to move from overloaded to underloaded servers.
code_tags:
- STATE_MUTATION
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# load-balancer-uneven-tablet-migration-count

## Instructions

# Load Balancer Uneven Tablet Migration Count

## Instructions

WHEN the TG encounters a load balancing algorithm that:
1. Computes `even = total / numServers` and `numServersOverEven = total % numServers`
2. Uses a `goal` per server that is `even` (or `even + 1` for the first `numServersOverEven` servers)
3. Computes `needToUnload = tooMany.count - goal` as the number of tablets to move away
4. Iterates through a sorted list of `ServerCounts` from high to low, pairing overloaded servers with underloaded servers
5. Calls `move()` which returns a `List<TabletMigration>` for each pair, accumulating into a result list

THEN the TG should:
- Create a test scenario where one server has more excess tablets than there are servers (e.g., 26 servers with 1 tablet each, plus 9 extra tablets on one server = 35 total, even=35/26=1, numServersOverEven=9, servers at index < 9 get goal=2, others get goal=1)
- Set up the test so that the overloaded server has significantly more tablets than the average (e.g., 10 tablets on a server when others have 1 each, with 26 total servers)
- After calling `getMigrations(current, result)`, compute the total number of tablets moved by summing the **count** parameter passed to `move()`, NOT just checking `result.size()`
- Verify that `needToUnload` is correctly computed as `tooMany.count - goal` (not `tooMany.count - goal + 1`)
- Specifically verify that when `needToUnload >= needToLoad`, the number of migrations added equals `needToLoad` (not `needToLoad + 1`)
- Use `assertEquals(expectedCount, actualCount)` to compare against hand-computed expected values

Common pitfalls to avoid:
- Checking only `result.size()` without verifying that the aggregated migration amount matches the expected redistribution. A single `move()` call returns one `TabletMigration` per tablet, but a bug can cause it to move one extra tablet beyond what's needed.
- Assuming that `goal = even + (tooManyIndex < numServersOverEven ? 1 : 0)` is correct without validating the off-by-one logic in the main loop.
- Forgetting to account for `movedAlready` tracking when `needToUnload < needToLoad`, which adjusts how `needToLoad` is computed in subsequent iterations.

Correct example:
```java
// 26 servers with 1 tablet each (one table "a"), plus 9 extra tablets on first server from "newTable"
// Total = 26 + 9 = 35, even = 35/26 = 1, numServersOverEven = 9
// First 9 servers (indices 0-8) have goal=2, rest have goal=1
// First server has 10 tablets, goal=2, needToUnload = 8
// Remaining 25 servers each have 1 tablet, goal=1 => needToLoad = 1 - 1 - 0 = 0 for 17 servers
// For servers at end indices with goal=2: needToLoad = 2 - 1 - 0 = 1 for 8 servers
// Total migrations = 8 (one to each of the 8 servers that need 1 extra)
ArrayList<TabletMigration> migrations = new ArrayList<>();
boolean more = balancer.getMigrations(current, migrations);
// Verify total tablets moved = 8, not 9
assertEquals(8, migrations.size());
```

Incorrect example:
```java
ArrayList<TabletMigration> migrations = new ArrayList<>();
boolean more = balancer.getMigrations(current, migrations);
// WRONG: blindly trusting result.size() without computing expected value
// This passes with the buggy code that moves 9 instead of 8
assertEquals(8, migrations.size()); // Correct only if bug is fixed
```