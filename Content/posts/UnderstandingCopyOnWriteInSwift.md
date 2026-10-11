---
title: Understanding Copy-on-Write in Swift
date: 2026-10-11 15:13
description: Explore Swift's Copy-on-Write (CoW) optimization for value types like Array, Dictionary, and String, and learn how to implement custom CoW for your own types.
tags: Swift, iOS, Programming
---

# Understanding Copy-on-Write in Swift

Swift is a language that strongly encourages the use of value types, such as `struct`s and `enum`s. They offer significant benefits like predictable behavior, thread safety, and easier reasoning about your code. However, working with large value types can sometimes introduce performance overhead, especially when they are copied. This is where **Copy-on-Write (CoW)** comes to the rescue.

CoW is a clever optimization technique that Swift uses extensively for its built-in collection types (`Array`, `Dictionary`, `Set`) and `String`. It allows these value types to behave like reference types when they are merely copied, only performing a true, deep copy of their underlying storage when a modification is actually made. This article will dive deep into how CoW works, why it's beneficial, and how you can implement it for your own custom types.

## The Performance Challenge with Large Value Types

Imagine you have a `struct` that encapsulates a significant amount of data, perhaps a large image buffer or a complex data model.

```swift
struct ImageData {
    var pixels: [UInt8] // Imagine this array holds millions of bytes
    var width: Int
    var height: Int

    init(width: Int, height: Int) {
        self.width = width
        self.height = height
        self.pixels = Array(repeating: 0, count: width * height * 4) // 4 bytes per pixel (RGBA)
    }

    mutating func invertColors() {
        for i in 0..<pixels.count {
            pixels[i] = 255 - pixels[i]
        }
    }
}

// Create a large image data instance
var originalImage = ImageData(width: 1920, height: 1080)
```

Now, consider what happens when you "copy" this `originalImage`:

```swift
var copiedImage = originalImage // This assignment performs a full copy
```

Because `ImageData` is a `struct` (a value type), Swift's default behavior is to make a complete, member-wise copy of `originalImage` into `copiedImage`. If `pixels` contains millions of bytes, this means allocating new memory and copying all those bytes, even if `copiedImage` is never modified. This can be a significant performance hit if such copies happen frequently, leading to unnecessary memory allocations and CPU cycles.

