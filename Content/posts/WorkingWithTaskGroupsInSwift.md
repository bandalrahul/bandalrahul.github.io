---
title: Working with Task Groups in Swift
date: 2026-07-05 10:59
description: Learn how Swift's Task Groups enable dynamic, structured concurrency for a variable number of asynchronous operations, handling errors and cancellation effectively.
tags: Swift, Concurrency, iOS
---

# Working with Task Groups in Swift

Swift's structured concurrency, introduced with `async/await`, has revolutionized how we write asynchronous code. While `async let` provides a fantastic way to run a fixed number of tasks concurrently, what if the number of tasks you need to perform isn't known until runtime? This is where `TaskGroup` comes into play.

`TaskGroup` offers a powerful mechanism for managing a dynamic number of child tasks, ensuring that their lifecycle, error propagation, and cancellation are handled in a structured and predictable manner. If you're an intermediate iOS developer comfortable with `async/await`, you're ready to unlock the full potential of `TaskGroup` to build more robust and efficient concurrent applications.

## `async let` vs. `TaskGroup`: Choosing the Right Tool

Before diving into `TaskGroup`, let's quickly recap `async let` to understand when each is most appropriate.

`async let` is perfect when you know exactly how many independent asynchronous operations you need to perform and you want to run them in parallel.

```swift
func fetchUserData() async throws -> User { /* ... */ }
func fetchUserFriends() async throws -> [Friend] { /* ... */ }
func fetchUserPhotos() async throws -> [Photo] { /* ... */ }

func loadUserProfile() async throws -> UserProfile {
    async let user = fetchUserData()
    async let friends = fetchUserFriends()
    async let photos = fetchUserPhotos()

    // These `await` calls will wait for their respective tasks to complete
    // and collect their results.
    return UserProfile(user: await user, friends: await friends, photos: await photos)
}
```

In this example, we always fetch three distinct pieces of data. `async let` clearly expresses this fixed parallelism.

However, imagine a scenario where you need to process a list of items, but the list's size varies. Or perhaps you're fetching data from multiple URLs, and the number of URLs is determined at runtime. This is where `TaskGroup` shines. It allows you to dynamically spawn child tasks within a defined scope and collect their results as they complete.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Comparison between async let and TaskGroup for structured concurrency">
  <title>async let vs TaskGroup Comparison</title>

  <!-- async let section -->
  <rect x="50" y="20" width="200" height="30" fill="#1565c0" rx="5" ry="5"/>
  <text x="150" y="40" font-family="Arial" font-size="14" fill="white" text-anchor="middle">async let</text>

  <rect x="50" y="70" width="80" height="40" fill="#E0E0E0" stroke="#999" stroke-width="1"/>
  <text x="90" y="95" font-family="Arial" font-size="12" text-anchor="middle">Task A</text>
  <rect x="170" y="70" width="80" height="40" fill="#E0E0E0" stroke="#999" stroke-width="1"/>
  <text x="210" y="95" font-family="Arial" font-size="12" text-anchor="middle">Task B</text>

  <line x1="90" y1="120" x2="90" y2="150" stroke="#999" stroke-width="2" marker-end="url(#arrowhead)"/>
  <line x1="210" y1="120" x2="210" y2="150" stroke="#999" stroke-width="2" marker-end="url(#arrowhead)"/>

  <rect x="100" y="150" width="100" height="40" fill="#D0D0D0" stroke="#999" stroke-width="1"/>
  <text x="150" y="175" font-family="Arial" font-size="12" text-anchor="middle">Await All</text>

  <!-- TaskGroup section -->
  <rect x="350" y="20" width="200" height="30" fill="#2A8367" rx="5" ry="5"/>
  <text x="450" y="40" font-family="Arial" font-size="14" fill="white" text-anchor="middle">TaskGroup</text>

  <rect x="350" y="70" width="80" height="40" fill="#E0E0E0" stroke="#999" stroke-width="1"/>
  <text x="390" y="95" font-family="Arial" font-size="12" text-anchor="middle">Task 1</text>
  <rect x="440" y="70" width="80" height="40" fill="#E0E0E0" stroke="#999" stroke-width="1"/>
  <text x="480" y="95" font-family="Arial" font-size="12" text-anchor="middle">Task 2</text>
  <rect x="530" y="70" width="20" height="40" fill="#E0E0E0" stroke="#999" stroke-width="1"/>
  <text x="540" y="95" font-family="Arial" font-size="12" text-anchor="middle">...</text>

  <line x1="390" y1="120" x2="390" y2="150" stroke="#999" stroke-width="2" marker-end="url(#arrowhead)"/>
  <line x1="480" y1="120" x2="480" y2="150" stroke="#999" stroke-width="2" marker-end="url(#arrowhead)"/>
  <line x1="540" y1="120" x2="540" y2="150" stroke="#999" stroke-width="2" marker-end="url(#arrowhead)"/>

  <rect x="380" y="150" width="140" height="40" fill="#D0D0D0" stroke="#999" stroke-width="1"/>
  <text x="450" y="175" font-family="Arial" font-size="12" text-anchor="middle">Collect Results (for await)</text>

  <!-- Arrows -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#999" />
    </marker>
  </defs>

  <text x="150" y="205" font-family="Arial" font-size="12" text-anchor="middle" fill="#1565c0">Fixed number of tasks</text>
  <text x="450" y="205" font-family="Arial" font-size="12" text-anchor="middle" fill="#2A8367">Dynamic number of tasks</text>
