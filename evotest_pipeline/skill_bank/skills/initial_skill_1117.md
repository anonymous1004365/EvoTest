---
name: weak-listener-deduplication-by-identity
description: When the same WeakMojoExecutionListener instance is provided under multiple
  Key types in a scoping context, getProvidedListeners() must deduplicate by identity
  (not equality) using IdentityHashMap to ensure each listener's callbacks are invoked
  exactly once. This skill teaches how to test that listener deduplication works correctly
  when the same instance is registered under different keys.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
- WEAK_LISTENER_DEDUPLICATION
test_pattern: STATE_TEST
---

# weak-listener-deduplication-by-identity

## Instructions

# Weak Listener Deduplication by Identity

## Instructions

WHEN the TG encounters code that provides the same `WeakMojoExecutionListener` instance under multiple `Key<?>` types via `scope.scope(Key.get(...), provider)`, and the scope internally collects/deduplicates listeners by iterating over `provided.values()` using `IdentityHashMap`:

- THEN the TG MUST write a test where the **same object instance** is provided under at least two different `Key` types (e.g., `Key.get(Object.class)` and `Key.get(WeakMojoExecutionListener.class)`)
- THEN the TG MUST verify that after providing the same instance under multiple keys, calling `beforeMojoExecution()`, `afterMojoExecutionSuccess()`, and `afterExecutionFailure()` invokes the callbacks **exactly once** per listener (not once per key)
- THEN the TG MUST use `AtomicInteger` counters inside the listener implementation to count how many times each callback method is invoked
- THEN the TG MUST call `scope.enter()` before setting up the scope bindings, and `scope.exit()` after verifying the results
- THEN the TG MUST assert that each `AtomicInteger` equals `1` (not `2` or more) after invoking the lifecycle events, confirming identity-based deduplication works

Common pitfalls:
- **Providing different instances under each key** — this defeats the purpose of deduplication testing. The whole point is the same instance is reused.
- **Using only one key** — the bug only manifests when the same listener is bound under multiple keys. A single-key test will always report correct counts and won't detect the deduplication failure.
- **Forgetting to enter the scope** — `scope.enter()` must be called before `scope.scope()` and lifecycle methods, otherwise an `IllegalStateException` or `OutOfScopeException` will be thrown.
- **Testing equality instead of identity** — the deduplication uses `IdentityHashMap` (identity-based), so verify it's the exact same Java object, not just an equal one.

### Correct example (catches the bug):

```java
public void testMultiKeyInstance() throws Exception
{
    MojoExecutionScope scope = new MojoExecutionScope();
    scope.enter();

    final AtomicInteger beforeExecution = new AtomicInteger();
    final AtomicInteger afterExecutionSuccess = new AtomicInteger();
    final AtomicInteger afterExecutionFailure = new AtomicInteger();
    final WeakMojoExecutionListener instance = new WeakMojoExecutionListener()
    {
        @Override
        public void beforeMojoExecution( MojoExecutionEvent event ) { beforeExecution.incrementAndGet(); }

        @Override
        public void afterMojoExecutionSuccess( MojoExecutionEvent event ) { afterExecutionSuccess.incrementAndGet(); }

        @Override
        public void afterExecutionFailure( MojoExecutionEvent event ) { afterExecutionFailure.incrementAndGet(); }
    };

    // Bind the SAME instance under TWO different keys
    assertSame( instance, scope.scope( Key.get( Object.class ), new Provider<Object>()
    {
        @Override
        public Object get() { return instance; }
    } ).get() );
    assertSame( instance, scope.scope( Key.get( WeakMojoExecutionListener.class ), new Provider<WeakMojoExecutionListener>()
    {
        @Override
        public WeakMojoExecutionListener get() { return instance; }
    } ).get() );

    final MojoExecutionEvent event = new MojoExecutionEvent( null, null, null, null );
    scope.beforeMojoExecution( event );
    scope.afterMojoExecutionSuccess( event );
    scope.afterExecutionFailure( event );

    assertEquals( 1, beforeExecution.get() );       // fails if deduplication is broken
    assertEquals( 1, afterExecutionSuccess.get() );  // fails if deduplication is broken
    assertEquals( 1, afterExecutionFailure.get() );  // fails if deduplication is broken

    scope.exit();
}
```

### Incorrect example (does NOT catch the bug):

```java
public void testSingleKeyInstance() throws Exception
{
    MojoExecutionScope scope = new MojoExecutionScope();
    scope.enter();

    final AtomicInteger count = new AtomicInteger();
    final WeakMojoExecutionListener listener = new WeakMojoExecutionListener()
    {
        @Override
        public void beforeMojoExecution( MojoExecutionEvent event ) { count.incrementAndGet(); }
        // ...
    };

    // Only bound under ONE key — will pass even with buggy deduplication
    assertSame( listener, scope.scope( Key.get( WeakMojoExecutionListener.class ), 
        Providers.of( listener ) ).get() );

    scope.beforeMojoExecution( new MojoExecutionEvent( null, null, null, null ) );
    assertEquals( 1, count.get() );  // always passes, even if deduplication code were removed entirely
    scope.exit();
}
```