---
title: Sendable and Data Race Safety in Swift
date: 2026-09-15 14:03
description: Explore Swift's Sendable protocol to ensure data race safety in concurrent code, understand its implications for value and reference types, and avoid common pitfalls.
tags: Swift, Concurrency, iOS
---

# Sendable and Data Race Safety in Swift

Concurrency has become an indispensable part of modern application development, especially in Swift and on Apple platforms. With the introduction of Swift's new concurrency model (`async`/`await`, `Task`, `Actor`), writing concurrent code is more accessible than ever. However, with great power comes great responsibility – specifically, the responsibility to prevent data races.

Data races are one of the most insidious bugs in concurrent programming. They occur when multiple threads or tasks access the same mutable shared state without proper synchronization, and at least one of those accesses is a write. The unpredictable nature of these bugs can lead to crashes, corrupted data, or subtle, hard-to-diagnose issues.

Swift's concurrency model introduces the `Sendable` protocol as a key mechanism to help us write data-race-safe code. In this article, we'll dive deep into what `Sendable` means, how to use it effectively, and how it empowers the Swift compiler to help you catch concurrency bugs *at compile time*.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Diagram showing a data race scenario">
  <title>Data Race Scenario</title>

  <!-- Shared Resource -->
  <rect x="250" y="70" width="100" height="40" rx="5" fill="#F04B3E" stroke="#A03020" stroke-width="2"/>
  <text x="300" y="95" font-family="Arial" font-size="16" fill="white" text-anchor="middle">Shared Data</text>

  <!-- Task 1 -->
  <rect x="50" y="50" width="120" height="60" rx="5" fill="#1565c0" stroke="#0A4080" stroke-width="2"/>
  <text x="110" y="75" font-family="Arial" font-size="16" fill="white" text-anchor="middle">Task A</text>
  <text x="110" y="95" font-family="Arial" font-size="14" fill="white" text-anchor="middle">(Read & Write)</text>

  <!-- Task 2 -->
  <rect x="430" y="50" width="120" height="60" rx="5" fill="#1565c0" stroke="#0A4080" stroke-width="2"/>
  <text x="490" y="75" font-family="Arial" font-size="16" fill="white" text-anchor="middle">Task B</text>
  <text x="490" y="95" font-family="Arial" font-size="14" fill="white" text-anchor="middle">(Read & Write)</text>

  <!-- Arrows -->
  <path d="M170 80 H240" stroke="#F04B3E" stroke-width="3" marker-end="url(#arrowhead)" />
  <path d="M360 80 H430" stroke="#F04B3E" stroke-width="3" marker-end="url(#arrowhead)" />

  <!-- Overlapping access -->
  <rect x="190" y="150" width="220" height="40" rx="5" fill="#F04B3E" stroke="#A03020" stroke-width="2"/>
  <text x="300" y="175" font-family="Arial" font-size="16" fill="white" text-anchor="middle">Unsynchronized Concurrent Access = Data Race!</text>

  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#F04B3E" />
    </marker>
  </defs>
</svg>
</div>

## The Problem: Unsynchronized Shared Mutable State

Before `Sendable`, ensuring data safety across concurrent operations often involved manual synchronization mechanisms like locks, semaphores, or dispatch queues. While effective, these methods are prone to deadlocks, priority inversions, and can be difficult to reason about, especially in complex systems.

Consider a simple `BankAccount` class that allows deposits:

```swift
class BankAccount {
    var balance: Int

    init(initialBalance: Int) {
        self.balance = initialBalance
    }

    func deposit(amount: Int) {
        // Simulate some work
        Thread.sleep(forTimeInterval: 0.01)
        balance += amount
    }

    func getBalance() -> Int {
        return balance
    }
}
```

If we try to deposit money concurrently using multiple tasks, we might encounter a data race:

```swift
func simulateDeposits() async {
    let account = BankAccount(initialBalance: 0)
    let depositAmount = 100

    await withTaskGroup(of: Void.self) { group in
        for _ in 1...100 {
            group.addTask {
                account.deposit(amount: depositAmount) // Potential data race here!
            }
        }
    }

    print("Final balance: \(account.getBalance())")
    // Expected: 100 * 100 = 10000
    // Actual: Could be anything less than 10000 due to data races
}

// Call from an async context, e.g., a button action or main Task
// Task { await simulateDeposits() }
```

When you run `simulateDeposits()`, you'll likely see a `Final balance` that is less than the expected `10000`. This happens because `balance += amount` is not an atomic operation. It involves reading `balance`, adding `amount`, and then writing the new `balance`. If two tasks read the `balance` simultaneously, both might calculate a new balance based on the *old* value, leading to one of the updates being lost.

