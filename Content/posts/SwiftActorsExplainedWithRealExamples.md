---
title: Swift Actors Explained with Real Examples
date: 2026-07-04 10:50
description: Dive into Swift Actors, a powerful concurrency feature that eliminates data races and simplifies shared mutable state management in your iOS apps.
tags: Swift, Concurrency, iOS
---

# Swift Actors Explained with Real Examples

Concurrency in software development has always been a double-edged sword. It allows our applications to perform multiple tasks simultaneously, leading to more responsive and efficient user experiences. However, it also introduces complex challenges, particularly when multiple concurrent tasks try to access and modify the same shared piece of data. This scenario often leads to insidious bugs known as "data races."

Traditionally, developers have relied on tools like locks, semaphores, and dispatch queues to protect shared mutable state. While effective, these mechanisms can be notoriously difficult to use correctly, often leading to deadlocks, priority inversions, or simply confusing and error-prone code.

Swift's structured concurrency, introduced in Swift 5.5, brought us `async/await` for managing asynchronous operations more cleanly. But `async/await` alone doesn't solve the problem of shared mutable state. That's where **Swift Actors** come into play. Actors provide a safe and natural way to manage shared mutable state, eliminating data races by design and making concurrent programming significantly safer and easier.

In this article, we'll explore what Swift Actors are, how they work, and how you can leverage them to write robust, concurrent applications for iOS, macOS, and beyond.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Diagram illustrating a data race scenario without Swift Actors.">
  <title>The Problem: Data Race Without Actors</title>

  <!-- Shared Resource Box -->
  <rect x="220" y="10" width="160" height="60" rx="10" fill="#F04B3E" stroke="#c0392b" stroke-width="2"/>
  <text x="300" y="45" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">Shared Counter: 0</text>

  <!-- Task A Box -->
  <rect x="50" y="140" width="150" height="60" rx="10" fill="#1565c0" stroke="#0e519e" stroke-width="2"/>
  <text x="125" y="175" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">Task A (Increment)</text>

  <!-- Task B Box -->
  <rect x="400" y="140" width="150" height="60" rx="10" fill="#1565c0" stroke="#0e519e" stroke-width="2"/>
  <text x="475" y="175" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">Task B (Increment)</text>

  <!-- Arrow from Task A to Shared Resource -->
  <line x1="125" y1="140" x2="270" y2="70" stroke="#1565c0" stroke-width="3" marker-end="url(#arrowhead)"/>
  <text x="180" y="105" font-family="Arial, sans-serif" font-size="14" fill="#1565c0" text-anchor="middle">Reads 0, Writes 1</text>

  <!-- Arrow from Task B to Shared Resource -->
  <line x1="475" y1="140" x2="330" y2="70" stroke="#1565c0" stroke-width="3" marker-end="url(#arrowhead)"/>
  <text x="420" y="105" font-family="Arial, sans-serif" font-size="14" fill="#1565c0" text-anchor="middle">Reads 0, Writes 1</text>

  <!-- Result Box -->
  <rect x="220" y="140" width="160" height="60" rx="10" fill="#F04B3E" stroke="#c0392b" stroke-width="2"/>
  <text x="300" y="175" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">Final Counter: 1 (Expected 2)</text>

  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#1565c0" />
    </marker>
  </defs>
</svg>
</div>

## What are Swift Actors?

At its core, an **actor** is a reference type, similar to a class, that protects its own mutable state from concurrent access. The key principle behind actors is **actor isolation**: an actor's mutable properties and methods can only be accessed by code running *within* the actor itself. Any access from outside the actor's "isolation domain" must be done asynchronously and is automatically serialized.

Think of an actor as having its own private mailbox and a single worker. When you send a message (call a method) to an actor, that message goes into its mailbox. The worker processes messages one by one, in the order they were received. While the worker is busy with one message, all other incoming messages wait in the mailbox. This serial execution within the actor ensures that its internal state is never accessed by multiple tasks simultaneously, thus preventing data races.

Declaring an actor is simple: you just use the `actor` keyword instead of `class`.

```swift
actor BankAccount {
    private var balance: Double

    init(initialBalance: Double) {
        self.balance = initialBalance
    }

    func deposit(amount: Double) {
        balance += amount
        print("Deposited \(amount). New balance: \(balance)")
    }

    func withdraw(amount: Double) {
        if balance >= amount {
            balance -= amount
            print("Withdrew \(amount). New balance: \(balance)")
        } else {
            print("Insufficient funds to withdraw \(amount). Current balance: \(balance)")
        }
    }

    func getBalance() -> Double {
        return balance
    }
}
```

## How Actors Prevent Data Races

