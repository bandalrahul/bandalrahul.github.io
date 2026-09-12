---
title: Common Swift Concurrency Pitfalls on iOS
date: 2026-09-12 12:32
description: Explore common pitfalls when working with Swift Concurrency on iOS, including UI updates, actor reentrancy, and unstructured tasks.
tags: Swift, Concurrency, iOS
---

# Common Swift Concurrency Pitfalls on iOS

Swift Concurrency, with its `async/await` syntax and Actors, has fundamentally changed how we write asynchronous code on Apple platforms. It offers a powerful, readable, and type-safe way to manage concurrent operations, moving us away from complex completion handlers and callback pyramids. However, like any powerful tool, it comes with its own set of nuances and potential pitfalls.

While `async/await` makes concurrent code *look* simpler, truly understanding its underlying behavior is crucial to avoid subtle bugs, performance issues, and even crashes. This article assumes you have a basic understanding of `async/await`, `Task`, and `Actors`. We'll dive into some of the most common mistakes and misunderstandings developers encounter when adopting Swift Concurrency in their iOS apps, providing practical solutions to help you write robust and efficient concurrent code.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Diagram illustrating common Swift Concurrency pitfalls.">
  <title>Common Swift Concurrency Pitfalls</title>

  <!-- Happy Path -->
  <rect x="50" y="30" width="200" height="60" rx="10" ry="10" fill="#2A8367" stroke="#2A8367" stroke-width="2"/>
  <text x="150" y="65" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">Structured Concurrency</text>
  <path d="M150 90 L150 120" stroke="#2A8367" stroke-width="2" marker-end="url(#arrowGreen)"/>
  <rect x="50" y="120" width="200" height="60" rx="10" ry="10" fill="#2A8367" stroke="#2A8367" stroke-width="2"/>
  <text x="150" y="155" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">Safe & Efficient Code</text>

  <!-- Pitfall Path -->
  <rect x="350" y="30" width="200" height="60" rx="10" ry="10" fill="#F04B3E" stroke="#F04B3E" stroke-width="2"/>
  <text x="450" y="65" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">Common Pitfalls</text>
  <path d="M450 90 L450 120" stroke="#F04B3E" stroke-width="2" marker-end="url(#arrowRed)"/>
  <rect x="350" y="120" width="200" height="60" rx="10" ry="10" fill="#F04B3E" stroke="#F04B3E" stroke-width="2"/>
  <text x="450" y="155" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">Bugs & Crashes</text>

  <!-- Connecting text -->
  <text x="300" y="105" font-family="Arial, sans-serif" font-size="18" fill="#1565c0" text-anchor="middle">Understanding Is Key</text>

  <!-- Markers for arrows -->
  <defs>
    <marker id="arrowGreen" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
      <path d="M0,0 L10,5 L0,10 Z" fill="#2A8367" />
    </marker>
    <marker id="arrowRed" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
      <path d="M0,0 L10,5 L0,10 Z" fill="#F04B3E" />
    </marker>
  </defs>
</svg>
</div>

## 1. Forgetting `await` on `async` Calls

This might seem obvious, but it's a very common early pitfall. When you call an `async` function, the compiler *requires* you to either `await` its result or explicitly launch it within a `Task`. Forgetting `await` often leads to a compiler warning like "Expression is 'async' but is not 'await'ed".

If you ignore this warning and wrap the `async` call in a `Task { ... }` without `await`, you might inadvertently create a detached task that runs in the background, potentially leading to race conditions or unexpected behavior if its side effects are not properly synchronized.

```swift
func fetchData() async -> String {
    // Simulate a network request
    try? await Task.sleep(for: .seconds(1))
    return "Data fetched!"
}

func processData() async {
    // Pitfall: Forgetting 'await' or not handling the task
    // let data = fetchData() // Compiler warning: 'async' call is not 'await'ed
    
    // Correct way: Awaiting the result
    let data = await fetchData()
    print(data)
    
    // Or, if you intend to run it detached and don't need the result immediately:
    Task {
        let backgroundData = await fetchData()
        print("Background data: \(backgroundData)")
    }
}

// Example usage
Task {
    await processData()
}
```

**Solution:** Always heed compiler warnings. If a function is `async`, you must `await` its result if you want to pause the current task until it completes. If you intend to run it concurrently without waiting, explicitly wrap it in a `Task { await someAsyncCall() }` and consider its lifecycle and potential side effects carefully.

## 2. UI Updates Off the Main Actor