This is the problem Copy-on-Write aims to solve: delaying the expensive copy operation until it's absolutely necessary.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Comparison of Value Type Copying without and with Copy-on-Write">
  <title>Comparison of Value Type Copying without and with Copy-on-Write</title>

  <!-- Title for the diagram -->
  <text x="300" y="20" font-family="Arial, sans-serif" font-size="18" font-weight="bold" text-anchor="middle" fill="#333">Value Type Copying: Without CoW vs. With CoW</text>

  <!-- Without CoW Section -->
  <rect x="30" y="40" width="260" height="160" rx="8" ry="8" fill="#F0F0F0" stroke="#ccc" stroke-width="1"/>
  <text x="160" y="60" font-family="Arial, sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#333">Without Copy-on-Write</text>

  <rect x="50" y="80" width="100" height="40" rx="5" ry="5" fill="#1565c0" stroke="#1565c0" stroke-width="1"/>
  <text x="100" y="105" font-family="Arial, sans-serif" font-size="12" fill="white" text-anchor="middle">var A</text>
  <rect x="180" y="80" width="90" height="40" rx="5" ry="5" fill="#E0E0E0" stroke="#ccc" stroke-width="1"/>
  <text x="225" y="105" font-family="Arial, sans-serif" font-size="12" fill="#333" text-anchor="middle">Data Block 1</text>
  <line x1="150" y1="100" x2="180" y2="100" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowhead)"/>

  <rect x="50" y="140" width="100" height="40" rx="5" ry="5" fill="#F04B3E" stroke="#F04B3E" stroke-width="1"/>
  <text x="100" y="165" font-family="Arial, sans-serif" font-size="12" fill="white" text-anchor="middle">var B = A</text>
  <rect x="180" y="140" width="90" height="40" rx="5" ry="5" fill="#F0E0E0" stroke="#ccc" stroke-width="1"/>
  <text x="225" y="165" font-family="Arial, sans-serif" font-size="12" fill="#333" text-anchor="middle">Data Block 2</text>
  <line x1="150" y1="160" x2="180" y2="160" stroke="#F04B3E" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="160" y="127" font-family="Arial, sans-serif" font-size="10" fill="#F04B3E" text-anchor="middle">Deep Copy!</text>

  <!-- With CoW Section -->
  <rect x="310" y="40" width="260" height="160" rx="8" ry="8" fill="#F0F0F0" stroke="#ccc" stroke-width="1"/>
  <text x="440" y="60" font-family="Arial, sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#333">With Copy-on-Write</text>

  <rect x="330" y="80" width="100" height="40" rx="5" ry="5" fill="#1565c0" stroke="#1565c0" stroke-width="1"/>
  <text x="380" y="105" font-family="Arial, sans-serif" font-size="12" fill="white" text-anchor="middle">var A</text>
  <rect x="460" y="90" width="90" height="40" rx="5" ry="5" fill="#E0E0E0" stroke="#ccc" stroke-width="1"/>
  <text x="505" y="115" font-family="Arial, sans-serif" font-size="12" fill="#333" text-anchor="middle">Data Block X</text>
  <line x1="430" y1="100" x2="460" y2="100" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowhead)"/>

  <rect x="330" y="140" width="100" height="40" rx="5" ry="5" fill="#2A8367" stroke="#2A8367" stroke-width="1"/>
  <text x="380" y="165" font-family="Arial, sans-serif" font-size="12" fill="white" text-anchor="middle">var B = A</text>
  <line x1="430" y1="160" x2="460" y2="120" stroke="#2A8367" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="440" y="140" font-family="Arial, sans-serif" font-size="10" fill="#2A8367" text-anchor="middle">Shared Ref</text>

  <text x="440" y="185" font-family="Arial, sans-serif" font-size="10" fill="#F04B3E" text-anchor="middle">(Copy only on modification)</text>


  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
    </marker>
  </defs>
</svg>
</div>

## How Copy-on-Write Works in Swift

Swift's CoW implementation leverages the distinction between value types (structs, enums) and reference types (classes). While your `Array`, `Dictionary`, `Set`, or `String` are value types, their *internal storage* is often managed by a private, heap-allocated class instance (a reference type).

Here's the mechanism:

1.  **Initial Assignment (Copying)**: When you assign one CoW-enabled value type instance to another (e.g., `var newArray = originalArray`), Swift does *not* immediately create a deep copy of the underlying data. Instead, both `originalArray` and `newArray` now internally point to the *same* class instance that holds the actual data. Swift's runtime keeps track of how many references point to this shared storage.

2.  **Modification (Copy Trigger)**: If you then try to *modify* either `originalArray` or `newArray`, Swift performs a check. It asks: "Is this internal storage currently referenced by more than one variable?"
    *   **If Yes (Not Uniquely Referenced)**: A new, independent copy of the underlying storage is created. The variable attempting the modification is then updated to point to this new copy. The modification is applied to this new copy, leaving the original shared storage untouched for the other variable(s). This is the "copy-on-write" step.
    *   **If No (Uniquely Referenced)**: If the internal storage is only referenced by the variable attempting the modification, no copy is needed. The modification is applied directly to the existing storage. This is an optimization that avoids unnecessary copying.

This strategy means that the expensive deep copy operation only occurs when it's truly needed – when a value type instance is modified while it's still being shared. If you copy a value type and never modify it, or if you modify it but it's not shared, you pay no performance penalty for the copy.

## Illustrating CoW with Swift's Built-in Types

Let's use `Array` to see CoW in action. While we can't directly observe the internal storage, we can infer its behavior.

