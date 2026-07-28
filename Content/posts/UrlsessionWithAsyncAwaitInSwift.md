---
title: URLSession with async/await in Swift
date: 2026-07-28 11:10
description: Learn how to modernize your networking code with Swift's async/await for URLSession, simplifying data fetching and error handling.
tags: Networking, Swift, iOS
---

# URLSession with async/await in Swift

Networking is a fundamental aspect of almost every modern iOS application. For years, Swift developers have relied on `URLSession` and its completion handler-based APIs to fetch data, upload files, and interact with web services. While functional, these callback-driven patterns often led to nested closures, complex error handling, and a phenomenon affectionately (or not so affectionately) known as the "pyramid of doom."

With the advent of Swift's structured concurrency, `async/await` has revolutionized how we write asynchronous code, making it more readable, maintainable, and less prone to errors. `URLSession` has fully embraced this paradigm shift, offering new `async/await`-native methods that dramatically simplify networking operations.

In this article, we'll dive deep into using `URLSession` with Swift's `async/await`. We'll explore the new APIs, see how they streamline common tasks, improve error handling, and make your networking code a joy to work with. If you're ready to modernize your app's networking layer, you're in the right place!

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Comparison of URLSession with Completion Handlers vs. Async/Await">
  <title>URLSession Networking: Before (Completion Handler) vs. After (Async/Await)</title>
  <!-- Completion Handler Side -->
  <rect x="20" y="20" width="260" height="180" rx="10" ry="10" stroke="#1565c0" stroke-width="2" fill="#e3f2fd"/>
  <text x="150" y="45" font-family="Arial, sans-serif" font-size="18" font-weight="bold" text-anchor="middle" fill="#1565c0">Traditional (Completion Handler)</text>

  <rect x="40" y="70" width="100" height="40" rx="5" ry="5" fill="#f0f0f0" stroke="#ccc"/>
  <text x="90" y="95" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">`dataTask(...)`</text>

  <path d="M140 90 L180 90" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <rect x="180" y="70" width="80" height="80" rx="5" ry="5" fill="#fff3e0" stroke="#fbc02d"/>
  <text x="220" y="105" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">Completion</text>
  <text x="220" y="125" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">Closure</text>

  <path d="M220 150 L220 170 C220 180 180 180 180 170 L180 150" stroke="#F04B3E" stroke-width="2" fill="none"/>
  <text x="220" y="180" font-family="Arial, sans-serif" font-size="12" text-anchor="middle" fill="#F04B3E">Error Path</text>


  <!-- Async/Await Side -->
  <rect x="320" y="20" width="260" height="180" rx="10" ry="10" stroke="#2A8367" stroke-width="2" fill="#e8f5e9"/>
  <text x="450" y="45" font-family="Arial, sans-serif" font-size="18" font-weight="bold" text-anchor="middle" fill="#2A8367">Modern (Async/Await)</text>

  <rect x="340" y="70" width="100" height="40" rx="5" ry="5" fill="#f0f0f0" stroke="#ccc"/>
  <text x="390" y="95" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">`data(from:)`</text>

  <path d="M440 90 L480 90" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <rect x="480" y="70" width="80" height="40" rx="5" ry="5" fill="#e8f5e9" stroke="#2A8367"/>
  <text x="520" y="95" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">`try await`</text>

  <path d="M520 110 L520 130 C520 140 480 140 480 130 L480 110" stroke="#F04B3E" stroke-width="2" fill="none"/>
  <text x="520" y="140" font-family="Arial, sans-serif" font-size="12" text-anchor="middle" fill="#F04B3E">Error Path</text>

  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
    </marker>
  </defs>
</svg>
</div>

## The Traditional Way: Completion Handlers

Before `async/await`, performing a network request with `URLSession` typically involved calling a method like `dataTask(with:completionHandler:)`. This method would immediately return a `URLSessionDataTask` instance, and the actual result (data, response, or error) would be delivered asynchronously to a closure you provided.

Here's a quick reminder of what that looked like:

