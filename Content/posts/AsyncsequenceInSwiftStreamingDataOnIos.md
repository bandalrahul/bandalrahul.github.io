---
title: AsyncSequence in Swift: Streaming Data on iOS
date: 2026-07-06 12:39
description: Explore Swift's AsyncSequence to efficiently stream and process continuous data flows on iOS, simplifying asynchronous iteration with practical examples.
tags: Swift, Concurrency, iOS
---

# AsyncSequence in Swift: Streaming Data on iOS

Modern applications often deal with continuous streams of data: real-time updates from a server, sensor readings, or user input events. Handling these asynchronous data flows traditionally involved complex callback patterns, delegate methods, or reactive frameworks. With the advent of Swift's concurrency model (`async/await`), Apple introduced `AsyncSequence`, a powerful and elegant way to process asynchronous sequences of values.

For intermediate iOS developers already familiar with `async/await`, `AsyncSequence` is the natural next step to unlock streamlined data processing. It brings the familiar `for-in` loop into the asynchronous world, allowing you to iterate over values as they become available, without blocking the current thread.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 750 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Comparison of Synchronous Sequence and Asynchronous Sequence iteration">
  <title>Synchronous vs Asynchronous Sequence Iteration</title>

  <!-- Synchronous Sequence -->
  <rect x="50" y="30" width="150" height="50" rx="10" fill="#1565c0" opacity="0.1" stroke="#1565c0" stroke-width="2"/>
  <text x="125" y="60" font-family="Arial" font-size="16" fill="#1565c0" text-anchor="middle">Synchronous Sequence</text>

  <path d="M125 85 L125 115" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowheadBlue)"/>
  <text x="125" y="100" font-family="Arial" font-size="14" fill="#666" text-anchor="middle">immediately available</text>

  <rect x="50" y="120" width="150" height="50" rx="10" fill="#2A8367" opacity="0.1" stroke="#2A8367" stroke-width="2"/>
  <text x="125" y="150" font-family="Arial" font-size="16" fill="#2A8367" text-anchor="middle">for element in sequence</text>

  <path d="M125 175 L125 205" stroke="#2A8367" stroke-width="2" marker-end="url(#arrowheadGreen)"/>
  <text x="125" y="190" font-family="Arial" font-size="14" fill="#666" text-anchor="middle">process element</text>


  <!-- Asynchronous Sequence -->
  <rect x="400" y="30" width="180" height="50" rx="10" fill="#1565c0" opacity="0.1" stroke="#1565c0" stroke-width="2"/>
  <text x="490" y="60" font-family="Arial" font-size="16" fill="#1565c0" text-anchor="middle">Asynchronous Sequence</text>

  <path d="M490 85 L490 115" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowheadBlue)"/>
  <text x="490" y="100" font-family="Arial" font-size="14" fill="#666" text-anchor="middle">values become available over time</text>

  <rect x="400" y="120" width="180" height="50" rx="10" fill="#2A8367" opacity="0.1" stroke="#2A8367" stroke-width="2"/>
  <text x="490" y="150" font-family="Arial" font-size="16" fill="#2A8367" text-anchor="middle">for await element in sequence</text>

  <path d="M490 175 L490 205" stroke="#2A8367" stroke-width="2" marker-end="url(#arrowheadGreen)"/>
  <text x="490" y="190" font-family="Arial" font-size="14" fill="#666" text-anchor="middle">process element (suspending)</text>

  <!-- Arrowheads -->
  <defs>
    <marker id="arrowheadBlue" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#1565c0" />
    </marker>
    <marker id="arrowheadGreen" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#2A8367" />
    </marker>
  </defs>
</svg>
</div>

## The Problem with Traditional Streaming

Before `AsyncSequence`, dealing with continuous data streams often involved:

*   **Callbacks/Delegates**: Asynchronous operations would notify their completion via callbacks or delegate methods. For a stream, this means a stream of individual callbacks, which can lead to "callback hell" or complex state management.
*   **Combine Framework**: While powerful, Combine introduces its own set of publishers, subscribers, and operators, requiring a different mental model and often a significant amount of boilerplate for simple tasks.
*   **Manual Thread Management**: Ensuring data is processed on the correct thread, especially for UI updates, required careful use of `DispatchQueue.main.async`.

