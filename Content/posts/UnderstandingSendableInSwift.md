---
title: Understanding Sendable in Swift
date: 2026-10-19 16:03
description: Demystify Swift's Sendable protocol, its role in safe concurrency, and how to make your types safely shareable across tasks and actors.
tags: Swift, iOS, Programming
---

# Understanding Sendable in Swift

Swift's modern concurrency model, introduced with `async`/`await`, `Task`s, and `Actor`s, has revolutionized how we write concurrent code. It provides powerful tools to manage asynchronous operations with greater clarity and safety. However, concurrency always brings a fundamental challenge: how to safely share mutable state between different concurrent contexts without introducing data races.

This is where the `Sendable` protocol comes into play. `Sendable` is a cornerstone of Swift's structured concurrency, acting as a compile-time guarantee that a type can be safely passed across isolation domains (like between tasks or to/from actors). Without a proper understanding of `Sendable`, you might find yourself battling compiler warnings or, worse, elusive runtime bugs.

In this article, we'll demystify `Sendable`. We'll explore the problem it solves, how different types conform to it, and how to effectively use it to write robust, data-race-free concurrent Swift code.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Diagram showing two tasks accessing a shared mutable resource leading to a data race.">
  <title>The Problem: Unsafe Shared Mutable State</title>

  <!-- Shared Mutable State Box -->
  <rect x="250" y="70" width="100" height="80" rx="10" ry="10" fill="#F04B3E" stroke="#E03A2D" stroke-width="2"/>
  <text x="300" y="115" font-family="Arial" font-size="16" fill="white" text-anchor="middle">Mutable</text>
  <text x="300" y="135" font-family="Arial" font-size="16" fill="white" text-anchor="middle">Shared State</text>

  <!-- Task 1 -->
  <rect x="50" y="50" width="100" height="50" rx="10" ry="10" fill="#1565c0" stroke="#0F4C9B" stroke-width="2"/>
  <text x="100" y="80" font-family="Arial" font-size="16" fill="white" text-anchor="middle">Task A</text>

  <!-- Task 2 -->
  <rect x="50" y="120" width="100" height="50" rx="10" ry="10" fill="#1565c0" stroke="#0F4C9B" stroke-width="2"/>
  <text x="100" y="150" font-family="Arial" font-size="16" fill="white" text-anchor="middle">Task B</text>

  <!-- Arrow Task A to Shared State -->
  <line x1="150" y1="75" x2="250" y2="100" stroke="#F04B3E" stroke-width="3" marker-end="url(#arrowhead)"/>
  <text x="190" y="70" font-family="Arial" font-size="14" fill="#F04B3E">Write/Read</text>

  <!-- Arrow Task B to Shared State -->
  <line x1="150" y1="145" x2="250" y2="120" stroke="#F04B3E" stroke-width="3" marker-end="url(#arrowhead)"/>
  <text x="190" y="160" font-family="Arial" font-size="14" fill="#F04B3E">Write/Read</text>

  <!-- Data Race Text -->
  <text x="450" y="115" font-family="Arial" font-size="20" fill="#F04B3E" text-anchor="middle" font-weight="bold">Data Race!</text>
  <path d="M 400 110 L 350 110 L 375 90 Z" fill="#F04B3E"/>
  <path d="M 400 120 L 350 120 L 375 140 Z" fill="#F04B3E"/>

  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#F04B3E" />
    </marker>
  </defs>
</svg>
</div>

## The Problem: Unsafe Sharing and Data Races

Before diving into `Sendable`, let's understand the problem it aims to solve: data races. A data race occurs when multiple threads or concurrent tasks access the same mutable shared state, and at least one of those accesses is a write operation, without any proper synchronization mechanism.

Consider a simple counter that multiple tasks try to increment:

```swift
class UnsafeCounter {
    var value: Int = 0

    func increment() {
        value += 1
    }
}

let counter = UnsafeCounter()

func runUnsafeTasks() async {
    await withTaskGroup(of: Void.self) { group in
        for _ in 0..<1000 {
            group.addTask {
                // Warning: Non-Sendable type 'UnsafeCounter' in asynchronous call to function
                // that does not conform to 'Sendable' protocol
                counter.increment()
            }
        }
    }
    print("Final unsafe counter value: \(counter.value)") // Will likely be less than 1000
}

// To run this example, wrap it in a Task:
// Task { await runUnsafeTasks() }
```