```swift
var numbers = [1, 2, 3, 4, 5]
print("Original numbers: \(numbers)") // Output: Original numbers: [1, 2, 3, 4, 5]

// 'copiedNumbers' now shares the same internal storage as 'numbers'
// No deep copy of the elements has occurred yet.
var copiedNumbers = numbers
print("Copied numbers (before modification): \(copiedNumbers)") // Output: Copied numbers (before modification): [1, 2, 3, 4, 5]

// Now, modify 'copiedNumbers'.
// At this point, Swift detects that 'numbers' also refers to the same storage.
// Therefore, a *copy* of the underlying storage is made for 'copiedNumbers'.
// The modification then applies to this new, independent storage.
copiedNumbers[0] = 100
print("Copied numbers (after modification): \(copiedNumbers)") // Output: Copied numbers (after modification): [100, 2, 3, 4, 5]

// 'numbers' remains unchanged because 'copiedNumbers' now has its own copy.
print("Original numbers (after copiedNumbers modification): \(numbers)") // Output: Original numbers (after copiedNumbers modification): [1, 2, 3, 4, 5]
```

If we were to modify `numbers` *after* `copiedNumbers` was modified, `numbers` would also trigger a copy if it was still sharing. But in this case, `copiedNumbers` already has its own copy, so `numbers` remains uniquely referenced to its *original* copy.

```
Initial State:
┌───────────┐    ┌─────────────┐
│  numbers  │───▶│ [1, 2, 3, 4, 5] │
└───────────┘    └─────────────┘

After `copiedNumbers = numbers`:
┌───────────┐    ┌─────────────┐
│  numbers  │───▶│ [1, 2, 3, 4, 5] │
├───────────┤    ▲─────────────┘
│copiedNumbers│───┘
└───────────┘
  (Shared Storage)

After `copiedNumbers[0] = 100` (CoW triggered):
┌───────────┐    ┌─────────────┐
│  numbers  │───▶│ [1, 2, 3, 4, 5] │
└───────────┘    └─────────────┘

┌───────────┐    ┌─────────────┐
│copiedNumbers│───▶│ [100, 2, 3, 4, 5] │
└───────────┘    └─────────────┘
  (Separate Storage)
```

This ASCII diagram clearly illustrates how the shared storage is broken when a modification occurs, ensuring value semantics are preserved without unnecessary early copying.

## Performance Implications of Copy-on-Write

CoW is a powerful optimization, but it's important to understand its performance characteristics:

*   **Benefit**: Reduced memory allocation and copying overhead. If you copy a large collection and never modify it, or modify it only when it's not shared, you get the performance of reference semantics (just copying a pointer) while retaining the safety and predictability of value semantics.
*   **Cost**:
    *   **Reference Counting Overhead**: Swift's runtime needs to track the number of references to the internal storage. This adds a small overhead to each assignment and deallocation.
    *   **Uniqueness Check Overhead**: Before modification, a check (`isKnownUniquelyReferenced`) is performed.
    *   **Copy Penalty**: If a modification *does* trigger a copy, you pay the full price of a deep copy at that moment. This can be less predictable than always copying immediately.

For most common use cases with `Array`, `Dictionary`, `Set`, and `String`, the benefits of CoW far outweigh these costs. Swift's standard library implementations are highly optimized.

## Implementing Custom Copy-on-Write for Your Own Types

While Swift provides CoW for its built-in collections, you might have custom value types that manage large amounts of data and could benefit from this optimization. For instance, our `ImageData` struct from earlier.

To implement custom CoW, you'll typically follow this pattern:

1.  **Create a Reference Type (Class) for Storage**: This class will hold the actual mutable data.
2.  **Create a Value Type (Struct) as the Public API**: This struct will wrap an instance of your storage class.
3.  **Use `isKnownUniquelyReferenced(_:)`**: Inside the struct's mutating methods or computed properties, check if the wrapped storage class instance is uniquely referenced. If not, create a new copy of the storage before applying changes.

Let's refactor our `ImageData` struct to use CoW:

```swift
// 1. Reference Type for Storage
final class ImageDataStorage {
    var pixels: [UInt8]
    let width: Int
    let height: Int

    init(width: Int, height: Int) {
        self.width = width
        self.height = height
        self.pixels = Array(repeating: 0, count: width * height * 4)
    }

    // A convenience initializer for copying existing storage
    init(copying storage: ImageDataStorage) {
        self.width = storage.width
        self.height = storage.height
        self.pixels = storage.pixels // Deep copy of the array elements
    }
}

// 2. Value Type as the Public API
struct CoWImageData {
    private var storage: ImageDataStorage // Holds a reference to the storage class

    init(width: Int, height: Int) {
        self.storage = ImageDataStorage(width: width, height: height)
    }

    // Private method to ensure unique storage before modification
    private mutating func ensureUniqueStorage() {
        if !isKnownUniquelyReferenced(&storage) {
            // If not unique, create a new copy of the storage
            storage = ImageDataStorage(copying: storage)
            print("--- CoW triggered: Made a new copy of ImageDataStorage ---")
        } else {
            print("--- Storage is unique: Modifying in place ---")
        }
    }

    // Public properties and methods that trigger CoW on write
    var width: Int { storage.width }
    var height: Int { storage.height }

    subscript(index: Int) -> UInt8 {
        get {
            precondition(index >= 0 && index < storage.pixels.count, "Index out of bounds")
            return storage.pixels[index]
        }
        set {
            precondition(index >= 0 && index < storage.pixels.count, "Index out of bounds")
            ensureUniqueStorage() // Check for uniqueness before modification
            storage.pixels[index] = newValue
        }
    }

    mutating func invertColors() {
        ensureUniqueStorage() // Check for uniqueness before modification
        for i in 0..<storage.pixels.count {
            storage.pixels[i] = 255 - storage.pixels[i]
        }
    }
}
```

Let's test our custom `CoWImageData`:

```swift
print("--- Creating original image ---")
var originalCoWImage = CoWImageData(width: 10, height: 10) // Small for demo
originalCoWImage[0] = 50 // Storage is unique, modify in place
print("OriginalCoWImage[0]: \(originalCoWImage[0])")

print("\n--- Copying original image ---")
var copiedCoWImage = originalCoWImage // Shares storage with originalCoWImage
print("CopiedCoWImage[0] (before modification): \(copiedCoWImage[0])")

print("\n--- Modifying copied image ---")
// This will trigger CoW because 'originalCoWImage' also points to the same storage
copiedCoWImage[0] = 150
print("CopiedCoWImage[0] (after modification): \(copiedCoWImage[0])")
print("OriginalCoWImage[0] (after copiedCoWImage modification): \(originalCoWImage[0])") // Remains 50

print("\n--- Modifying original image (now unique) ---")
originalCoWImage[1] = 200 // Storage is now unique, modify in place
print("OriginalCoWImage[1]: \(originalCoWImage[1])")
```

**Output:**

```
--- Creating original image ---
--- Storage is unique: Modifying in place ---
OriginalCoWImage[0]: 50

--- Copying original image ---
CopiedCoWImage[0] (before modification): 50

--- Modifying copied image ---
--- CoW triggered: Made a new copy of ImageDataStorage ---
CopiedCoWImage[0] (after modification): 150
OriginalCoWImage[0] (after copiedCoWImage modification): 50

--- Modifying original image (now unique) ---
--- Storage is unique: Modifying in place ---
OriginalCoWImage[1]: 200
```