These approaches, while functional, can obscure the data flow, make error handling cumbersome, and complicate cancellation logic. `AsyncSequence` aims to simplify this by integrating streaming data directly into Swift's structured concurrency.

## Introducing `AsyncSequence`

At its core, `AsyncSequence` is a protocol that allows you to iterate over a sequence of values asynchronously. Just as the `Sequence` protocol enables synchronous iteration with `for element in sequence`, `AsyncSequence` enables asynchronous iteration with `for await element in sequence`.

The `for await` loop will suspend its execution until the next element in the sequence becomes available. This is a crucial distinction:
*   **`Sequence`**: All elements are available immediately or can be generated synchronously. The `for-in` loop completes quickly.
*   **`AsyncSequence`**: Elements become available over time, potentially with significant delays between them. The `for await` loop suspends and resumes as needed, without blocking the thread.

Let's look at a simple example:

```swift
import Foundation

// A simple AsyncSequence that emits numbers with a delay
struct DelayedCounter: AsyncSequence {
    typealias Element = Int

    let limit: Int
    let delay: TimeInterval

    init(limit: Int, delay: TimeInterval) {
        self.limit = limit
        self.delay = delay
    }

    func makeAsyncIterator() -> AsyncIterator {
        AsyncIterator(limit: limit, delay: delay)
    }

    struct AsyncIterator: AsyncIteratorProtocol {
        let limit: Int
        let delay: TimeInterval
        var current = 0

        mutating func next() async throws -> Int? {
            guard current < limit else {
                return nil // Sequence has ended
            }

            try await Task.sleep(for: .seconds(delay)) // Simulate asynchronous work
            let value = current
            current += 1
            return value
        }
    }
}

// How to consume an AsyncSequence
func consumeCounter() async {
    print("Starting to consume delayed counter...")
    do {
        for await number in DelayedCounter(limit: 5, delay: 0.5) {
            print("Received number: \(number)")
        }
        print("Finished consuming delayed counter.")
    } catch {
        print("An error occurred: \(error)")
    }
}

// Call the async function
Task {
    await consumeCounter()
}
// Expected output (with 0.5s delays):
// Starting to consume delayed counter...
// Received number: 0
// Received number: 1
// Received number: 2
// Received number: 3
// Received number: 4
// Finished consuming delayed counter.
```
In this example, `DelayedCounter` conforms to `AsyncSequence` and produces numbers one by one, pausing for a specified `delay` between each. The `for await` loop in `consumeCounter()` elegantly handles the asynchronous nature, waiting for each number to arrive without blocking the main thread.

## Building Custom `AsyncSequence`s

While you can conform custom types to `AsyncSequence` and `AsyncIteratorProtocol` as shown above, Swift provides easier ways to bridge existing asynchronous APIs into `AsyncSequence`: `AsyncStream` and `AsyncThrowingStream`.

### `AsyncStream`

`AsyncStream` is a concrete, non-throwing `AsyncSequence` type that allows you to create a bridge from existing callback-based or delegate-based APIs. It's perfect for when you need to provide an `AsyncSequence` interface to a source that doesn't natively offer one.