If you run this code, you'll likely find that `counter.value` is less than 1000, and its exact value will vary between runs. This non-deterministic behavior is a hallmark of a data race. The `increment()` operation (`value += 1`) is not atomic; it involves reading `value`, adding 1, and then writing the new `value`. If two tasks perform this sequence concurrently, one task's write might overwrite another's, leading to lost updates.

Swift's concurrency model aims to prevent such issues at compile time. When you try to pass `counter` (an instance of `UnsafeCounter`) into `group.addTask { ... }`, the compiler issues a warning: "Non-Sendable type 'UnsafeCounter' in asynchronous call to function that does not conform to 'Sendable' protocol." This warning is your first line of defense, signaling a potential data race.

## Introducing the `Sendable` Protocol

`Sendable` is a marker protocol. It doesn't define any methods or properties; its sole purpose is to tell the Swift compiler that an instance of a type can be safely copied or moved across different concurrency domains (e.g., from one `Task` to another, or into/out of an `Actor`).

When the compiler sees a type conforming to `Sendable`, it gains a crucial guarantee: any instance of that type, or any reference to it, can be safely used in a concurrent context without introducing data races, *provided the type itself is correctly implemented*. This allows the compiler to enforce isolation rules at compile time, preventing a whole class of concurrency bugs before your code even runs.

The compiler performs a static analysis to determine if a type is `Sendable`. If a type is `Sendable`, it means one of the following is true:

1.  It is a value type (struct, enum) with `Sendable` members.
2.  It is an immutable reference type with `Sendable` members.
3.  It is an actor type.
4.  It uses internal synchronization to protect its mutable state.
5.  It is explicitly marked as `@unchecked Sendable` by the developer, taking full responsibility.

## What Makes a Type `Sendable`?

Let's break down how different Swift types achieve `Sendable` conformance.

### Value Types: Structs and Enums

Value types are generally the easiest to make `Sendable`. A `struct` or `enum` is automatically `Sendable` if all of its stored properties (for structs) or associated values (for enums) are themselves `Sendable`.

**Why?** Because value types are copied when passed across concurrency boundaries. Each task gets its own independent copy, eliminating the shared mutable state problem. Even if a `struct` contains a `class` instance, if that `class` instance is immutable (and `Sendable`), then the `struct` itself can be `Sendable`.

```swift
// Example 1: Sendable Struct
struct UserID: Sendable, Hashable {
    let id: String // String is Sendable
}

struct Message: Sendable {
    let sender: UserID // UserID is Sendable
    let content: String // String is Sendable
    let timestamp: Date // Date is Sendable
}

// Example 2: Sendable Enum
enum NetworkError: Error, Sendable {
    case invalidURL
    case serverError(code: Int) // Int is Sendable
    case customError(message: String, code: Int) // String, Int are Sendable
}
```

In both examples, the types are automatically inferred as `Sendable` because their components are also `Sendable` value types or immutable reference types.

### Reference Types: Classes

Classes are trickier. Since they are reference types, multiple tasks can hold references to the *same instance* of a class. For a class to be `Sendable`, it must guarantee that its state cannot be mutated concurrently by different tasks in an unsafe way.

A `class` can be `Sendable` if:

1.  **It's immutable**: All its stored properties are `let` constants, and their types are `Sendable`.
    ```swift
    final class ImmutableConfiguration: Sendable {
        let apiKey: String
        let environment: String

        init(apiKey: String, environment: String) {
            self.apiKey = apiKey
            self.environment = environment
        }
    }
    ```
    Note the `final` keyword. While not strictly required for `Sendable` conformance itself, it's good practice for immutable classes to prevent subclasses from introducing mutable state. The compiler can infer `Sendable` for such classes.

2.  **It's an `Actor`**: `Actor`s provide their own isolation mechanism, ensuring that access to their mutable state is serialized. Therefore, `Actor` types are implicitly `Sendable`.
    ```swift
    actor SafeCounter: Sendable { // Actor types implicitly conform to Sendable
        var value: Int = 0

        func increment() {
            value += 1
        }

        func getValue() -> Int {
            return value
        }
    }

    func runSafeActorTasks() async {
        let counter = SafeCounter()

        await withTaskGroup(of: Void.self) { group in
            for _ in 0..<1000 {
                group.addTask {
                    await counter.increment() // Safe access via actor isolation
                }
            }
        }
        let finalValue = await counter.getValue()
        print("Final safe actor counter value: \(finalValue)") // Will be 1000
    }

    // To run this example, wrap it in a Task:
    // Task { await runSafeActorTasks() }
    ```
    Here, the `SafeCounter` actor handles concurrent access safely, and its type is `Sendable`.