This is a classic concurrency problem that persists with Swift Concurrency. UIKit and SwiftUI views are not thread-safe and must always be updated on the main thread (or, more accurately, on the `MainActor`). Forgetting this can lead to UI glitches, inconsistent states, or outright crashes.

```swift
class ViewController: UIViewController {
    @IBOutlet weak var statusLabel: UILabel!

    func loadDataAndDisplay() async {
        let data = await fetchData() // Assume fetchData() is async and runs on a background context

        // Pitfall: Updating UI directly after an await that might have switched contexts
        // statusLabel.text = "Loaded: \(data)" // Potentially off MainActor, can crash or glitch!

        // Correct way 1: Mark the entire function or class as MainActor
        // If 'loadDataAndDisplay' was '@MainActor' it would automatically hop back.
        
        // Correct way 2: Explicitly hop back to MainActor for UI updates
        await MainActor.run {
            self.statusLabel.text = "Loaded: \(data)"
            self.statusLabel.textColor = .systemGreen
        }
    }
    
    // ... fetchData() implementation ...
}
```

The `await MainActor.run { ... }` block ensures that the code inside it executes on the `MainActor`. Alternatively, you can mark an entire function or class with `@MainActor` if all its operations, or at least its entry points, are intended to run on the main actor.

```swift
@MainActor
class MyViewModel: ObservableObject {
    @Published var message: String = "Loading..."

    func fetchAndUpdateMessage() async {
        let data = await someNetworkCall() // Runs off MainActor if not marked @MainActor
        self.message = "Data: \(data)" // This line automatically hops back to MainActor because the function is @MainActor
    }
}
```

This ensures that any state changes or UI updates handled by `MyViewModel` automatically occur on the `MainActor`, preventing common UI concurrency bugs.

```
┌───────────────┐     ┌───────────────────┐     ┌───────────────┐
│ Background    │     │                   │     │               │
│ Task (Data)   │ ──► │     MainActor     │ ──► │   UI Update   │
│               │     │                   │     │               │
└───────────────┘     └───────────────────┘     └───────────────┘
```

## 3. Actor Reentrancy Misunderstandings

Actors are designed to protect their mutable state from concurrent access. They guarantee that only one piece of code can access an actor's isolated state at any given time. However, actors are *reentrant* by default. This means that when an actor method `await`s another asynchronous operation, the actor temporarily "pauses" its current execution and allows other messages (method calls) to be processed.

This reentrancy can lead to unexpected state changes between the `await` points if you're not careful.

```swift
actor BankAccount {
    private var balance: Double

    init(initialBalance: Double) {
        self.balance = initialBalance
    }

    func withdraw(amount: Double) async throws {
        // Pitfall: State can change between the check and the actual withdrawal
        if balance < amount { // Check 1
            throw BankError.insufficientFunds
        }

        // Simulate an asynchronous operation (e.g., calling an external service)
        try await Task.sleep(for: .milliseconds(100))

        // If another withdrawal happens here, 'balance' might have changed!
        // A second withdrawal could have reduced the balance below 'amount'
        // after Check 1 but before the actual deduction.
        balance -= amount // Withdrawal
        print("Withdrew \(amount), new balance: \(balance)")
    }
    
    func deposit(amount: Double) {
        balance += amount
        print("Deposited \(amount), new balance: \(balance)")
    }

    func getBalance() -> Double {
        return balance
    }
}

enum BankError: Error {
    case insufficientFunds
}

// Example of reentrancy issue
Task {
    let account = BankAccount(initialBalance: 100)

    async let withdraw1 = account.withdraw(amount: 70) // Initiates withdrawal
    async let withdraw2 = account.withdraw(amount: 50) // Initiates another withdrawal while the first is 'await'ing

    // Due to reentrancy, the second withdraw might be processed
    // after the first's 'if balance < amount' check but before its actual deduction.
    // If balance was 100, withdraw1 checks 100 < 70 (false).
    // Then withdraw2 checks 100 < 50 (false).
    // Then withdraw1 deducts, balance = 30.
    // Then withdraw2 deducts, balance = -20. (This would be a bug!)

    // For this specific example, Swift's actor isolation would prevent the negative balance
    // because the `withdraw` method itself would be isolated. The pitfall arises
    // when you rely on state that could be modified by *other* actor methods
    // while the current one is suspended.

    // A more realistic reentrancy pitfall:
    // If `withdraw` called an `async` external validation service,
    // and another `deposit` or `withdraw` call modified `balance`
    // *before* the first `withdraw` resumed and completed.
    // To prevent this, capture the state before any `await` point:

    await account.deposit(amount: 100) // Example for demonstration
    let initialBalanceForWithdrawal = await account.getBalance() // Capture state
    
    // Now, if `withdraw` was structured to use this captured state,
    // it would be safer, but Swift actors handle this more robustly than traditional locks.
    // The key is to be aware that the actor's state *can* change during an `await` pause.
    
    do {
        try await withdraw1
        try await withdraw2
    } catch {
        print("Error: \(error)")
    }
    print("Final balance: \(await account.getBalance())")
}
```

