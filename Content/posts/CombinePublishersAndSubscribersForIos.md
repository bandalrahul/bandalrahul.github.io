---
title: Combine Publishers and Subscribers for iOS
date: 2026-07-23 11:02
description: Learn the fundamentals of Combine in iOS development, focusing on how Publishers emit values and Subscribers consume them to build reactive data flows.
tags: Combine, iOS, Development
---

# Combine Publishers and Subscribers for iOS

Reactive programming has become a cornerstone of modern iOS development, and Apple's Combine framework is at its heart. If you've ever dealt with asynchronous events, callbacks, or delegates, you know how complex and error-prone managing them can become. Combine offers a declarative Swift API for processing values over time, making your asynchronous code cleaner, more readable, and less error-prone.

This article will dive into the two fundamental building blocks of Combine: **Publishers** and **Subscribers**. Understanding these core concepts is key to unlocking the power of Combine in your iOS applications.

## What is Combine?

At its core, Combine is a framework for handling asynchronous events. It's Apple's answer to reactive programming, similar to RxSwift or ReactiveSwift. It provides a standardized way to:

1.  **Declare** how values are produced (Publishers).
2.  **Transform** these values (Operators).
3.  **Consume** these values (Subscribers).

This paradigm shift helps you move away from imperative, callback-heavy code to a more declarative, stream-based approach.

## The Core Components: Publishers

A `Publisher` is a protocol that declares that a type can deliver a sequence of values over time to one or more `Subscriber` instances. Think of a publisher as a data source. It doesn't actually produce any values until a subscriber explicitly requests them.

Publishers can emit three types of events:

1.  **Zero or more values**: These are the actual data points (e.g., a new text input, a network response).
2.  **One completion event**: This signals that the publisher has finished emitting values. This can be either:
    *   `.finished`: The publisher completed successfully.
    *   `.failure(Error)`: The publisher completed with an error.