3.  **It uses internal synchronization**: If a class manages its mutable state using internal synchronization primitives (like `NSLock` or a dispatch queue), it can also be `Sendable`. However, the Swift compiler cannot automatically verify this. In such cases, you might need to manually mark it as `Sendable` (often with `@unchecked Sendable`, as discussed later). This is generally discouraged in favor of actors or value types.

### Functions and Closures: `@Sendable`

Functions and closures can also be `Sendable`. A function or closure is `@Sendable` if it captures only `Sendable` values. This is crucial because when you pass a closure to a `Task` or an `Actor`, the closure's captured environment must be safe to move across concurrency domains.

```swift
func processData(completion: @Sendable @escaping (Result<String, NetworkError>) -> Void) {
    // This function can be called from any concurrency domain
    // The completion handler can be safely passed to another task/actor
    Task {
        await Task.sleep(nanoseconds: 1_000_000_000) // Simulate work
        let result: Result<String, NetworkError> = .success("Data processed!")
        completion(result)
    }
}

// Example of using a @Sendable closure
let myID = UserID(id: "user123") // UserID is Sendable

func performOperation() async {
    let operation: @Sendable () async -> String = {
        // 'myID' is captured here. Since UserID is Sendable, this closure is Sendable.
        await Task.sleep(nanoseconds: 500_000_000)
        return "Operation for \(myID.id) completed."
    }

    let result = await Task { await operation() }.value
    print(result)
}

// To run this example, wrap it in a Task:
// Task { await performOperation() }
```

```
┌───────────────────────┐             ┌───────────────────────┐
│       Value Type      │             │     Reference Type    │
│    (struct, enum)     │             │        (class)        │
└───────────┬───────────┘             └───────────┬───────────┘
            │                                     │
            │ All stored properties/              │ All stored properties are:
            │ associated values are Sendable?     │  - `let` (immutable) AND Sendable
            │                                     │  - OR, type is an Actor
            │                                     │  - OR, protected by internal sync
            ▼                                     ▼
┌───────────────────────┐             ┌───────────────────────┐
│     Automatically     │             │  Compiler can infer   │
│       Sendable        │             │    (if immutable)     │
└───────────────────────┘             │  Manual conformance   │
                                      │   (e.g., @unchecked)  │
                                      └───────────────────────┘
```

## Automatic vs. Manual Conformance

Swift's compiler is smart. For many common types, it can automatically infer `Sendable` conformance:

*   Most standard library value types (`Int`, `String`, `Array`, `Dictionary`, `Date`, `URL`, `UUID`, etc.) are `Sendable`.
*   Structs and enums containing only `Sendable` types are automatically `Sendable`.
*   Final classes with only `let` stored properties of `Sendable` types are automatically `Sendable`.
*   Actor types are automatically `Sendable`.

However, there are situations where you might need to explicitly declare `Sendable` conformance:

### Explicit `Sendable` Conformance