When you try to call a method or access a mutable property of an actor from outside its isolation domain, the Swift compiler enforces a crucial rule: you must use the `await` keyword. This `await` keyword signifies that the call is potentially asynchronous and might involve a context switch.

When you `await` an actor's method:
1.  Your current task *suspends* its execution.
2.  The actor receives the message and adds it to its internal queue.
3.  When the actor's "worker" is free, it picks up the message and executes the method.
4.  Once the method completes, its result (if any) is returned, and your suspended task can resume.

Because the actor processes its messages serially, any internal state changes are guaranteed to happen one at a time. This is the magic that eliminates data races.

Let's illustrate with a common scenario: managing a shared counter.

First, consider a non-actor class, which is prone to data races:

```swift
class UnsafeCounter {
    var value: Int = 0

    func increment() {
        // Simulate some work or contention
        let currentValue = value
        // Imagine other tasks might read/write 'value' here
        Thread.sleep(forTimeInterval: 0.0001) // Simulate a tiny delay
        value = currentValue + 1
    }

    func getValue() -> Int {
        return value
    }
}

func demonstrateDataRace() async {
    let counter = UnsafeCounter()
    let numTasks = 1000
    let incrementsPerTask = 100

    await withTaskGroup(of: Void.self) { group in
        for _ in 0..<numTasks {
            group.addTask {
                for _ in 0..<incrementsPerTask {
                    counter.increment()
                }
            }
        }
    }

    // This will almost certainly print a value less than 100,000
    print("UnsafeCounter final value: \(counter.getValue())")
}

// Call it:
// Task { await demonstrateDataRace() }
```

Now, let's use an actor to make it safe:

```swift
actor SafeCounter {
    private var value: Int = 0

    func increment() {
        // Simulate some work or contention
        let currentValue = value
        // No other task can access 'value' while this actor method is running
        Thread.sleep(forTimeInterval: 0.0001) // Simulate a tiny delay
        value = currentValue + 1
    }

    func getValue() -> Int {
        return value
    }
}

func demonstrateSafeCounter() async {
    let counter = SafeCounter()
    let numTasks = 1000
    let incrementsPerTask = 100

    await withTaskGroup(of: Void.self) { group in
        for _ in 0..<numTasks {
            group.addTask {
                for _ in 0..<incrementsPerTask {
                    await counter.increment() // Await required for actor calls
                }
            }
        }
    }

    // This will correctly print 100,000
    print("SafeCounter final value: \(await counter.getValue())") // Await required
}

// Call it:
// Task { await demonstrateSafeCounter() }
```

The difference is stark. The `await` keyword ensures that access to `SafeCounter`'s `increment()` method is serialized, preventing the concurrent updates that lead to data races.

```
┌─────────────────┐
│     Actor       │
│  (Mailbox/Queue)│
├─────────────────┤
│ Message A (inc) │
│ Message B (inc) │
│ Message C (inc) │
└─────────────────┘
        │
        ▼
┌─────────────────┐
│ Actor Instance  │
│ (Serial Access) │
│  - Processes A  │
│  - Processes B  │
│  - Processes C  │
└─────────────────┘
        │
        ▼
┌─────────────────┐
│   Safe State    │
│  (No Data Race) │
└─────────────────┘
```

## Actor Reentrancy

A crucial concept to understand with actors is **reentrancy**. While an actor processes messages serially, it's not entirely "locked" during an `await` call *within* one of its methods. If an actor method encounters an `await` (e.g., calling another asynchronous function), the actor *suspends* its current execution, allowing other tasks waiting in its mailbox to enter and execute their methods. Once the awaited operation completes, the original method resumes.

This reentrancy is vital for performance, as it prevents actors from blocking the entire system while waiting for I/O or other asynchronous work. However, it means that the actor's state might have changed between the `await` point and the resumption point.

Consider this example:

```swift
actor DataProcessor {
    private var processingQueue: [String] = []
    private var isProcessing: Bool = false

    func processItem(_ item: String) async {
        if isProcessing {
            print("[\(item)] Actor is busy, adding to queue.")
            processingQueue.append(item)
            return
        }

        isProcessing = true
        print("[\(item)] Starting to process item.")

        // Simulate an external asynchronous operation
        await Task.sleep(nanoseconds: 2_000_000_000) // 2 second delay

        // After this await, another task could have entered and potentially changed state
        print("[\(item)] Finished processing item.")
        isProcessing = false // Resetting state might be affected by reentrancy

        // Now process items from the queue
        while let nextItem = processingQueue.first {
            processingQueue.removeFirst()
            await processItem(nextItem) // Recursive call, but actor is reentrant
        }
    }
}

func demonstrateReentrancy() async {
    let processor = DataProcessor()

    await withTaskGroup(of: Void.self) { group in
        group.addTask { await processor.processItem("Item A") }
        group.addTask { await processor.processItem("Item B") }
        group.addTask { await processor.processItem("Item C") }
    }
    print("All items attempted for processing.")
}

// Task { await demonstrateReentrancy() }
```
In this example, "Item A" starts processing and then `await`s. During this `await`, "Item B" and "Item C" can enter the actor. They see `isProcessing` is `true`, so they are added to the queue. When "Item A" resumes, it finishes and then processes items from its queue. This behavior might be exactly what you want, but it requires careful consideration of state changes across `await` points.