## Introducing `Sendable`

The `Sendable` protocol is a marker protocol. It doesn't define any methods or properties. Its sole purpose is to declare that a type's values can be safely sent across concurrency domains (e.g., from one `Task` to another, or from outside an `Actor` to inside it, or between different `Actor` instances). The Swift compiler uses this information to enforce data race safety.

When a type conforms to `Sendable`, the compiler guarantees that:
1.  **Value Types (structs, enums)**: If all their stored properties (or associated values for enums) are `Sendable`, they are implicitly `Sendable`. This is generally true for most common Swift types like `Int`, `String`, `Array`, `Dictionary`, etc.
2.  **Reference Types (classes, actors)**:
    *   They must be immutable (all stored properties are `let` and themselves `Sendable`).
    *   They must protect all mutable state with internal synchronization (e.g., using a `private let` `Actor` or `NSLock`). This is less common for direct `Sendable` conformance and more aligned with the `Actor` model itself.
    *   They are actors (actors are implicitly `Sendable`).
3.  **Functions and Closures**: Can be marked `@Sendable` if they don't capture mutable state that isn't `Sendable`, or if they capture immutable `Sendable` state.

If you attempt to pass a non-`Sendable` type across a concurrency boundary, the Swift compiler will issue a warning or an error, helping you catch potential data races at compile time rather than runtime.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Diagram showing Sendable types crossing concurrency boundaries safely">
  <title>Sendable Types Across Concurrency Boundaries</title>

  <!-- Concurrency Boundary 1 (e.g., Task) -->
  <rect x="50" y="30" width="200" height="80" rx="10" fill="#1565c0" stroke="#0A4080" stroke-width="2"/>
  <text x="150" y="75" font-family="Arial" font-size="18" fill="white" text-anchor="middle">Task A</text>

  <!-- Concurrency Boundary 2 (e.g., Actor) -->
  <rect x="350" y="30" width="200" height="80" rx="10" fill="#2A8367" stroke="#1C5C48" stroke-width="2"/>
  <text x="450" y="75" font-family="Arial" font-size="18" fill="white" text-anchor="middle">Actor B</text>

  <!-- Sendable Data -->
  <rect x="240" y="140" width="120" height="40" rx="5" fill="#2A8367" stroke="#1C5C48" stroke-width="2"/>
  <text x="300" y="165" font-family="Arial" font-size="16" fill="white" text-anchor="middle">Sendable Data</text>

  <!-- Arrows for Sendable data flow -->
  <path d="M150 110 V140 M150 110 C150 125, 200 135, 240 150" stroke="#2A8367" stroke-width="3" marker-end="url(#arrowhead-green)" fill="none"/>
  <path d="M450 110 V140 M450 110 C450 125, 400 135, 360 150" stroke="#2A8367" stroke-width="3" marker-end="url(#arrowhead-green)" fill="none"/>

  <path d="M250 80 H340" stroke="#2A8367" stroke-width="3" marker-end="url(#arrowhead-green)" />

  <!-- Labels for arrows -->
  <text x="295" y="65" font-family="Arial" font-size="14" fill="#2A8367" text-anchor="middle">Safe Transfer</text>
  <text x="210" y="125" font-family="Arial" font-size="12" fill="#2A8367" text-anchor="middle" transform="rotate(-30 210 125)">Safe Transfer</text>
  <text x="390" y="125" font-family="Arial" font-size="12" fill="#2A8367" text-anchor="middle" transform="rotate(30 390 125)">Safe Transfer</text>


  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowhead-green" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#2A8367" />
    </marker>
  </defs>
</svg>
</div>

## Conforming to `Sendable`

Let's look at how different types conform to `Sendable`.

### Value Types (Structs, Enums)

Most value types are `Sendable` by default, provided their constituent parts are also `Sendable`. This is a huge win for Swift's value semantics.

```swift
// This struct is implicitly Sendable because Int and String are Sendable.
struct UserProfile: Sendable {
    let id: UUID
    let name: String
    var email: String // Even if mutable, it's copied when passed, so safe.
}

// This enum is implicitly Sendable because String and Int are Sendable.
enum NetworkStatus: Sendable {
    case connected(server: String)
    case disconnected(code: Int)
    case unknown
}

func processUserProfile(_ profile: UserProfile) async {
    // ... process profile ...
    print("Processing profile for \(profile.name)")
}

func updateStatus(_ status: NetworkStatus) async {
    // ... update UI based on status ...
    switch status {
    case .connected(let server):
        print("Connected to \(server)")
    case .disconnected(let code):
        print("Disconnected with code \(code)")
    case .unknown:
        print("Unknown network status")
    }
}

// These calls are safe because UserProfile and NetworkStatus are Sendable.
Task {
    let user = UserProfile(id: UUID(), name: "Alice", email: "alice@example.com")
    await processUserProfile(user)
}

Task {
    await updateStatus(.connected(server: "api.example.com"))
}
```