**Solution:** Be acutely aware that an actor's state can change across an `await` boundary. If your logic depends on a certain state being true *before and after* an `await`, you might need to capture that state into a local variable before the `await` or re-validate it after the `await`. For critical state, you might need to introduce a lock or a more complex state machine if reentrancy causes issues, but for simple cases like the `BankAccount` example, Swift's actor isolation often handles it correctly by ensuring only one method runs at a time. The pitfall is *assuming* no other actor method ran during an `await`.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Diagram illustrating actor reentrancy during an await operation.">
  <title>Actor Reentrancy</title>

  <!-- Actor Box -->
  <rect x="50" y="30" width="500" height="150" rx="15" ry="15" fill="#E0E0E0" stroke="#1565c0" stroke-width="2"/>
  <text x="300" y="55" font-family="Arial, sans-serif" font-size="20" fill="#1565c0" text-anchor="middle">MyActor</text>

  <!-- Method 1 Flow -->
  <rect x="70" y="80" width="100" height="30" rx="5" ry="5" fill="#2A8367"/>
  <text x="120" y="100" font-family="Arial, sans-serif" font-size="14" fill="white" text-anchor="middle">Method A Start</text>
  <path d="M170 95 L220 95" stroke="#2A8367" stroke-width="2" marker-end="url(#arrowGreen)"/>
  <rect x="220" y="80" width="100" height="30" rx="5" ry="5" fill="#F04B3E"/>
  <text x="270" y="100" font-family="Arial, sans-serif" font-size="14" fill="white" text-anchor="middle">await call()</text>
  <path d="M320 95 L370 95" stroke="#2A8367" stroke-width="2" marker-end="url(#arrowGreen)"/>
  <rect x="370" y="80" width="100" height="30" rx="5" ry="5" fill="#2A8367"/>
  <text x="420" y="100" font-family="Arial, sans-serif" font-size="14" fill="white" text-anchor="middle">Method A Resume</text>

  <!-- Method 2 Flow (reentrant) -->
  <rect x="220" y="130" width="100" height="30" rx="5" ry="5" fill="#1565c0"/>
  <text x="270" y="150" font-family="Arial, sans-serif" font-size="14" fill="white" text-anchor="middle">Method B runs</text>
  
  <!-- Arrows for reentrancy -->
  <path d="M270 110 L270 130" stroke="#F04B3E" stroke-width="2" marker-end="url(#arrowBlue)"/>
  <text x="270" y="125" font-family="Arial, sans-serif" font-size="12" fill="#F04B3E" text-anchor="middle">Reentrancy</text>

  <defs>
    <marker id="arrowGreen" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
      <path d="M0,0 L10,5 L0,10 Z" fill="#2A8367" />
    </marker>
    <marker id="arrowRed" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
      <path d="M0,0 L10,5 L0,10 Z" fill="#F04B3E" />
    </marker>
     <marker id="arrowBlue" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
      <path d="M0,0 L10,5 L0,10 Z" fill="#1565c0" />
    </marker>
  </defs>
</svg>
</div>

## 4. Unstructured Concurrency Leaks (Detached Tasks)

While `Task { ... }` is convenient for launching fire-and-forget operations, over-reliance on it for long-running or UI-related tasks can lead to resource leaks if not managed carefully. A `Task` launched this way is "detached" from its calling context and will continue to run even if the object that created it is deallocated, potentially leading to memory issues or unexpected background work.

```swift
class DataFetcher {
    var data: String?

    func startFetching() {
        // Pitfall: Detached Task without explicit cancellation or lifecycle management
        Task {
            print("Fetching started...")
            try? await Task.sleep(for: .seconds(5)) // Simulate long operation
            self.data = "Fetched Data!"
            print("Fetching finished. Data: \(self.data ?? "nil")")
            // If DataFetcher is deallocated before this finishes, 'self.data' might still be updated
            // or the task continues to consume resources.
        }
    }
    
    deinit {
        print("DataFetcher deallocated.")
    }
}

// Example usage
var fetcher: DataFetcher? = DataFetcher()
fetcher?.startFetching()

// If we nil out the fetcher immediately, the Task might still run
// and try to update 'data' on a deallocated instance, or just waste resources.
fetcher = nil // DataFetcher deallocated, but Task might still be running!
```