If you have a custom type that the compiler cannot infer as `Sendable` (e.g., a class that uses internal synchronization that Swift doesn't understand, or an `NSObject` subclass), but you know it's safe, you can declare its conformance:

```swift
// Example: A class that uses a lock internally
import Foundation

final class ThreadSafeCache<Key: Hashable, Value>: @unchecked Sendable {
    private var storage: [Key: Value] = [:]
    private let lock = NSLock()

    func set(_ value: Value, forKey key: Key) {
        lock.lock()
        defer { lock.unlock() }
        storage[key] = value
    }

    func get(forKey key: Key) -> Value? {
        lock.lock()
        defer { lock.unlock() }
        return storage[key]
    }
}
```

Notice the `@unchecked Sendable`. This is a powerful and dangerous tool.

### `@unchecked Sendable`: The Escape Hatch

`@unchecked Sendable` is an attribute you apply to a type's `Sendable` conformance declaration. It tells the compiler: "I, the developer, guarantee that this type is safe to send across concurrency domains, even if you can't prove it. Please trust me and suppress any related warnings."

**When to use it:**
*   When integrating with Objective-C classes that are thread-safe but not marked as such for Swift.
*   When implementing complex custom synchronization mechanisms that the Swift compiler cannot analyze.

**When NOT to use it:**
*   **Never use it blindly.** If your type is truly not `Sendable`, using `@unchecked Sendable` will reintroduce data races and undefined behavior, bypassing Swift's safety guarantees.
*   Avoid it if you can achieve `Sendable` conformance through other means (e.g., making a class immutable, using an actor, or refactoring to value types).

Using `@unchecked Sendable` places the burden of correctness entirely on you. If you get it wrong, you're back to debugging elusive concurrency bugs.

## `Sendable` in Action: Practical Scenarios

Let's look at how `Sendable` plays a role in common Swift concurrency patterns.

### Passing Data to `Task`s

When you create a `Task`, any values captured by its closure or passed as parameters should ideally be `Sendable` to ensure safe operation.

```swift
struct WorkItem: Sendable {
    let id: UUID
    let data: String
}

func processWorkItem(_ item: WorkItem) async {
    print("Processing work item \(item.id) with data: \(item.data)")
    await Task.sleep(nanoseconds: 100_000_000)
}

func startProcessingTasks() async {
    let item1 = WorkItem(id: UUID(), data: "First batch")
    let item2 = WorkItem(id: UUID(), data: "Second batch")

    await Task {
        await processWorkItem(item1) // item1 is Sendable, safe to capture
    }.value

    await Task {
        await processWorkItem(item2) // item2 is Sendable, safe to capture
    }.value
}

// To run this example, wrap it in a Task:
// Task { await startProcessingTasks() }
```
Because `WorkItem` is a `Sendable` struct (assuming `UUID` and `String` are `Sendable`), `item1` and `item2` can be safely captured by the respective `Task` closures. Each task gets its own copy of the `WorkItem` value.

### Actors and `Sendable`

Actors are designed to isolate mutable state. When you interact with an actor, you're either sending it `Sendable` data or receiving `Sendable` data from it. The actor itself is `Sendable`.

```swift
actor DataProcessor {
    private var processedCount: Int = 0

    // Input must be Sendable
    func process(_ data: WorkItem) async -> String { // WorkItem is Sendable
        processedCount += 1
        print("Actor processing item \(data.id). Total processed: \(processedCount)")
        await Task.sleep(nanoseconds: 50_000_000)
        return "Processed \(data.id)"
    }

    // Output must be Sendable
    func getProcessedCount() -> Int { // Int is Sendable
        return processedCount
    }
}

func coordinateProcessing() async {
    let processor = DataProcessor()
    let items = (0..<5).map { _ in WorkItem(id: UUID(), data: "Data \($0)") }

    await withTaskGroup(of: String.self) { group in
        for item in items {
            group.addTask {
                await processor.process(item) // item (WorkItem) is Sendable
            }
        }

        for await result in group {
            print("Received result: \(result)")
        }
    }

    let finalCount = await processor.getProcessedCount()
    print("Final processed count: \(finalCount)")
}

// To run this example, wrap it in a Task:
// Task { await coordinateProcessing() }
```
Here, `WorkItem` is `Sendable`, allowing it to be safely passed to the `DataProcessor` actor. The `Int` return type of `getProcessedCount()` is also `Sendable`, allowing it to be safely returned from the actor.

### `TaskGroup`s and `Sendable`

When using `TaskGroup`s, the values passed to `group.addTask` and the return values from the child tasks should be `Sendable`.

```swift
struct CalculationInput: Sendable {
    let value: Int
}

struct CalculationResult: Sendable {
    let originalValue: Int
    let squaredValue: Int
}

func performCalculation(input: CalculationInput) async -> CalculationResult {
    await Task.sleep(nanoseconds: UInt64.random(in: 10_000_000...100_000_000))
    return CalculationResult(originalValue: input.value, squaredValue: input.value * input.value)
}

func runCalculations() async {
    let inputs = (1...5).map { CalculationInput(value: $0) }

    await withTaskGroup(of: CalculationResult.self) { group in
        for input in inputs {
            group.addTask {
                // input (CalculationInput) is Sendable
                await performCalculation(input: input)
            }
        }

        for await result in group {
            // result (CalculationResult) is Sendable
            print("Calculated: \(result.originalValue)^2 = \(result.squaredValue)")
        }
    }
}

// To run this example, wrap it in a Task:
// Task { await runCalculations() }
```
Both `CalculationInput` and `CalculationResult` are `Sendable` structs, ensuring safe data flow within the `TaskGroup`.

## Common Pitfalls and Best Practices

*   **Compiler Warnings are Your Friends**: Don't ignore "Non-Sendable type..." warnings. They are Swift's way of telling you there's a potential data race. Address them by making your types `Sendable`.
*   **Embrace Value Types and Immutability**: Whenever possible, design your data models using structs and enums. For reference types, prefer `final class` with `let` properties. This naturally leads to `Sendable` types and simplifies concurrent programming.
*   **Leverage Actors for Mutable State**: When you absolutely need shared mutable state, use actors. Actors provide built-in isolation and are implicitly `Sendable`.
*   **Avoid `@unchecked Sendable`**: Use this escape hatch only when you fully understand the implications and have thoroughly verified the thread safety of your type through other means (e.g., locks, queues). It's a last resort.
*   **Understand Captured Values in Closures**: Be mindful of what your closures capture. If a closure captures a non-`Sendable` reference type, the closure itself becomes non-`Sendable`, potentially leading to compiler errors when passed to `Task`s or `Actor`s.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 250" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Diagram showing Sendable as a gatekeeper for safe data flow between concurrent domains.">
  <title>Sendable as a Safe Data Flow Gatekeeper</title>

  <!-- Concurrent Context 1 -->
  <rect x="50" y="30" width="120" height="60" rx="10" ry="10" fill="#1565c0" stroke="#0F4C9B" stroke-width="2"/>
  <text x="110" y="65" font-family="Arial" font-size="16" fill="white" text-anchor="middle">Task A / Actor 1</text>

  <!-- Concurrent Context 2 -->
  <rect x="50" y="160" width="120" height="60" rx="10" ry="10" fill="#1565c0" stroke="#0F4C9B" stroke-width="2"/>
  <text x="110" y="195" font-family="Arial" font-size="16" fill="white" text-anchor="middle">Task B / Actor 2</text>

  <!-- Shared Data Before Sendable (Unsafe) -->
  <rect x="250" y="80" width="100" height="40" rx="5" ry="5" fill="#F04B3E" stroke="#E03A2D" stroke-width="2"/>
  <text x="300" y="105" font-family="Arial" font-size="14" fill="white" text-anchor="middle">Unsafe Data</text>

  <!-- Arrows to Unsafe Data -->
  <line x1="170" y1="60" x2="250" y2="90" stroke="#F04B3E" stroke-width="2" marker-end="url(#arrowheadRed)"/>
  <line x1="170" y1="190" x2="250" y2="100" stroke="#F04B3E" stroke-width="2" marker-end="url(#arrowheadRed)"/>
  <text x="210" y="70" font-family="Arial" font-size="12" fill="#F04B3E">Access</text>
  <text x="210" y="180" font-family="Arial" font-size="12" fill="#F04B3E">Access</text>

  <!-- Sendable Data (Safe) -->
  <rect x="450" y="80" width="100" height="40" rx="5" ry="5" fill="#2A8367" stroke="#226B52" stroke-width="2"/>
  <text x="500" y="105" font-family="Arial" font-size="14" fill="white" text-anchor="middle">Sendable Data</text>

  <!-- Arrows to Sendable Data -->
  <line x1="170" y1="60" x2="450" y2="90" stroke="#2A8367" stroke-width="2" marker-end="url(#arrowheadGreen)"/>
  <text x="310" y="70" font-family="Arial" font-size="12" fill="#2A8367">Pass Safely</text>
  <line x1="170" y1="190" x2="450" y2="100" stroke="#2A8367" stroke-width="2" marker-end="url(#arrowheadGreen)"/>
  <text x="310" y="180" font-family="Arial" font-size="12" fill="#2A8367">Pass Safely</text>

  <!-- Label for Unsafe vs Safe -->
  <text x="300" y="40" font-family="Arial" font-size="18" fill="#F04B3E" text-anchor="middle">Without Sendable (Unsafe)</text>
  <text x="500" y="40" font-family="Arial" font-size="18" fill="#2A8367" text-anchor="middle">With Sendable (Safe)</text>

  <!-- Arrowhead definitions -->
  <defs>
    <marker id="arrowheadRed" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#F04B3E" />
    </marker>
    <marker id="arrowheadGreen" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#2A8367" />
    </marker>
  </defs>
</svg>
</div>

## Summary

The `Sendable` protocol is a critical component of Swift's modern concurrency model, providing compile-time safety guarantees against data races when sharing data across concurrent tasks and actors. By understanding how different types conform to `Sendable` – with value types often being automatically `Sendable` and reference types requiring immutability or actor isolation – you can write more robust and predictable concurrent code. Embrace `Sendable` to harness the full power of Swift's structured concurrency safely and effectively.

Happy Swifting!