## The `MainActor`

A special type of actor provided by Swift is the `MainActor`. Its purpose is to synchronize all work onto the main thread, which is crucial for UI updates in iOS, macOS, watchOS, and tvOS apps. Any code that modifies UI elements *must* run on the main thread.

You can mark properties, methods, or even entire classes and structs with `@MainActor` to ensure that all access to them happens on the main thread.

```swift
@MainActor
class ViewModel: ObservableObject {
    @Published var statusMessage: String = "Ready"
    @Published var isLoading: Bool = false

    func updateUI(message: String, loading: Bool) {
        // These updates are guaranteed to be on the main thread
        self.statusMessage = message
        self.isLoading = loading
        print("UI updated on thread: \(Thread.current)")
    }

    func fetchData() async {
        // Perform background work
        print("Fetching data on thread: \(Thread.current)")
        await Task.sleep(nanoseconds: 1_000_000_000) // Simulate network request

        // Switch to MainActor to update UI
        await updateUI(message: "Data loaded!", loading: false)
    }
}

// Usage from a background task:
func runMainActorExample() {
    let viewModel = ViewModel() // ViewModel is @MainActor, so this init is on main thread

    Task {
        // This task might start on a background thread
        print("Initiating fetch from background thread: \(Thread.current)")
        await viewModel.updateUI(message: "Loading...", loading: true) // Awaits MainActor
        await viewModel.fetchData() // fetchData itself contains an await for MainActor
    }
}

// Call it:
// runMainActorExample()
```
Notice how `await viewModel.updateUI(...)` automatically hops to the main actor. The `fetchData()` method, though marked `@MainActor`, can still perform background work by `await`ing non-main-actor tasks. When it needs to update its `@Published` properties, it transparently switches back to the main actor's execution context.

## `nonisolated` and `nonisolated(unsafe)`

While actor isolation is powerful, sometimes you have properties or methods that don't access the actor's mutable state and therefore don't need to be serialized. For these, you can use the `nonisolated` keyword.

```swift
actor UserCache {
    private var users: [String: String] = [:] // Isolated state

    // A nonisolated property can be accessed without 'await'
    // It must not access any isolated state.
    nonisolated let cacheName: String = "UserCache"

    init(name: String) {
        self.cacheName = name // For nonisolated let, init must be careful
        // Self.cacheName is actually initialized outside actor isolation
        // A better approach for `let` is to just declare it directly.
        // For `var` it would be nonisolated(unsafe) or computed.
    }

    init() { // Default init
        self.cacheName = "DefaultUserCache"
    }


    func addUser(_ id: String, name: String) {
        users[id] = name
    }

    func getUser(id: String) -> String? {
        return users[id]
    }

    // A nonisolated method can be called without 'await'
    // It must not access any isolated mutable state.
    nonisolated func describeCache() -> String {
        return "This is the \(cacheName) for storing user data."
    }
}

func demonstrateNonisolated() async {
    let cache = UserCache()
    await cache.addUser("1", name: "Alice")

    // No await needed for nonisolated properties/methods
    print(cache.cacheName)
    print(cache.describeCache())

    // Await still needed for isolated methods
    if let user = await cache.getUser(id: "1") {
        print("Found user: \(user)")
    }
}

// Task { await demonstrateNonisolated() }
```
`nonisolated` is useful for constants (`let`) or computed properties that don't depend on isolated mutable state, or for methods that only operate on parameters or other `nonisolated` properties.