</svg>
</div>

## Understanding `TaskGroup` Basics

A `TaskGroup` provides a way to create a collection of child tasks that are executed concurrently. These tasks are part of the current task's structured concurrency hierarchy, meaning their cancellation and lifecycle are tied to the parent task.

The primary way to create and interact with a `TaskGroup` is using the `withTaskGroup(of:returning:body:)` function.

```swift
func withTaskGroup<ChildTaskResult, GroupResult>(
    of: ChildTaskResult.Type,
    returning: GroupResult.Type = GroupResult.self,
    body: (inout TaskGroup<ChildTaskResult>) async throws -> GroupResult
) async rethrows -> GroupResult
```

Let's break down the parameters:
*   `of: ChildTaskResult.Type`: Specifies the type of result that each child task in the group will produce.
*   `returning: GroupResult.Type`: Specifies the type of result that the `withTaskGroup` closure itself will return.
*   `body`: An `async throws` closure where you add child tasks to the group and collect their results. The `TaskGroup` instance is passed as an `inout` parameter.

Inside the `body` closure, you interact with the `TaskGroup` instance:
1.  **Adding Tasks**: Use `group.addTask { ... }` to add new child tasks. Each `addTask` call takes an `async` closure that returns a `ChildTaskResult`.
2.  **Collecting Results**: Use a `for await let result in group { ... }` loop to iterate over the results of the child tasks as they complete. This is similar to how you'd iterate over an `AsyncSequence`.
3.  **Error Handling**: If any child task throws an error, the `await` on the `for await` loop (or the final `return` from the `body` closure if no `for await` loop is used) will rethrow that error.
4.  **Cancellation**: If the parent task (the one calling `withTaskGroup`) is cancelled, all child tasks within the group are automatically cancelled. You can also explicitly cancel all tasks in a group using `group.cancelAll()`.

### A Simple Example

Let's say we want to download a series of files concurrently and aggregate their sizes.