```swift
func fetchPostsTraditional(completion: @escaping (Result<[Post], Error>) -> Void) {
    guard let url = URL(string: "https://jsonplaceholder.typicode.com/posts") else {
        completion(.failure(NetworkError.invalidURL))
        return
    }

    URLSession.shared.dataTask(with: url) { data, response, error in
        if let error = error {
            completion(.failure(error))
            return
        }

        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            completion(.failure(NetworkError.invalidResponse))
            return
        }

        guard let data = data else {
            completion(.failure(NetworkError.noData))
            return
        }

        do {
            let posts = try JSONDecoder().decode([Post].self, from: data)
            completion(.success(posts))
        } catch {
            completion(.failure(NetworkError.decodingError(error)))
        }
    }.resume() // Don't forget to resume the task!
}

// Example usage:
enum NetworkError: Error, LocalizedError {
    case invalidURL
    case invalidResponse
    case noData
    case decodingError(Error)

    var errorDescription: String? {
        switch self {
        case .invalidURL: return "The URL provided was invalid."
        case .invalidResponse: return "Received an invalid HTTP response."
        case .noData: return "No data was returned from the server."
        case .decodingError(let error): return "Failed to decode data: \(error.localizedDescription)"
        }
    }
}

struct Post: Decodable, Identifiable {
    let id: Int
    let title: String
    let body: String
}

// In a ViewController or ViewModel:
// fetchPostsTraditional { result in
//     switch result {
//     case .success(let posts):
//         print("Fetched \(posts.count) posts.")
//     case .failure(let error):
//         print("Error fetching posts: \(error.localizedDescription)")
//     }
// }
```

While functional, this approach often led to:
- **Callback Hell:** Deeply nested closures when chaining multiple asynchronous operations.
- **Error Handling Complexity:** Each layer of the callback chain needed its own error checks.
- **Readability Issues:** The flow of execution jumped around, making it harder to follow.
- **`resume()`:** Easy to forget to call `.resume()` on the `dataTask`.

## Embracing Modern Networking: `async/await`

Swift 5.5 introduced `async/await`, a powerful feature that allows you to write asynchronous code that looks and behaves like synchronous code. `URLSession` was quickly updated to provide `async/await`-native methods, making the traditional completion handlers largely obsolete for new code.

The key methods you'll now use are:
- `data(from: URL, delegate: URLSessionTaskDelegate?) async throws -> (Data, URLResponse)`: For fetching all data at once.
- `bytes(from: URL, delegate: URLSessionTaskDelegate?) async throws -> (URLSession.AsyncBytes, URLResponse)`: For streaming data, useful for large files or progressive downloads.

These methods are `async` because they perform work that might take time without blocking the current thread, and `throws` because they can fail, allowing you to use Swift's native `do-catch` error handling.

### Basic Data Fetching with `data(from:delegate:)`

Let's refactor our `fetchPosts` function using `async/await`:

```swift
func fetchPostsAsync() async throws -> [Post] {
    guard let url = URL(string: "https://jsonplaceholder.typicode.com/posts") else {
        throw NetworkError.invalidURL
    }

    // Perform the network request and await its result
    let (data, response) = try await URLSession.shared.data(from: url)

    // Type-cast the response and check status code
    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 200 else {
        throw NetworkError.invalidResponse
    }

    // Decode the data
    do {
        let posts = try JSONDecoder().decode([Post].self, from: data)
        return posts
    } catch {
        throw NetworkError.decodingError(error)
    }
}

// How to call it:
// This must be called from an async context, e.g., a Task
Task {
    do {
        let posts = try await fetchPostsAsync()
        print("Fetched \(posts.count) posts using async/await.")
        // Update UI on the main actor if needed
        // await MainActor.run {
        //     self.posts = posts
        // }
    } catch {
        print("Error fetching posts with async/await: \(error.localizedDescription)")
    }
}
```

Notice the immediate improvements:
- **Linear Flow:** The code reads from top to bottom, just like synchronous code. No more jumping into closures.
- **Explicit Error Handling:** `try await` clearly indicates a failable asynchronous operation, and `do-catch` handles errors naturally.
- **No `resume()`:** The task starts automatically.
- **Tuple Return:** The `data` and `response` are returned directly as a tuple, making them readily available.

### Handling Errors Gracefully

With `async/await`, error handling becomes much more straightforward. You use `do-catch` blocks, just as you would for any other throwing function. Defining custom error types, like our `NetworkError` enum, allows you to provide specific context for different failure scenarios.

```swift
enum NetworkError: Error, LocalizedError {
    case invalidURL
    case invalidResponse(statusCode: Int) // Added statusCode for more detail
    case noData
    case decodingError(Error)
    case unknown(Error)

    var errorDescription: String? {
        switch self {
        case .invalidURL: return "The URL provided was invalid."
        case .invalidResponse(let statusCode): return "Received an invalid HTTP response with status code \(statusCode)."
        case .noData: return "No data was returned from the server."
        case .decodingError(let error): return "Failed to decode data: \(error.localizedDescription)"
        case .unknown(let error): return "An unknown network error occurred: \(error.localizedDescription)"
        }
    }
}

// ... inside fetchPostsAsync
// ...
    guard let httpResponse = response as? HTTPURLResponse else {
        // If it's not an HTTPURLResponse, it's an unexpected response type
        throw NetworkError.invalidResponse(statusCode: -1) // Or a more specific error
    }
    guard httpResponse.statusCode == 200 else {
        throw NetworkError.invalidResponse(statusCode: httpResponse.statusCode)
    }
// ...
```