The key here is that when a `UserProfile` or `NetworkStatus` instance is passed to a new `Task` or `Actor`, it's copied. Each concurrency domain gets its own independent copy, eliminating the possibility of a data race on that instance's internal state.

### Reference Types (Classes)

Reference types are where `Sendable` becomes crucial and often requires more thought. By default, classes are *not* `Sendable` unless explicitly marked and adhering to specific rules.

Consider our `BankAccount` class again:

```swift
class BankAccount { // Compiler warning: 'BankAccount' is not Sendable
    var balance: Int
    // ...
}
```

The compiler will warn you that `BankAccount` is not `Sendable` when you try to use it across concurrency boundaries, like passing it to `group.addTask`. This is because `BankAccount` has mutable state (`var balance`) that is not protected.

To make a class `Sendable`, it must typically be immutable:

```swift
// This class is Sendable because all its properties are 'let' and themselves Sendable.
final class ImmutableConfiguration: Sendable {
    let baseURL: String
    let timeout: TimeInterval
    let apiKey: String

    init(baseURL: String, timeout: TimeInterval, apiKey: String) {
        self.baseURL = baseURL
        self.timeout = timeout
        self.apiKey = apiKey
    }
}

func fetchConfig() async -> ImmutableConfiguration {
    // Simulate fetching
    await Task.sleep(nanoseconds: 1_000_000_000)
    return ImmutableConfiguration(baseURL: "https://api.example.com", timeout: 30.0, apiKey: "secret")
}

// This is safe because ImmutableConfiguration is Sendable.
Task {
    let config = await fetchConfig()
    await Task.detached {
        // Can safely use 'config' in a new task because it's immutable and Sendable.
        print("Using API Key: \(config.apiKey)")
    }.value
}
```

If a class needs mutable state and concurrent access, it should typically be an `actor`. Actors inherently provide isolation for their mutable state, making them `Sendable` by default.

```swift
actor SafeBankAccount: Sendable { // Actors are implicitly Sendable
    var balance: Int

    init(initialBalance: Int) {
        self.balance = initialBalance
    }

    func deposit(amount: Int) {
        // This method is isolated to the actor, so 'balance' access is safe.
        Thread.sleep(forTimeInterval: 0.01) // Simulate work
        balance += amount
    }

    func getBalance() -> Int {
        return balance
    }
}

func simulateSafeDeposits() async {
    let account = SafeBankAccount(initialBalance: 0)
    let depositAmount = 100

    await withTaskGroup(of: Void.self) { group in
        for _ in 1...100 {
            group.addTask {
                await account.deposit(amount: depositAmount) // Safe due to actor isolation
            }
        }
    }

    print("Final safe balance: \(await account.getBalance())") // Should be 10000
}

// Task { await simulateSafeDeposits() }
```

### `@Sendable` Closures

Closures can also capture values from their surrounding scope. If a closure is to be passed across a concurrency boundary (e.g., as an argument to `Task` or an `Actor` method), it must be `@Sendable`.

A closure is `@Sendable` if all values it captures are `Sendable`. If it captures a non-`Sendable` mutable value, the compiler will flag it.

```swift
var counter = 0 // A non-Sendable mutable value

func performUnsafeTask() {
    // Compiler error/warning: Capture of 'counter' by a non-Sendable closure
    // in a Sendable context.
    Task {
        counter += 1
        print("Counter: \(counter)")
    }
}

// To make it safe, ensure captured values are Sendable or immutable.
func performSafeTask() {
    let immutableCounter = 0 // Immutable, thus Sendable
    Task { // This closure is implicitly @Sendable
        let _ = immutableCounter + 1 // No mutation of captured state
        print("Immutable counter: \(immutableCounter)")
    }
}

// If you need to mutate state, an actor is the way to go:
actor CounterActor {
    var value = 0
    func increment() { value += 1 }
    func getValue() -> Int { value }
}

func performActorSafeTask() async {
    let counterActor = CounterActor()

    await withTaskGroup(of: Void.self) { group in
        for _ in 1...10 {
            group.addTask {
                await counterActor.increment()
            }
        }
    }
    print("Actor counter: \(await counterActor.getValue())")
}

// Task { await performActorSafeTask() }
```