```swift
enum DownloadError: Error {
    case invalidURL
    case networkError(Error)
    case dataCorrupted
}

func downloadFile(url: URL) async throws -> Int {
    guard url.isFileURL else { // Simplified check, real download would be complex
        throw DownloadError.invalidURL
    }
    print("Downloading \(url.lastPathComponent)...")
    try await Task.sleep(for: .seconds(Double.random(in: 0.5...2.0))) // Simulate network delay
    let fileSize = Int.random(in: 1_000_000...10_000_000) // Simulate file size
    print("Finished downloading \(url.lastPathComponent), size: \(fileSize) bytes.")
    return fileSize
}

func downloadMultipleFiles(urls: [URL]) async throws -> [Int] {
    var fileSizes: [Int] = []

    try await withTaskGroup(of: Int.self) { group in
        for url in urls {
            group.addTask {
                do {
                    return try await downloadFile(url: url)
                } catch {
                    print("Error downloading \(url.lastPathComponent): \(error.localizedDescription)")
                    // Rethrow if you want the group to fail, or return a default/nil
                    throw error
                }
            }
        }

        // Collect results as they complete
        for await size in group {
            fileSizes.append(size)
        }
    }
    return fileSizes
}

// Usage:
@main
struct TaskGroupApp {
    static func main() async {
        let fileURLs = [
            URL(fileURLWithPath: "/tmp/file1.txt"),
            URL(fileURLWithPath: "/tmp/image.png"),
            URL(fileURLWithPath: "/tmp/document.pdf"),
            URL(fileURLWithPath: "/tmp/video.mp4")
        ]

        print("Starting file downloads...")
        do {
            let sizes = try await downloadMultipleFiles(urls: fileURLs)
            let totalSize = sizes.reduce(0, +)
            print("All downloads complete. Total size: \(totalSize) bytes.")
            print("Individual file sizes: \(sizes)")
        } catch {
            print("An error occurred during downloads: \(error.localizedDescription)")
        }
    }
}
```

In this example, the `downloadMultipleFiles` function takes an array of URLs. Inside `withTaskGroup`, it iterates through the URLs, adding a `downloadFile` task for each. The `for await size in group` loop then collects the results of these tasks as they finish, without waiting for all of them to complete before collecting the first result.

```
┌───────────────────────────────────┐
│       downloadMultipleFiles()     │
│ ┌───────────────────────────────┐ │
│ │  withTaskGroup(of: Int.self)  │ │
│ │                               │ │
│ │  ┌──────────────┐             │ │
│ │  │  addTask {   │             │ │
│ │  │    downloadFile(url1)       │─ ─ ─ ─ ─ ─ ─ ─ ─┐
│ │  └──────────────┘             │ │               │
│ │  ┌──────────────┐             │ │               │
│ │  │  addTask {   │             │ │               │
│ │  │    downloadFile(url2)       │─ ─ ─ ─ ─ ─ ─ ─ ─┼─┐
│ │  └──────────────┘             │ │               │ │
│ │  ┌──────────────┐             │ │               │ │
│ │  │  addTask {   │             │ │               │ │
│ │  │    downloadFile(url3)       │─ ─ ─ ─ ─ ─ ─ ─ ─┼─┼─┐
│ │  └──────────────┘             │ │               │ │ │
│ │             ...               │ │               │ │ │
│ │                               ▼ │               │ │ │
│ │  ┌───────────────────────────┐ │               │ │ │
│ │  │  for await size in group  │◄────────────────┘ │ │
│ │  │    fileSizes.append(size) │                   │ │
│ │  └───────────────────────────┘                   │ │
│ └───────────────────────────────┘                   │ │
│                ▼                                    │ │
│           return fileSizes ◄────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

The ASCII diagram illustrates the flow: `downloadMultipleFiles` initiates a `TaskGroup`. Inside the group, multiple `addTask` calls create concurrent `downloadFile` tasks. These tasks run in parallel. The `for await size in group` loop then asynchronously collects the results from these tasks as they complete, allowing `fileSizes` to be populated. Finally, `fileSizes` is returned.

## Practical Example: Processing a Batch of Images

Let's consider a common scenario in iOS development: processing a dynamic batch of images, perhaps applying a filter or resizing them, and then uploading the results. Each image processing step might be time-consuming, making concurrency essential.

```swift
import UIKit // For UIImage

enum ImageProcessingError: Error, LocalizedError {
    case invalidImageData
    case processingFailed
    case uploadFailed(Int) // Associate with original index for better debugging