This output clearly demonstrates `ensureUniqueStorage()` and `isKnownUniquelyReferenced` at work, triggering a copy only when necessary.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 280" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Custom Copy-on-Write Implementation Flow Diagram">
  <title>Custom Copy-on-Write Implementation Flow Diagram</title>

  <!-- Title -->
  <text x="300" y="20" font-family="Arial, sans-serif" font-size="18" font-weight="bold" text-anchor="middle" fill="#333">Custom Copy-on-Write Flow</text>

  <!-- MyCoWStruct Box -->
  <rect x="50" y="50" width="150" height="60" rx="8" ry="8" fill="#1565c0" stroke="#1565c0" stroke-width="1"/>
  <text x="125" y="75" font-family="Arial, sans-serif" font-size="14" fill="white" text-anchor="middle">MyCoWStruct</text>
  <text x="125" y="95" font-family="Arial, sans-serif" font-size="12" fill="white" text-anchor="middle">(Value Type)</text>

  <!-- StorageClass Box -->
  <rect x="400" y="50" width="150" height="60" rx="8" ry="8" fill="#E0E0E0" stroke="#ccc" stroke-width="1"/>
  <text x="475" y="75" font-family="Arial, sans-serif" font-size="14" fill="#333" text-anchor="middle">StorageClass</text>
  <text x="475" y="95" font-family="Arial, sans-serif" font-size="12" fill="#333" text-anchor="middle">(Reference Type)</text>

  <!-- Arrow from Struct to Class -->
  <line x1="200" y1="80" x2="400" y2="80" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="300" y="70" font-family="Arial, sans-serif" font-size="10" fill="#333" text-anchor="middle">Holds reference to</text>

  <!-- Modification Flow -->
  <rect x="50" y="140" width="150" height="40" rx="5" ry="5" fill="#F0F0F0" stroke="#ccc" stroke-width="1"/>
  <text x="125" y="165" font-family="Arial, sans-serif" font-size="12" fill="#333" text-anchor="middle">Attempt to Modify</text>

  <line x1="125" y1="180" x2="125" y2="200" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>

  <!-- Decision Diamond -->
  <polygon points="125,200 175,225 125,250 75,225" fill="#F0F0F0" stroke="#ccc" stroke-width="1"/>
  <text x="125" y="228" font-family="Arial, sans-serif" font-size="12" fill="#333" text-anchor="middle">`isKnownUniquelyReferenced`?</text>

  <!-- True Path (Green) -->
  <line x1="175" y1="225" x2="270" y2="225" stroke="#2A8367" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="225" y="215" font-family="Arial, sans-serif" font-size="10" fill="#2A8367" text-anchor="middle">YES</text>
  <rect x="270" y="205" width="150" height="40" rx="5" ry="5" fill="#2A8367" stroke="#2A8367" stroke-width="1"/>
  <text x="345" y="230" font-family="Arial, sans-serif" font-size="12" fill="white" text-anchor="middle">Modify Storage Directly</text>

  <!-- False Path (Red) -->
  <line x1="125" y1="250" x2="125" y2="270" stroke="#F04B3E" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="100" y="260" font-family="Arial, sans-serif" font-size="10" fill="#F04B3E" text-anchor="middle">NO</text>
  <rect x="20" y="270" width="210" height="40" rx="5" ry="5" fill="#F04B3E" stroke="#F04B3E" stroke-width="1"/>
  <text x="125" y="295" font-family="Arial, sans-serif" font-size="12" fill="white" text-anchor="middle">Create New Storage Copy & Modify</text>

  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
    </marker>
  </defs>
</svg>
</div>

## When to Use (and Not Use) Custom CoW

Implementing custom CoW adds complexity to your code, so it's not a universal solution.

**You should consider implementing custom CoW when:**

*   **Your value type wraps a large amount of data:** The cost of copying this data directly is significant.
*   **Copies of your value type are frequent:** If your type is passed around, assigned, or stored in collections often.
*   **Modifications after copying are relatively infrequent:** The `CoW` mechanism shines when copies are common, but modifications are rare or happen only when the instance is no longer shared.
*   **You need strict value semantics:** You want your type to behave like a struct, where each instance is independent, but you need the performance optimization of deferred copying.

**Avoid implementing custom CoW when:**

*   **Your value type is small and cheap to copy:** The overhead of `isKnownUniquelyReferenced` and the indirection through a class might outweigh the benefits.
*   **Modifications after copying are *always* expected:** If every copy of your type is immediately modified, you'll always incur the copy cost, plus the CoW overhead. In such cases, a simple struct or even a class might be more straightforward.
*   **You actually desire reference semantics:** If multiple variables *should* refer to the same mutable data and see each other's changes, then a `class` is the appropriate choice.

## Summary

Copy-on-Write is a fundamental optimization in Swift that allows value types like `Array`, `Dictionary`, `Set`, and `String` to offer excellent performance for large data structures while maintaining their predictable value semantics. By delaying expensive deep copy operations until a modification occurs on a shared instance, CoW strikes a balance between performance and correctness.

For your own custom large value types, you can implement CoW using a private class for storage and the `isKnownUniquelyReferenced(_:)` function. However, always weigh the benefits against the added complexity and overhead to ensure it's the right solution for your specific performance needs.

Happy Swifting!