By providing more specific error cases, your app can react more intelligently to different failure conditions, offering better feedback to the user or logging more useful information for debugging.

## Beyond Basic Fetching: `bytes(from:delegate:)` for Streaming

For scenarios involving very large files or when you need to process data as it arrives (e.g., displaying download progress, parsing streaming data), `URLSession` offers `bytes(from:delegate:)`. This method returns an `URLSession.AsyncBytes` object, which conforms to `AsyncSequence`. This allows you to iterate over the incoming bytes using a `for await` loop.

```swift
func downloadLargeFile(url: URL) async throws -> Data {
    let (asyncBytes, response) = try await URLSession.shared.bytes(from: url)

    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 200 else {
        throw NetworkError.invalidResponse(statusCode: (response as? HTTPURLResponse)?.statusCode ?? -1)
    }

    var downloadedData = Data()
    var totalBytesReceived = 0
    let expectedContentLength = httpResponse.expectedContentLength // Can be -1 if not available

    print("Starting download for \(url.lastPathComponent), expected size: \(expectedContentLength > 0 ? "\(expectedContentLength) bytes" : "unknown")")

    for try await byte in asyncBytes {
        downloadedData.append(byte)
        totalBytesReceived += 1

        // Example: Update progress (ensure on MainActor for UI)
        if expectedContentLength > 0 {
            let progress = Double(totalBytesReceived) / Double(expectedContentLength)
            // print("Download progress: \(Int(progress * 100))%")
        }
    }
    print("Download complete. Received \(totalBytesReceived) bytes.")
    return downloadedData
}

// Example usage:
Task {
    if let largeFileUrl = URL(string: "https://speed.hetzner.de/100MB.bin") { // Example large file
        do {
            let fileData = try await downloadLargeFile(url: largeFileUrl)
            print("Successfully downloaded \(fileData.count) bytes.")
        } catch {
            print("Error downloading large file: \(error.localizedDescription)")
        }
    }
}
```

This `for await` loop makes processing streamed data incredibly elegant, eliminating the need for `URLSessionDelegate` methods like `urlSession(_:dataTask:didReceive:)` for simple streaming tasks.

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│ URLSession.bytes│──────►│ AsyncBytes      │──────►│ Process Chunk 1 │
│ (URL)           │       │ (AsyncSequence) │       │ (e.g., append)  │
└─────────────────┘       └─────────────────┘       └─────────────────┘
                                  │                       ▲
                                  ▼                       │
                               ┌─────────────────┐       │
                               │ Process Chunk 2 │───────┘
                               └─────────────────┘
```

## Configuring Your `URLSession`

While `URLSession.shared` is convenient, for most real-world applications, you'll want to create your own `URLSession` instance with specific configurations. This allows you to control aspects like caching policies, timeouts, and custom headers.

```swift
func createCustomURLSession() -> URLSession {
    let configuration = URLSessionConfiguration.default
    configuration.timeoutIntervalForRequest = 30.0 // 30 seconds
    configuration.timeoutIntervalForResource = 60.0 // 60 seconds for the entire resource
    configuration.httpAdditionalHeaders = ["User-Agent": "SwiftByRahulApp/1.0", "Accept": "application/json"]
    configuration.urlCache = URLCache(memoryCapacity: 4 * 1024 * 1024, diskCapacity: 20 * 1024 * 1024, diskPath: "SwiftByRahulCache") // 4MB memory, 20MB disk cache

    return URLSession(configuration: configuration)
}

// Then use it:
let customSession = createCustomURLSession()

func fetchUsers(session: URLSession) async throws -> [String] {
    guard let url = URL(string: "https://jsonplaceholder.typicode.com/users") else {
        throw NetworkError.invalidURL
    }
    let (data, response) = try await session.data(from: url)
    // ... process data and response ...
    return ["User 1", "User 2"] // Placeholder
}