Every publisher specifies two associated types: `Output` (the type of values it publishes) and `Failure` (the type of error it can publish, which must conform to Swift's `Error` protocol). If a publisher never fails, its `Failure` type is `Never`.

Let's look at some common types of publishers:

### 1. `Just` Publisher

The simplest publisher, `Just`, emits a single value and then finishes. It's useful for providing an initial value or for testing.

```swift
import Combine

let justPublisher = Just("Hello, Combine!")
    .sink { value in
        print("Received: \(value)")
    }
// Output: Received: Hello, Combine!
```

### 2. `PassthroughSubject`

A `PassthroughSubject` is a publisher that you can imperatively send values to. It acts as both a publisher and a subscriber, allowing you to "inject" values into a Combine stream. This is perfect for bridging existing imperative code with Combine.

```swift
import Combine

// Declare a subject that publishes Strings and never fails
let mySubject = PassthroughSubject<String, Never>()

// Subscribe to the subject
let subscriber = mySubject
    .sink { value in
        print("Subject received: \(value)")
    }

// Send values to the subject
mySubject.send("First message")
mySubject.send("Second message")

// When you're done, send a completion event
mySubject.send(completion: .finished)

// Output:
// Subject received: First message
// Subject received: Second message
```

### 3. `CurrentValueSubject`

Similar to `PassthroughSubject`, but `CurrentValueSubject` holds a buffer of the most recent element. When a new subscriber attaches, it immediately receives the current value.

```swift
import Combine

// Declare a subject with an initial value
let counterSubject = CurrentValueSubject<Int, Never>(0)

// Subscriber 1: Subscribes immediately
let sub1 = counterSubject
    .sink { value in
        print("Subscriber 1 received: \(value)")
    }

// Send a new value
counterSubject.send(1) // Both subscribers will get this

// Subscriber 2: Subscribes later, will immediately get the current value (1)
let sub2 = counterSubject
    .sink { value in
        print("Subscriber 2 received: \(value)")
    }

// Send another value
counterSubject.send(2) // Both subscribers will get this

// Output:
// Subscriber 1 received: 0
// Subscriber 1 received: 1
// Subscriber 2 received: 1
// Subscriber 1 received: 2
// Subscriber 2 received: 2
```

### Other Built-in Publishers

Combine integrates with many existing Apple frameworks:

*   **`NotificationCenter.Publisher`**: Publishes events from `NotificationCenter`.
*   **`URLSession.dataTaskPublisher`**: Publishes data from network requests.
*   **Timer Publishers**: For time-based events.

Here's a visual representation of a publisher emitting values over time:

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A diagram showing a Publisher emitting values over time to a Subscriber.">
  <title>Publisher Emitting Values</title>

  <!-- Publisher Box -->
  <rect x="50" y="50" width="100" height="40" rx="5" ry="5" fill="#2A8367" stroke="#000" stroke-width="2"/>
  <text x="100" y="75" font-family="Arial" font-size="16" fill="#fff" text-anchor="middle">Publisher</text>

  <!-- Value 1 -->
  <circle cx="200" cy="70" r="15" fill="#1565c0" stroke="#000" stroke-width="1"/>
  <text x="200" y="75" font-family="Arial" font-size="14" fill="#fff" text-anchor="middle">A</text>
  <line x1="155" y1="70" x2="180" y2="70" stroke="#000" stroke-width="2" marker-end="url(#arrowhead)"/>

  <!-- Value 2 -->
  <circle cx="280" cy="70" r="15" fill="#1565c0" stroke="#000" stroke-width="1"/>
  <text x="280" y="75" font-family="Arial" font-size="14" fill="#fff" text-anchor="middle">B</text>
  <line x1="220" y1="70" x2="260" y2="70" stroke="#000" stroke-width="2" marker-end="url(#arrowhead)"/>

  <!-- Value 3 -->
  <circle cx="360" cy="70" r="15" fill="#1565c0" stroke="#000" stroke-width="1"/>
  <text x="360" y="75" font-family="Arial" font-size="14" fill="#fff" text-anchor="middle">C</text>
  <line x1="300" y1="70" x2="340" y2="70" stroke="#000" stroke-width="2" marker-end="url(#arrowhead)"/>

  <!-- Completion -->
  <rect x="420" y="60" width="40" height="20" fill="#F04B3E" stroke="#000" stroke-width="1"/>
  <text x="440" y="75" font-family="Arial" font-size="12" fill="#fff" text-anchor="middle">Finish</text>
  <line x1="380" y1="70" x2="410" y2="70" stroke="#000" stroke-width="2" marker-end="url(#arrowhead)"/>

  <!-- Subscriber Box -->
  <rect x="500" y="50" width="100" height="40" rx="5" ry="5" fill="#1565c0" stroke="#000" stroke-width="2"/>
  <text x="550" y="75" font-family="Arial" font-size="16" fill="#fff" text-anchor="middle">Subscriber</text>
  <line x1="465" y1="70" x2="490" y2="70" stroke="#000" stroke-width="2" marker-end="url(#arrowhead)"/>

  <!-- Time Axis -->
  <line x1="50" y1="150" x2="550" y2="150" stroke="#888" stroke-width="1" stroke-dasharray="5,5"/>
  <text x="570" y="155" font-family="Arial" font-size="14" fill="#888">Time</text>

  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#000" />
    </marker>
  </defs>
</svg>
</div>

## The Core Components: Subscribers

A `Subscriber` is a protocol that declares that a type can receive values and a completion event from a `Publisher`. A subscriber is the endpoint of a Combine stream; it's where you actually handle the data.

When a subscriber connects to a publisher, it creates a `Subscription`. This subscription manages the flow of data, allowing the subscriber to request a specific number of values from the publisher (demand).

### 1. `sink(receiveCompletion:receiveValue:)`

This is the most common way to create a subscriber. It takes two closures: one to handle the completion event (either `.finished` or `.failure`) and one to handle each received value.

```swift
import Combine

let numbersPublisher = PassthroughSubject<Int, Never>()

let cancellable = numbersPublisher
    .sink(receiveCompletion: { completion in
        switch completion {
        case .finished:
            print("Publisher finished successfully.")
        case .failure(let error):
            print("Publisher failed with error: \(error.localizedDescription)")
        }
    }, receiveValue: { value in
        print("Received value: \(value)")
    })

numbersPublisher.send(10)
numbersPublisher.send(20)
numbersPublisher.send(completion: .finished)

// Output:
// Received value: 10
// Received value: 20
// Publisher finished successfully.
```

### 2. `assign(to:on:)`

The `assign(to:on:)` subscriber is incredibly useful for binding the output of a publisher directly to a property of an object. This is often used to update UI elements or view model properties.

```swift
import Combine
import Foundation // For NSObject, if needed for KVO compliance

class DataStore {
    var username: String = "Guest" {
        didSet {
            print("Username updated to: \(username)")
        }
    }
}

let store = DataStore()
let namePublisher = PassthroughSubject<String, Never>()

// Assign the output of namePublisher directly to store.username
let cancellableAssignment = namePublisher
    .assign(to: \.username, on: store)

namePublisher.send("Alice")
namePublisher.send("Bob")

// Output:
// Username updated to: Alice
// Username updated to: Bob
```

### `AnyCancellable`: Managing Subscriptions

Whenever you subscribe to a publisher using `sink` or `assign`, these methods return an `AnyCancellable` instance. This `AnyCancellable` object represents the active subscription.

It's crucial to store `AnyCancellable` instances in a property (e.g., `Set<AnyCancellable>`) that lives as long as you want the subscription to be active. When the `AnyCancellable` object is deallocated, it automatically cancels the subscription, preventing memory leaks and unnecessary work.

```swift
import Combine

class ViewModel {
    let namePublisher = PassthroughSubject<String, Never>()
    var greeting: String = "" {
        didSet {
            print("Greeting updated: \(greeting)")
        }
    }

    // Store cancellables to keep subscriptions alive
    var cancellables = Set<AnyCancellable>()

    init() {
        namePublisher
            .map { "Hello, \($0)!" }
            .assign(to: \.greeting, on: self)
            .store(in: &cancellables) // Store the cancellable here

        // Example of another subscription
        namePublisher
            .sink { value in
                print("Raw name received in sink: \(value)")
            }
            .store(in: &cancellables) // Store this one too
    }

    deinit {
        print("ViewModel deallocated. All subscriptions cancelled.")
    }
}

var viewModel: ViewModel? = ViewModel()
viewModel?.namePublisher.send("Charlie")
viewModel?.namePublisher.send("Diana")

// Set viewModel to nil to deallocate it and cancel subscriptions
viewModel = nil
// Output:
// Greeting updated: Hello, Charlie!
// Raw name received in sink: Charlie
// Greeting updated: Hello, Diana!
// Raw name received in sink: Diana
// ViewModel deallocated. All subscriptions cancelled.
```

If `cancellables` were not used, the subscriptions would be immediately deallocated after `init()` completes, and no values would be received.

## Connecting Publishers and Subscribers

The real power of Combine comes from chaining publishers, operators, and subscribers together to form a data flow.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Publisher  │ ──► │   Operator  │ ──► │  Subscriber │
└─────────────┘     └─────────────┘     └─────────────┘
      ^                   ^                   ^
      |                   |                   |
    Emits             Transforms          Receives
    Values              Values              Values
```

## Operators: Transforming the Stream (Briefly)

Between a publisher and a subscriber, you can insert **operators**. Operators are methods that transform, combine, or filter the values emitted by a publisher before they reach the subscriber. They are themselves publishers, meaning you can chain multiple operators together.

Common operators include:

*   `map`: Transforms each value into a new type.
*   `filter`: Only allows values that satisfy a condition to pass through.
*   `debounce`: Delays values until a pause in the stream, useful for search bars.
*   `removeDuplicates`: Filters out consecutive duplicate values.

We won't dive deep into operators here, but they are essential for building complex data pipelines.

## Error Handling in Combine

Publishers can either complete successfully (`.finished`) or with an error (`.failure(Error)`). Subscribers must be prepared to handle both.

When a publisher emits an error, the stream terminates immediately, and no further values will be sent.

You can handle errors in your `sink` closure:

```swift
import Combine

enum MyError: Error {
    case somethingWentWrong
}

let errorPublisher = PassthroughSubject<String, MyError>()

let errorCancellable = errorPublisher
    .sink(receiveCompletion: { completion in
        switch completion {
        case .finished:
            print("Successfully completed.")
        case .failure(let error):
            print("Received error: \(error.localizedDescription)")
        }
    }, receiveValue: { value in
        print("Received value: \(value)")
    })

errorPublisher.send("Data 1")
errorPublisher.send(completion: .failure(MyError.somethingWentWrong))
errorPublisher.send("Data 2") // This will never be received

// Output:
// Received value: Data 1
// Received error: The operation couldn’t be completed. (MyError somethingWentWrong.)
```

You can also use operators like `catch` to recover from errors, replacing the error with a new publisher or a default value.

## Real-World Example: Fetching Data

Let's put Publishers and Subscribers into action with a common task: fetching data from a network API. Combine provides `URLSession.shared.dataTaskPublisher` for this purpose.

```swift
import Combine
import Foundation

// Define a simple Decodable struct for our data
struct Post: Decodable, Identifiable {
    let id: Int
    let title: String
    let body: String
    let userId: Int
}

class PostFetcher {
    var cancellables = Set<AnyCancellable>()
    var posts: [Post] = [] {
        didSet {
            print("Fetched \(posts.count) posts.")
            posts.prefix(2).forEach { print("  - \($0.title)") }
        }
    }
    
    enum NetworkError: Error, LocalizedError {
        case invalidURL
        case network(Error)
        case decoding(Error)
        case unknown
        
        var errorDescription: String? {
            switch self {
            case .invalidURL: return "The URL was invalid."
            case .network(let error): return "Network error: \(error.localizedDescription)"
            case .decoding(let error): return "Decoding error: \(error.localizedDescription)"
            case .unknown: return "An unknown error occurred."
            }
        }
    }

    func fetchPosts() {
        guard let url = URL(string: "https://jsonplaceholder.typicode.com/posts") else {
            print(NetworkError.invalidURL.localizedDescription)
            return
        }

        URLSession.shared.dataTaskPublisher(for: url)
            .tryMap { data, response in
                guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
                    throw NetworkError.network(URLError(.badServerResponse))
                }
                return data
            }
            .decode(type: [Post].self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main) // Ensure UI updates happen on the main thread
            .sink(receiveCompletion: { [weak self] completion in
                switch completion {
                case .finished:
                    print("Post fetching finished successfully.")
                case .failure(let error):
                    // Cast the error to our custom NetworkError if possible
                    if let networkError = error as? NetworkError {
                        print("Error fetching posts: \(networkError.localizedDescription)")
                    } else if let decodingError = error as? DecodingError {
                        print("Decoding error: \(decodingError.localizedDescription)")
                    } else {
                        print("Unknown error: \(error.localizedDescription)")
                    }
                    self?.posts = [] // Clear posts on error
                }
            }, receiveValue: { [weak self] fetchedPosts in
                self?.posts = fetchedPosts
            })
            .store(in: &cancellables) // Store the subscription
    }
}