There's also `nonisolated(unsafe)`. This is an extremely powerful and dangerous escape hatch. It tells the compiler to *trust you* that you are handling concurrency safely for a particular property or method, even if it accesses isolated state. You should only use `nonisolated(unsafe)` when you have a very clear and proven external synchronization mechanism (like a `NSRecursiveLock`) that you are managing manually. **Use it with extreme caution and only if you fully understand the implications.** In most cases, if you need to access isolated state, you should `await` the actor.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 700 250" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Comparison of traditional locking vs. Swift Actor isolation for concurrent access.">
  <title>Concurrency Approaches: Traditional Locking vs. Swift Actors</title>

  <!-- Traditional Locking Section -->
  <rect x="20" y="10" width="320" height="230" rx="10" fill="#f8f8f8" stroke="#ccc" stroke-width="2"/>
  <text x="180" y="35" font-family="Arial, sans-serif" font-size="18" fill="#333" text-anchor="middle" font-weight="bold">Traditional Locking (e.g., Mutex)</text>

  <!-- Shared Resource (Locking) -->
  <rect x="100" y="70" width="160" height="50" rx="8" fill="#eee" stroke="#666" stroke-width="1"/>
  <text x="180" y="100" font-family="Arial, sans-serif" font-size="14" fill="#333" text-anchor="middle">Shared Resource</text>

  <!-- Lock Box -->
  <rect x="130" y="130" width="100" height="40" rx="5" fill="#2A8367" stroke="#1f654f" stroke-width="1"/>
  <text x="180" y="155" font-family="Arial, sans-serif" font-size="14" fill="white" text-anchor="middle">Lock</text>

  <!-- Task 1 (Locking) -->
  <rect x="30" y="180" width="140" height="50" rx="8" fill="#1565c0" stroke="#0e519e" stroke-width="1"/>
  <text x="100" y="210" font-family="Arial, sans-serif" font-size="14" fill="white" text-anchor="middle">Task 1</text>
  <path d="M100 180 L100 160 L130 160" fill="none" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowheadBlue)"/>
  <path d="M100 180 L100 120 L130 120" fill="none" stroke="#1565c0" stroke-width="2"/>


  <!-- Task 2 (Locking) -->
  <rect x="190" y="180" width="140" height="50" rx="8" fill="#1565c0" stroke="#0e519e" stroke-width="1"/>
  <text x="260" y="210" font-family="Arial, sans-serif" font-size="14" fill="white" text-anchor="middle">Task 2</text>
  <path d="M260 180 L260 160 L230 160" fill="none" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowheadBlue)"/>
  <path d="M260 180 L260 120 L230 120" fill="none" stroke="#1565c0" stroke-width="2"/>
  <text x="180" y="170" font-family="Arial, sans-serif" font-size="12" fill="#F04B3E" text-anchor="middle">Manual Management, Prone to Deadlocks</text>


  <!-- Swift Actor Section -->
  <rect x="360" y="10" width="320" height="230" rx="10" fill="#f8f8f8" stroke="#ccc" stroke-width="2"/>
  <text x="520" y="35" font-family="Arial, sans-serif" font-size="18" fill="#333" text-anchor="middle" font-weight="bold">Swift Actor Isolation</text>

  <!-- Actor Box -->
  <rect x="440" y="70" width="160" height="80" rx="8" fill="#2A8367" stroke="#1f654f" stroke-width="2"/>
  <text x="520" y="100" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">MyActor</text>
  <text x="520" y="125" font-family="Arial, sans-serif" font-size="14" fill="white" text-anchor="middle">(Serial Execution)</text>

  <!-- Task 3 (Actor) -->
  <rect x="370" y="180" width="140" height="50" rx="8" fill="#1565c0" stroke="#0e519e" stroke-width="1"/>
  <text x="440" y="210" font-family="Arial, sans-serif" font-size="14" fill="white" text-anchor="middle">Task 3</text>
  <path d="M440 180 L440 150 L470 150" fill="none" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowheadBlue)"/>
  <text x="440" y="170" font-family="Arial, sans-serif" font-size="12" fill="#1565c0" text-anchor="middle">await call</text>


  <!-- Task 4 (Actor) -->
  <rect x="530" y="180" width="140" height="50" rx="8" fill="#1565c0" stroke="#0e519e" stroke-width="1"/>
  <text x="600" y="210" font-family="Arial, sans-serif" font-size="14" fill="white" text-anchor="middle">Task 4</text>
  <path d="M600 180 L600 150 L570 150" fill="none" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowheadBlue)"/>
  <text x="600" y="170" font-family="Arial, sans-serif" font-size="12" fill="#1565c0" text-anchor="middle">await call</text>
  <text x="520" y="160" font-family="Arial, sans-serif" font-size="12" fill="#2A8367" text-anchor="middle">Compiler Enforced Safety</text>

  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowheadBlue" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#1565c0" />
    </marker>
  </defs>
</svg>
</div>

## Summary

Swift Actors are a game-changer for concurrent programming. By providing a clear, compiler-enforced mechanism for actor isolation, they effectively eliminate data races and simplify the management of shared mutable state. Understanding how to use actors, including concepts like reentrancy and the `MainActor`, is essential for building modern, robust, and performant Swift applications. Embrace actors, and say goodbye to many of the headaches traditionally associated with concurrency!

Happy Swifting!