Task {
    do {
        let users = try await fetchUsers(session: customSession)
        print("Fetched \(users.count) users with custom session.")
    } catch {
        print("Error fetching users with custom session: \(error.localizedDescription)")
    }
}
```

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Flow for creating and using a custom URLSession configuration.">
  <title>Custom URLSession Configuration Flow</title>
  
  <!-- Boxes -->
  <rect x="20" y="80" width="100" height="60" rx="5" ry="5" fill="#e3f2fd" stroke="#1565c0"/>
  <text x="70" y="115" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#1565c0">App Code</text>

  <rect x="180" y="20" width="150" height="180" rx="5" ry="5" fill="#fff3e0" stroke="#fbc02d"/>
  <text x="255" y="40" font-family="Arial, sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#fbc02d">URLSessionConfiguration</text>
  <text x="255" y="65" font-family="Arial, sans-serif" font-size="12" text-anchor="middle" fill="#333">.default</text>
  <text x="255" y="85" font-family="Arial, sans-serif" font-size="12" text-anchor="middle" fill="#333">.timeoutInterval</text>
  <text x="255" y="105" font-family="Arial, sans-serif" font-size="12" text-anchor="middle" fill="#333">.httpAdditionalHeaders</text>
  <text x="255" y="125" font-family="Arial, sans-serif" font-size="12" text-anchor="middle" fill="#333">.urlCache</text>
  <text x="255" y="145" font-family="Arial, sans-serif" font-size="12" text-anchor="middle" fill="#333">...</text>

  <rect x="390" y="80" width="100" height="60" rx="5" ry="5" fill="#e8f5e9" stroke="#2A8367"/>
  <text x="440" y="105" font-family="Arial, sans-serif" font-size="12" text-anchor="middle" fill="#2A8367">Custom</text>
  <text x="440" y="125" font-family="Arial, sans-serif" font-size="12" text-anchor="middle" fill="#2A8367">URLSession</text>

  <rect x="520" y="80" width="60" height="60" rx="5" ry="5" fill="#f0f0f0" stroke="#ccc"/>
  <text x="550" y="115" font-family="Arial, sans-serif" font-size="12" text-anchor="middle" fill="#333">Request</text>

  <!-- Arrows -->
  <path d="M120 110 L180 110" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <path d="M330 110 L390 110" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <path d="M490 110 L520 110" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  
  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
    </marker>
  </defs>
</svg>
</div>

## Concurrency and Parallel Requests

One of the most compelling advantages of `async/await` is how easily it enables concurrent operations. If you need to fetch multiple resources simultaneously, `async let` is your friend.

```swift
func fetchMultipleResources() async throws {
    let customSession = createCustomURLSession() // Reusing our custom session

    // Start both requests concurrently
    async let postsTask = fetchPostsAsync()
    async let usersTask = fetchUsers(session: customSession)

    // Await both results. This will suspend until both are complete.
    let posts = try await postsTask
    let users = try await usersTask

    print("Fetched \(posts.count) posts and \(users.count) users concurrently.")
}

Task {
    do {
        try await fetchMultipleResources()
    } catch {
        print("Error fetching multiple resources: \(error.localizedDescription)")
    }
}
```

With `async let`, Swift automatically manages the underlying tasks, ensuring that both `fetchPostsAsync()` and `fetchUsers()` run in parallel. The `try await` calls then wait for each result, making the concurrent logic incredibly clear. For more complex scenarios involving a dynamic number of tasks or stricter control over concurrency, `TaskGroup` offers even more power.

## Best Practices and Tips

To make the most of `URLSession` with `async/await`, consider these best practices:

1.  **Define Custom Error Types:** Use enums that conform to `Error` (and optionally `LocalizedError`) to provide clear, actionable error information.
2.  **Validate URLs Early:** Always check if a `URL` can be constructed from a string, especially if the string comes from an external source.
3.  **Update UI on the Main Actor:** Any code that modifies the UI must run on the `MainActor`. You can achieve this by marking your UI update functions with `@MainActor` or by wrapping UI updates in `await MainActor.run { ... }`.
4.  **Leverage Task Cancellation:** `URLSession`'s `async/await` methods are cancellation-aware. If the `Task` they are running in is cancelled, the underlying network request will also be cancelled. You should check for cancellation within long-running loops (e.g., in `bytes(from:)`) using `Task.checkCancellation()`.
5.  **Dependency Injection for `URLSession`:** For testability and flexibility, inject your `URLSession` instance into your networking layer rather than directly using `URLSession.shared`. This allows you to substitute a mock session during testing.
6.  **Secure Your Connections:** Always use HTTPS. `URLSession` respects App Transport Security (ATS) by default, which enforces secure connections.

## Summary

Swift's `async/await` has brought a breath of fresh air to networking with `URLSession`. The new `data(from:delegate:)` and `bytes(from:delegate:)` methods transform what was once a callback-ridden, error-prone process into a linear, readable, and robust experience. By embracing structured concurrency, you can write cleaner, more maintainable networking code that's easier to reason about and debug.

Modernizing your app's networking stack to use `async/await` is a highly recommended step that will pay dividends in code quality and developer experience.

Happy Swifting!