let fetcher = PostFetcher()
fetcher.fetchPosts()

// Keep the program running for a bit to allow the async network request to complete
import PlaygroundSupport
PlaygroundPage.current.needsIndefiniteExecution = true
```

This example demonstrates a complete Combine pipeline:
1.  `URLSession.shared.dataTaskPublisher`: The publisher initiating the network request.
2.  `tryMap`: An operator to check the HTTP response and extract the `Data`. It can throw an error if the status code is not 200.
3.  `decode`: An operator to parse the `Data` into `[Post]` using `JSONDecoder`. This can also throw a `DecodingError`.
4.  `receive(on: DispatchQueue.main)`: An operator to ensure the subsequent operations (specifically updating `self.posts`) happen on the main thread, which is crucial for UI updates.
5.  `sink`: The subscriber that handles the final `[Post]` array or any errors that occurred along the way.
6.  `store(in: &cancellables)`: Stores the `AnyCancellable` to keep the subscription active.

Here's a diagram illustrating this data flow:

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 700 250" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A Combine data flow diagram for fetching and decoding network data.">
  <title>Combine Network Data Flow</title>

  <!-- Boxes -->
  <rect x="20" y="50" width="120" height="40" rx="5" ry="5" fill="#2A8367" stroke="#000" stroke-width="2"/>
  <text x="80" y="75" font-family="Arial" font-size="14" fill="#fff" text-anchor="middle">URLSession</text>
  <text x="80" y="90" font-family="Arial" font-size="12" fill="#fff" text-anchor="middle">.dataTaskPublisher</text>

  <rect x="160" y="50" width="100" height="40" rx="5" ry="5" fill="#1565c0" stroke="#000" stroke-width="2"/>
  <text x="210" y="75" font-family="Arial" font-size="14" fill="#fff" text-anchor="middle">.tryMap</text>

  <rect x="280" y="50" width="100" height="40" rx="5" ry="5" fill="#1565c0" stroke="#000" stroke-width="2"/>
  <text x="330" y="75" font-family="Arial" font-size="14" fill="#fff" text-anchor="middle">.decode</text>

  <rect x="400" y="50" width="120" height="40" rx="5" ry="5" fill="#1565c0" stroke="#000" stroke-width="2"/>
  <text x="460" y="75" font-family="Arial" font-size="14" fill="#fff" text-anchor="middle">.receive(on: .main)</text>

  <rect x="540" y="50" width="100" height="40" rx="5" ry="5" fill="#F04B3E" stroke="#000" stroke-width="2"/>
  <text x="590" y="75" font-family="Arial" font-size="14" fill="#fff" text-anchor="middle">.sink</text>

  <!-- Arrows with labels -->
  <line x1="145" y1="70" x2="155" y2="70" stroke="#000" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="150" y="105" font-family="Arial" font-size="12" fill="#000" text-anchor="middle">Data, URLResponse</text>

  <line x1="265" y1="70" x2="275" y2="70" stroke="#000" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="270" y="105" font-family="Arial" font-size="12" fill="#000" text-anchor="middle">Data</text>

  <line x1="385" y1="70" x2="395" y2="70" stroke="#000" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="390" y="105" font-family="Arial" font-size="12" fill="#000" text-anchor="middle">[Post]</text>

  <line x1="525" y1="70" x2="535" y2="70" stroke="#000" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="530" y="105" font-family="Arial" font-size="12" fill="#000" text-anchor="middle">[Post]</text>

  <!-- Error Path -->
  <line x1="210" y1="95" x2="210" y2="150" stroke="#F04B3E" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="210" y1="150" x2="590" y2="150" stroke="#F04B3E" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="590" y1="150" x2="590" y1="95" stroke="#F04B3E" stroke-width="1" stroke-dasharray="5,5" marker-end="url(#arrowhead-red)"/>
  <text x="400" y="140" font-family="Arial" font-size="12" fill="#F04B3E" text-anchor="middle">Error Path</text>
  <text x="210" y="165" font-family="Arial" font-size="12" fill="#F04B3E" text-anchor="middle">NetworkError</text>

  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#000" />
    </marker>
    <marker id="arrowhead-red" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#F04B3E" />
    </marker>
  </defs>
</svg>
</div>

## Summary

Publishers and Subscribers are the bedrock of Combine. Publishers (`Just`, `PassthroughSubject`, `URLSession.dataTaskPublisher`, etc.) emit values and a completion event, while Subscribers (`sink`, `assign`) consume these values and handle completion. Operators, placed in between, transform the data stream. Always remember to store your `AnyCancellable` instances to manage the lifecycle of your subscriptions and prevent memory leaks. By mastering these core components, you're well on your way to writing robust, reactive, and maintainable iOS applications with Combine.

Happy Swifting!