**Solution:** Prefer structured concurrency (`async let`, `TaskGroup`) where tasks are implicitly cancelled when their parent task or scope finishes. When using `Task { ... }` for fire-and-forget, consider linking it to a `Task` handle and cancelling it explicitly, especially if it's tied to a view's or object's lifecycle.

For SwiftUI, `task(id:priority:_:)` or `onAppear` with an explicit `Task` cancellation are great options:

```swift
import SwiftUI

struct MyView: View {
    @State private var message = "Loading..."
    @State private var dataTask: Task<Void, Never>?

    var body: some View {
        Text(message)
            .onAppear {
                // Correct: Attaching Task to view's lifecycle
                dataTask = Task {
                    await fetchData()
                }
            }
            .onDisappear {
                dataTask?.cancel() // Cancel the task when the view disappears
                print("Task cancelled on disappear.")
            }
            // Alternative: Using .task(id:value:_:) for automatic cancellation
            // .task(id: true) { // 'id: true' means it runs once and cancels when view disappears
            //     await fetchData()
            // }
    }

    func fetchData() async {
        do {
            try await Task.sleep(for: .seconds(3))
            if !Task.isCancelled { // Always check for cancellation
                await MainActor.run {
                    message = "Data loaded!"
                }
            }
        } catch {
            await MainActor.run {
                message = "Loading failed or cancelled."
            }
        }
    }
}
```

## 5. Deadlocks with Synchronous Access to Actors

Actors are fundamentally asynchronous. Their isolation model is built around `await`ing messages. Trying to access an actor's isolated state or call its methods synchronously from outside the actor's isolation domain will result in a compiler error. This is by design to prevent race conditions.

```swift
actor Counter {
    private var value = 0

    func increment() -> Int {
        value += 1
        return value
    }

    func getValue() -> Int {
        return value
    }
}

let counter = Counter()

// Pitfall: Trying to access actor state synchronously
// let currentValue = counter.value // Error: Actor-isolated property 'value' can not be referenced from a non-isolated context
// let newValue = counter.increment() // Error: Call to actor-isolated instance method 'increment()' in a synchronous nonisolated context

// Correct way: Always await actor methods
Task {
    let initialValue = await counter.getValue()
    print("Initial value: \(initialValue)")

    let incrementedValue = await counter.increment()
    print("Incremented value: \(incrementedValue)")
}
```

**Solution:** Embrace the asynchronous nature of actors. Always `await` calls to actor methods or property accessors from outside the actor. If you need a synchronous "snapshot" of an actor's state, the actor must provide an `async` method to retrieve it.

## 6. Overuse of `Task.sleep()`

`Task.sleep()` is a convenient way to introduce a delay in an `async` task. However, it's often misused, especially for UI-related delays or to "fix" race conditions.

```swift
func performAnimationAndThenUpdate() async {
    // Pitfall: Using Task.sleep for UI-related delays
    // This pauses the current task, but might not be the best for UI responsiveness
    // or when you need a delay for visual effect.
    await MainActor.run {
        // Start animation
    }
    try? await Task.sleep(for: .seconds(0.5))
    await MainActor.run {
        // End animation or update UI
    }
}
```

While `Task.sleep()` is non-blocking to the underlying thread, it *does* pause the current task. For UI animations or delays where you want to ensure the UI remains responsive, or for debouncing user input, other mechanisms might be more appropriate.

**Solution:** Use `Task.sleep()` when you specifically need to pause the *current task* for a duration (e.g., simulating network delays in tests, polling with a delay). For UI-related delays, especially if you're dealing with UIKit, consider `DispatchQueue.main.asyncAfter` if you want to schedule a block on the main queue without blocking the current task. For debouncing, consider using `Combine` operators or a custom debouncer class.

```swift
// For UI-related delays
func performAnimationWithDispatchQueue() {
    // Start animation
    
    DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
        // End animation or update UI after delay
    }
}
```

## Summary

Swift Concurrency is a game-changer for asynchronous programming on Apple platforms, but a deep understanding of its mechanisms is key to avoiding common pitfalls. By being mindful of where your code runs (especially the `MainActor`), understanding actor reentrancy, managing the lifecycle of `Task`s, respecting actor isolation, and using `Task.sleep()` judiciously, you can write more reliable, performant, and maintainable concurrent code. Embrace the power of `async/await`, but always with an eye on these potential traps.

Happy Swifting!