    var errorDescription: String? {
        switch self {
        case .invalidImageData: return "The provided image data was invalid."
        case .processingFailed: return "Image processing operation failed."
        case .uploadFailed(let index): return "Failed to upload image at index \(index)."
        }
    }
}

struct ProcessedImage {
    let originalIndex: Int
    let data: Data
    let size: CGSize
}

// Simulate a network service for uploading
class ImageUploader {
    func uploadImage(data: Data, originalIndex: Int) async throws -> String {
        print("Uploading image \(originalIndex) (\(data.count) bytes)...")
        try await Task.sleep(for: .seconds(Double.random(in: 1.0...3.0))) // Simulate upload time
        if Bool.random() && originalIndex == 1 { // Simulate a random failure for image at index 1
            throw ImageProcessingError.uploadFailed(originalIndex)
        }
        let uploadURL = "https://example.com/uploads/image-\(UUID().uuidString).jpg"
        print("Image \(originalIndex) uploaded to: \(uploadURL)")
        return uploadURL
    }
}

// Simulate image processing
func processImage(data: Data, originalIndex: Int) async throws -> ProcessedImage {
    guard let image = UIImage(data: data) else {
        throw ImageProcessingError.invalidImageData
    }

    print("Processing image \(originalIndex) (original size: \(image.size))...")
    // Simulate resizing or applying a filter
    try await Task.sleep(for: .seconds(Double.random(in: 0.8...2.5)))

    // Example: simple resizing (not production quality)
    let newSize = CGSize(width: image.size.width * 0.5, height: image.size.height * 0.5)
    UIGraphicsBeginImageContextWithOptions(newSize, false, 1.0)
    image.draw(in: CGRect(origin: .zero, size: newSize))
    let resizedImage = UIGraphicsGetImageFromCurrentImageContext()
    UIGraphicsEndImageContext()

    guard let processedData = resizedImage?.jpegData(compressionQuality: 0.8) else {
        throw ImageProcessingError.processingFailed
    }

    print("Finished processing image \(originalIndex) (new size: \(newSize)).")
    return ProcessedImage(originalIndex: originalIndex, data: processedData, size: newSize)
}

func processAndUploadImages(imageDatas: [Data], uploader: ImageUploader) async throws -> [String] {
    var uploadedURLs: [String] = []

    try await withTaskGroup(of: String.self) { group in
        for (index, imageData) in imageDatas.enumerated() {
            group.addTask {
                do {
                    // Step 1: Process the image
                    let processedImage = try await processImage(data: imageData, originalIndex: index)
                    // Step 2: Upload the processed image
                    let url = try await uploader.uploadImage(data: processedImage.data, originalIndex: processedImage.originalIndex)
                    return url
                } catch {
                    print("Task for image \(index) failed: \(error.localizedDescription)")
                    // If any task fails, we rethrow it. The parent task will then catch it.
                    // Alternatively, you could return a special error string or nil to continue processing.
                    throw error
                }
            }
        }

        // Collect all uploaded URLs
        for await url in group {
            uploadedURLs.append(url)
        }
    }
    return uploadedURLs
}

// Simulating usage in an iOS app context
class ImageProcessorViewModel {
    let uploader = ImageUploader()

    func startProcessing(images: [UIImage]) async {
        let imageDatas = images.compactMap { $0.jpegData(compressionQuality: 0.9) }
        guard !imageDatas.isEmpty else {
            print("No valid image data to process.")
            return
        }

        print("Starting batch image processing and upload...")
        do {
            let urls = try await processAndUploadImages(imageDatas: imageDatas, uploader: uploader)
            print("Successfully uploaded \(urls.count) images:")
            urls.forEach { print("- \($0)") }
        } catch {
            print("Batch processing failed: \(error.localizedDescription)")
            // Handle specific errors, e.g., show an alert
            if let processingError = error as? ImageProcessingError {
                print("Specific error: \(processingError.errorDescription ?? "Unknown")")
            }
        }
    }
}