Let's imagine we want to receive location updates as an `AsyncSequence`.
(Note: A full Core Location example would be more involved, requiring `CLLocationManagerDelegate` and permissions. Here, we'll simulate it.)

```swift
import CoreLocation // Just for type, not full implementation

// Simulate a LocationManager that uses a callback
class MockLocationManager {
    typealias LocationUpdateHandler = (CLLocation) -> Void
    private var handler: LocationUpdateHandler?
    private var timer: Timer?
    private var currentLocation = CLLocation(latitude: 34.0522, longitude: -118.2437) // LA

    func startUpdatingLocation(handler: @escaping LocationUpdateHandler) {
        self.handler = handler
        timer = Timer.scheduledTimer(withTimeInterval: 2.0, repeats: true) { [weak self] _ in
            guard let self = self else { return }
            // Simulate location change
            let newLatitude = self.currentLocation.coordinate.latitude + Double.random(in: -0.01...0.01)
            let newLongitude = self.currentLocation.coordinate.longitude + Double.random(in: -0.01...0.01)
            self.currentLocation = CLLocation(latitude: newLatitude, longitude: newLongitude)
            handler(self.currentLocation)
        }
    }

    func stopUpdatingLocation() {
        timer?.invalidate()
        timer = nil
        handler = nil
    }
}

// Bridge MockLocationManager to an AsyncSequence using AsyncStream
extension MockLocationManager {
    var locations: AsyncStream<CLLocation> {
        AsyncStream { continuation in
            self.startUpdatingLocation { location in
                continuation.yield(location)
            }
            // When the AsyncStream is terminated (e.g., consumer task cancelled),
            // call stopUpdatingLocation.
            continuation.onTermination = { @Sendable _ in
                self.stopUpdatingLocation()
            }
        }
    }
}

// Consume the location stream
func monitorLocations() async {
    let locationManager = MockLocationManager()
    print("Starting location monitoring...")
    do {
        for await location in locationManager.locations {
            print("Received location: \(location.coordinate.latitude), \(location.coordinate.longitude)")
            // Simulate processing a few locations then stopping
            if location.coordinate.latitude > 34.06 {
                print("Location reached threshold, stopping monitoring.")
                break // This will terminate the AsyncStream
            }
        }
        print("Location monitoring finished.")
    } catch {
        print("Error monitoring locations: \(error)")
    }
}

// Run the monitoring in a Task
Task {
    await monitorLocations()
}
```
The `continuation` in `AsyncStream`'s closure is your gateway to yielding values (`continuation.yield(value)`), signaling completion (`continuation.finish()`), and handling termination (`continuation.onTermination`).

### `AsyncThrowingStream`

If your asynchronous source can produce errors, you'll use `AsyncThrowingStream`. It works identically to `AsyncStream` but allows you to `throw` errors via `continuation.yield(error:)` or `continuation.finish(throwing:)`.

```swift
enum DataStreamError: Error, LocalizedError {
    case connectionLost
    case invalidData
    
    var errorDescription: String? {
        switch self {
        case .connectionLost: return "Network connection lost."
        case .invalidData: return "Received invalid data."
        }
    }
}

func createThrowingStream() -> AsyncThrowingStream<String, Error> {
    AsyncThrowingStream { continuation in
        Task {
            for i in 1...5 {
                if Task.isCancelled {
                    print("Stream creation cancelled.")
                    continuation.finish()
                    return
                }
                await Task.sleep(for: .seconds(0.5))
                if i == 3 {
                    continuation.yield(with: .failure(DataStreamError.connectionLost))
                    continuation.finish() // Stream ends after error
                    return
                }
                continuation.yield("Data chunk \(i)")
            }
            continuation.finish()
        }
    }
}

func consumeThrowingStream() async {
    print("Starting to consume throwing stream...")
    do {
        for await chunk in createThrowingStream() {
            print("Received: \(chunk)")
        }
        print("Throwing stream finished successfully.")
    } catch {
        print("Error consuming throwing stream: \(error.localizedDescription)")
    }
}

Task {
    await consumeThrowingStream()
}
// Expected output:
// Starting to consume throwing stream...
// Received: Data chunk 1
// Received: Data chunk 2
// Error consuming throwing stream: Network connection lost.
```

## Practical Use Cases on iOS

`AsyncSequence` shines in scenarios where data arrives over time.

### 1. Network Streaming (e.g., `URLSession.shared.bytes`)

Reading large files or streaming data from a network endpoint is a perfect fit. `URLSession` offers a native `AsyncSequence` for this:

```swift
func downloadFileContent(from url: URL) async {
    print("Starting download from \(url.lastPathComponent)...")
    do {
        let (bytes, response) = try await URLSession.shared.bytes(for: URLRequest(url: url))
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            print("Failed to download: Invalid response.")
            return
        }
        
        var receivedBytes = 0
        for try await byte in bytes {
            // Process each byte as it arrives
            // For simplicity, just count
            receivedBytes += 1
            if receivedBytes % 1024 == 0 { // Print progress every KB
                print("Received \(receivedBytes / 1024) KB...")
            }
        }
        print("Download complete. Total bytes received: \(receivedBytes)")
    } catch {
        print("Download failed: \(error.localizedDescription)")
    }
}

// Example usage:
let largeFileURL = URL(string: "https://speed.hetzner.de/100MB.bin")! // A public large file
Task {
    await downloadFileContent(from: largeFileURL)
}
```

### 2. Notification Center

You can turn `NotificationCenter` notifications into an `AsyncSequence` using `notifications(named:object:)`:

```swift
func observeKeyboardNotifications() async {
    print("Observing keyboard notifications...")
    
    let keyboardWillShow = NotificationCenter.default.notifications(named: UIResponder.keyboardWillShowNotification)
    let keyboardWillHide = NotificationCenter.default.notifications(named: UIResponder.keyboardWillHideNotification)
    
    // Merge two streams into one for simpler iteration
    let combinedNotifications = keyboardWillShow.merge(keyboardWillHide)

    for await notification in combinedNotifications {
        if notification.name == UIResponder.keyboardWillShowNotification {
            print("Keyboard will show!")
            if let frame = notification.userInfo?[UIResponder.keyboardFrameEndUserInfoKey] as? CGRect {
                print("Keyboard frame: \(frame)")
            }
        } else if notification.name == UIResponder.keyboardWillHideNotification {
            print("Keyboard will hide!")
        }
    }
    print("Stopped observing keyboard notifications.")
}

// To run this, you'd typically start it in a View's task modifier or similar.
// For demonstration, we'll just run it in a Task.
import UIKit // Required for UIResponder.keyboardWillShowNotification

Task {
    await observeKeyboardNotifications()
}
// Output will appear when the system keyboard shows/hides, e.g., in a simulator.
```

This ASCII diagram illustrates a typical data flow through `AsyncStream`:
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Raw Data Source│     │  AsyncStream    │     │  for await ...  │
│ (e.g., Sensor,  │ --> │ (Bridging Layer)│ --> │  (Consumer Task)│
│    Network API) │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                                               │
         │ (yields data via callbacks/delegates)         │ (suspends/resumes)
         ▼                                               ▼
┌─────────────────┐                               ┌─────────────────┐
│  continuation.  │                               │  Process        │
│    yield(data)  │                               │  Received Data  │
└─────────────────┘                               └─────────────────┘
```

## Operators and Transformations

Just like `Sequence` offers methods like `map`, `filter`, `prefix`, `AsyncSequence` also has its asynchronous counterparts. These operators allow you to transform, filter, and combine asynchronous streams of data in a declarative way.

For example, to filter only even numbers from our `DelayedCounter`:

```swift
func consumeFilteredCounter() async {
    print("Starting to consume filtered counter...")
    do {
        let evenNumbers = DelayedCounter(limit: 10, delay: 0.3)
            .filter { $0 % 2 == 0 } // Asynchronously filters
            .map { "Even: \($0)" }   // Asynchronously transforms
        
        for await text in evenNumbers {
            print(text)
        }
        print("Finished consuming filtered counter.")
    } catch {
        print("An error occurred during filtering: \(error)")
    }
}

Task {
    await consumeFilteredCounter()
}
// Expected output (with delays):
// Starting to consume filtered counter...
// Even: 0
// Even: 2
// Even: 4
// Even: 6
// Even: 8
// Finished consuming filtered counter.
```

## Error Handling and Cancellation

Error handling in `AsyncSequence` is straightforward with `AsyncThrowingStream` and `do-catch` blocks around your `for await` loop. When an error is thrown from `next()` or yielded via `continuation.yield(with: .failure(error))`, the `for await` loop will exit, and the error will be caught by the surrounding `do-catch` block.

Cancellation is also handled gracefully by Swift's structured concurrency. If the `Task` consuming an `AsyncSequence` is cancelled, the `for await` loop will terminate. If you've used `continuation.onTermination` with `AsyncStream`/`AsyncThrowingStream`, your cleanup code (like `stopUpdatingLocation()`) will be executed, preventing resource leaks.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 700 250" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="AsyncSequence Lifecycle with Data Flow and Cancellation">
  <title>AsyncSequence Lifecycle and Cancellation</title>

  <!-- Start Event -->
  <circle cx="100" cy="50" r="20" fill="#2A8367" opacity="0.2" stroke="#2A8367" stroke-width="2"/>
  <text x="100" y="55" font-family="Arial" font-size="14" fill="#2A8367" text-anchor="middle">Start</text>

  <!-- Data Flow Boxes -->
  <rect x="180" y="30" width="100" height="40" rx="8" fill="#1565c0" opacity="0.1" stroke="#1565c0" stroke-width="2"/>
  <text x="230" y="55" font-family="Arial" font-size="14" fill="#1565c0" text-anchor="middle">Yield Data 1</text>

  <rect x="320" y="30" width="100" height="40" rx="8" fill="#1565c0" opacity="0.1" stroke="#1565c0" stroke-width="2"/>
  <text x="370" y="55" font-family="Arial" font-size="14" fill="#1565c0" text-anchor="middle">Yield Data 2</text>

  <rect x="460" y="30" width="100" height="40" rx="8" fill="#1565c0" opacity="0.1" stroke="#1565c0" stroke-width="2"/>
  <text x="510" y="55" font-family="Arial" font-size="14" fill="#1565c0" text-anchor="middle">Yield Data 3</text>

  <!-- Arrows for Data Flow -->
  <path d="M120 50 L170 50" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowheadBlue)"/>
  <path d="M280 50 L310 50" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowheadBlue)"/>
  <path d="M420 50 L450 50" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowheadBlue)"/>
  <path d="M560 50 L610 50" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowheadBlue)"/>

  <!-- End Event (Success) -->
  <circle cx="630" cy="50" r="20" fill="#2A8367" opacity="0.2" stroke="#2A8367" stroke-width="2"/>
  <text x="630" y="55" font-family="Arial" font-size="14" fill="#2A8367" text-anchor="middle">Finish</text>

  <!-- Cancellation Path -->
  <path d="M370 70 L370 140" stroke="#F04B3E" stroke-width="2" marker-end="url(#arrowheadRed)"/>
  <text x="370" y="105" font-family="Arial" font-size="14" fill="#666" text-anchor="middle">Task Cancellation</text>

  <rect x="300" y="150" width="140" height="40" rx="8" fill="#F04B3E" opacity="0.1" stroke="#F04B3E" stroke-width="2"/>
  <text x="370" y="175" font-family="Arial" font-size="14" fill="#F04B3E" text-anchor="middle">Stream Termination</text>

  <path d="M370 190 L370 220" stroke="#F04B3E" stroke-width="2" marker-end="url(#arrowheadRed)"/>
  <text x="370" y="235" font-family="Arial" font-size="14" fill="#666" text-anchor="middle">Cleanup (onTermination)</text>


  <!-- Arrowheads -->
  <defs>
    <marker id="arrowheadBlue" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#1565c0" />
    </marker>
    <marker id="arrowheadGreen" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#2A8367" />
    </marker>
    <marker id="arrowheadRed" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#F04B3E" />
    </marker>
  </defs>
</svg>
</div>

## Summary

`AsyncSequence` is a fundamental building block of modern Swift concurrency for handling streaming data. It provides a clean, declarative, and type-safe way to iterate over asynchronous sequences of values, integrating seamlessly with `async/await`. By leveraging `AsyncStream` and `AsyncThrowingStream`, you can easily bridge existing callback-based APIs to the `AsyncSequence` world, simplifying your code and making it more robust against errors and cancellations. Whether you're dealing with network streams, sensor data, or UI events, `AsyncSequence` offers a powerful paradigm shift for managing continuous data flows on Apple platforms.

Happy Swifting!