### `@unchecked Sendable` (Use with Extreme Caution!)

Sometimes, you might encounter a type that Swift cannot automatically prove is `Sendable`, but you *know* it's thread-safe due to underlying implementation details (e.g., it wraps a C++ thread-safe object, or it's implicitly protected by the operating system). In such rare cases, you can explicitly declare conformance using `@unchecked Sendable`.

```swift
// WARNING: This is almost always a bad idea unless you are absolutely certain
// of the underlying thread-safety and have no other way to model it.
final class UnsafeWrapper: @unchecked Sendable {
    // This class might wrap a C++ object that is thread-safe,
    // but Swift doesn't know about it.
    private var internalData: [Int] // Mutable state

    init(data: [Int]) {
        self.internalData = data
    }

    func append(_ value: Int) {
        // Imagine this is protected by a sophisticated C++ lock
        // that Swift can't see or verify.
        internalData.append(value)
    }

    func getData() -> [Int] {
        return internalData
    }
}

func useUncheckedSendable() async {
    let wrapper = UnsafeWrapper(data: [])

    await withTaskGroup(of: Void.self) { group in
        for i in 1...10 {
            group.addTask {
                // The compiler now allows this, but the safety is YOUR responsibility.
                wrapper.append(i)
            }
        }
    }
    print("Unchecked wrapper data: \(wrapper.getData())") // Still a data race if not truly safe!
}
// Task { await useUncheckedSendable() }
```

Using `@unchecked Sendable` disables the compiler's safety checks for that type. If your assumptions about its thread-safety are wrong, you've effectively reintroduced the very data races `Sendable` is designed to prevent. Only use this when absolutely necessary and you have a robust external guarantee of thread safety.

## Best Practices and Pitfalls

1.  **Prefer Value Types**: Structs and enums are inherently safer for concurrency because they are copied when passed around. This eliminates shared mutable state for that particular instance.
2.  **Make Classes Immutable**: If you need a reference type (e.g., for identity or performance reasons), make it `final` and ensure all its stored properties are `let` and `Sendable`. This makes the class itself `Sendable`.
3.  **Use Actors for Mutable Shared State**: If you have mutable state that needs to be shared and modified concurrently, an `actor` is almost always the correct solution. Actors provide isolation, ensuring that only one task can access their mutable state at a time.
4.  **Understand `nonisolated`**: When an `Actor` method is marked `nonisolated`, it means it can be called from outside the actor without awaiting. This is only safe if the method accesses only `Sendable` properties or `let` properties, or calls other `nonisolated` methods. `nonisolated` properties of an actor must be `Sendable`.
5.  **Avoid `@unchecked Sendable`**: This is your emergency escape hatch, not a routine tool. If you find yourself reaching for it, reconsider your design. Can you use an `actor`? Can you make the type immutable? Can you refactor to use value types?

## `Sendable` vs. Actors

It's important to understand the distinction:
*   **`Sendable`**: Guarantees that a *value* (an instance of a type) can be safely copied or moved across concurrency domains. It's about the *data itself*.
*   **`Actor`**: Guarantees that *mutable state* within the actor is accessed in a mutually exclusive way. It's about the *synchronization mechanism* for managing shared mutable state.

A `Sendable` type can be passed into an actor or out of an actor. An actor itself is `Sendable` because its internal state is protected.

```
┌────────────────────┐          ┌────────────────────┐
│      Sendable      │          │      Actor         │
│ (Immutable Data)   │          │ (Mutable State)    │
├────────────────────┤          ├────────────────────┤
│ - Value types      │          │ - Reference type   │
│   (structs, enums) │          │ - Provides isolation│
│ - Immutable classes│          │ - Methods are async│
│ - Copied on transfer│         │ - State accessed via│
│ - Data race safe by │         │   awaiting methods │
│   design           │          │ - Data race safe by │
│                    │          │   synchronization  │
└────────────────────┘          └────────────────────┘
```

## Summary

The `Sendable` protocol is a cornerstone of Swift's modern concurrency model, enabling the compiler to enforce data race safety. By understanding how value types, reference types, and closures conform to `Sendable`, you can write more robust, predictable, and safer concurrent code. Prioritize value types, make reference types immutable where possible, and leverage actors for managing mutable shared state. Embrace the compiler's guidance, and you'll spend less time debugging elusive concurrency bugs.

Happy Swifting!