// Example of how you'd call this from a ViewController or similar:
/*
// In a real app, 'imagePickerResults' would come from UIImagePickerController
let sampleImages: [UIImage] = [
    UIImage(systemName: "photo.fill")!,
    UIImage(systemName: "camera.fill")!,
    UIImage(systemName: "video.fill")!,
    UIImage(systemName: "mic.fill")!
]

let viewModel = ImageProcessorViewModel()
Task {
    await viewModel.startProcessing(images: sampleImages)
}
*/
```

This example demonstrates a more complex workflow. Each child task within the `TaskGroup` performs two sequential asynchronous operations: image processing and then image uploading. If either of these steps fails for a given image, the `catch` block prints an error and rethrows, causing the entire `withTaskGroup` block to throw, which is then handled by the `ImageProcessorViewModel`.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 280" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Flow diagram of processing and uploading multiple images using a TaskGroup">
  <title>Image Processing and Upload Flow with TaskGroup</title>

  <!-- Start -->
  <rect x="20" y="20" width="100" height="40" fill="#1565c0" rx="5" ry="5"/>
  <text x="70" y="45" font-family="Arial" font-size="12" fill="white" text-anchor="middle">Input Images</text>

  <!-- TaskGroup -->
  <rect x="150" y="20" width="120" height="40" fill="#2A8367" rx="5" ry="5"/>
  <text x="210" y="45" font-family="Arial" font-size="12" fill="white" text-anchor="middle">TaskGroup (Parent)</text>

  <!-- Add Task Loop -->
  <rect x="290" y="20" width="150" height="40" fill="#E0E0E0" stroke="#999" stroke-width="1"/>
  <text x="365" y="45" font-family="Arial" font-size="12" text-anchor="middle">Loop: `group.addTask { ... }`</text>

  <!-- Individual Task Flow -->
  <rect x="290" y="80" width="150" height="40" fill="#E0E0E0" stroke="#999" stroke-width="1"/>
  <text x="365" y="105" font-family="Arial" font-size="12" text-anchor="middle">Child Task (Image 1)</text>

  <rect x="290" y="130" width="150" height="40" fill="#E0E0E0" stroke="#999" stroke-width="1"/>
  <text x="365" y="155" font-family="Arial" font-size="12" text-anchor="middle">Child Task (Image 2)</text>

  <rect x="290" y="180" width="150" height="20" fill="#E0E0E0" stroke="#999" stroke-width="1"/>
  <text x="365" y="195" font-family="Arial" font-size="12" text-anchor="middle">...</text>

  <rect x="470" y="80" width="100" height="40" fill="#D0D0D0" stroke="#999" stroke-width="1"/>
  <text x="520" y="105" font-family="Arial" font-size="12" text-anchor="middle">Process Image</text>

  <rect x="470" y="130" width="100" height="40" fill="#D0D0D0" stroke="#999" stroke-width="1"/>
  <text x="520" y="155" font-family="Arial" font-size="12" text-anchor="middle">Upload Image</text>

  <!-- Error Path -->
  <rect x="470" y="200" width="100" height="40" fill="#F04B3E" rx="5" ry="5"/>
  <text x="520" y="225" font-family="Arial" font-size="12" fill="white" text-anchor="middle">Error</text>

  <!-- Collect Results -->
  <rect x="150" y="220" width="120" height="40" fill="#D0D0D0" stroke="#999" stroke-width="1"/>
  <text x="210" y="245" font-family="Arial" font-size="12" text-anchor="middle">Collect Results</text>

  <!-- End -->
  <rect x="20" y="220" width="100" height="40" fill="#1565c0" rx="5" ry="5"/>
  <text x="70" y="245" font-family="Arial" font-size="12" fill="white" text-anchor="middle">Uploaded URLs</text>

  <!-- Arrows -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#999" />
    </marker>
  </defs>

  <line x1="120" y1="40" x2="150" y2="40" stroke="#999" stroke-width="2" marker-end="url(#arrowhead)"/>
  <line x1="270" y1="40" x2="290" y2="40" stroke="#999" stroke-width="2" marker-end="url(#arrowhead)"/>

  <line x1="365" y1="60" x2="365" y2="80" stroke="#999" stroke-width="2" marker-end="url(#arrowhead)"/>
  <line x1="365" y1="120" x2="365" y2="130" stroke="#999" stroke-width="2" marker-end="url(#arrowhead)"/>
  <line x1="365" y1="170" x2="365" y2="180" stroke="#999" stroke-width="2" marker-end="url(#arrowhead)"/>

  <!-- Parallel processing -->
  <line x1="440" y1="100" x2="470" y2="100" stroke="#999" stroke-width="2" marker-end="url(#arrowhead)"/>
  <line x1="520" y1="120" x2="520" y2="130" stroke="#999" stroke-width="2" marker-end="url(#arrowhead)"/>
  <line x1="520" y1="170" x2="520" y2="200" stroke="#999" stroke-width="2" marker-end="url(#arrowhead)"/>

  <!-- Results back to group -->
  <line x1="470" y1="150" x2="290" y2="150" stroke="#999" stroke-width="2"/>
  <line x1="290" y1="150" x2="270" y2="230" stroke="#999" stroke-width="2" marker-end="url(#arrowhead)"/>

  <!-- Error path -->
  <line x1="520" y1="240" x2="290" y2="240" stroke="#999" stroke-width="2"/>
  <line x1="290" y1="240" x2="270" y2="230" stroke="#999" stroke-width="2" marker-end="url(#arrowhead)"/>

  <line x1="150" y1="240" x2="120" y2="240" stroke="#999" stroke-width="2" marker-end="url(#arrowhead)"/>
</svg>
</div>

The diagram illustrates that `Input Images` go into the `TaskGroup`. Inside the group, a loop adds `Child Tasks` for each image. Each child task performs `Process Image` then `Upload Image`. If an `Error` occurs, it's propagated. Finally, the group `Collects Results` (uploaded URLs) which are then returned.

## `TaskGroup` Best Practices

1.  **Define `ChildTaskResult` Carefully**: The `ChildTaskResult` type of the `TaskGroup` should represent the outcome of a *single* child task. If a child task can fail, you might want to return an `Result<Value, Error>` or an optional `Value?` from the `addTask` closure, and then explicitly handle the success/failure when collecting results. If you don't catch errors within `addTask`, a throwing child task will cause the entire `withTaskGroup` block to rethrow the first error encountered.
2.  **Handle Cancellation**: `TaskGroup`s are designed for structured concurrency. If the parent task is cancelled, all child tasks within the group are automatically cancelled. You can also explicitly cancel all child tasks with `group.cancelAll()`. Inside child tasks, check `Task.isCancelled` or `Task.checkCancellation()` if your operation is long-running and needs to respond to cancellation proactively.
3.  **Avoid Retain Cycles**: Just like with regular closures, be mindful of retain cycles when capturing `self` or other objects in `addTask` closures. Use `[weak self]` or `[unowned self]` as appropriate.
4.  **Balance Concurrency**: While `TaskGroup` allows for immense parallelism, be aware of system resources. Spawning too many tasks that perform CPU-intensive or I/O-intensive work simultaneously can degrade performance rather than improve it due to contention. Swift's concurrency runtime manages the number of concurrent tasks, but it's still good practice to consider the nature of your tasks.
5.  **Error Propagation**: By default, `withTaskGroup` rethrows the *first* error encountered by any child task. If you need to collect *all* errors or ensure all tasks run to completion even if some fail, you must catch errors within each `addTask` block and return an `Result` type or a custom type that can represent both success and failure.

## Summary

`TaskGroup` is an indispensable tool in Swift's structured concurrency toolkit, empowering you to manage a dynamic number of concurrent tasks with robust error handling and cancellation. While `async let` is suitable for a fixed set of parallel operations, `TaskGroup` excels when the number of concurrent tasks is determined at runtime, making it ideal for scenarios like batch processing, dynamic data fetching, and more. By understanding its mechanics and applying best practices, you can build highly efficient and resilient asynchronous features in your Swift applications.

Happy Swifting!
