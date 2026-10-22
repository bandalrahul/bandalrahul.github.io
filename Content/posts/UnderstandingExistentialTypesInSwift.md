---
title: Understanding Existential Types in Swift
date: 2026-10-22 14:15
description: Explore Swift's existential types using the 'any' keyword, their practical applications, performance implications, and how they differ from generics and opaque types.
tags: Swift, iOS, Programming
---

# Understanding Existential Types in Swift

Swift is a language that emphasizes type safety and performance. While we often work with concrete types like `String`, `Int`, or `UIViewController`, there are scenarios where we need to handle values whose specific type isn't known at compile time, but we *do* know they conform to a particular protocol. This is where **existential types** come into play.

If you've ever used `[someProtocol]` or just `someProtocol` (before Swift 5.6 where `any` became explicit), you've likely encountered existential types. They allow us to write flexible code that operates on values through their protocol conformance, abstracting away their underlying concrete types. This article will demystify existential types, explain when and how to use them, discuss their implications, and differentiate them from related Swift features like generics and opaque types.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Diagram showing an existential type as a container for different concrete types.">
  <title>Existential Type: A Container for Conforming Types</title>

  <!-- Existential Box -->
  <rect x="220" y="50" width="160" height="120" rx="10" ry="10" fill="#E0F2F1" stroke="#2A8367" stroke-width="2"/>
  <text x="300" y="85" font-family="Verdana" font-size="18" fill="#2A8367" text-anchor="middle">any Drawable</text>
  <text x="300" y="105" font-family="Verdana" font-size="12" fill="#666" text-anchor="middle">(Existential Container)</text>

  <!-- Concrete Type 1 -->
  <rect x="50" y="70" width="120" height="60" rx="5" ry="5" fill="#BBDEFB" stroke="#1565c0" stroke-width="1"/>
  <text x="110" y="105" font-family="Verdana" font-size="16" fill="#1565c0" text-anchor="middle">Circle</text>
  <line x1="170" y1="100" x2="220" y2="100" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowheadBlue)"/>

  <!-- Concrete Type 2 -->
  <rect x="430" y="70" width="120" height="60" rx="5" ry="5" fill="#BBDEFB" stroke="#1565c0" stroke-width="1"/>
  <text x="490" y="105" font-family="Verdana" font-size="16" fill="#1565c0" text-anchor="middle">Square</text>
  <line x1="380" y1="100" x2="430" y2="100" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowheadBlue)"/>

  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowheadBlue" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#1565c0" />
    </marker>
  </defs>
</svg>
</div>

## Protocols: The Foundation

Before diving into existentials, let's quickly recap protocols. In Swift, a protocol defines a blueprint of methods, properties, and other requirements that a class, struct, or enum can adopt. When a type adopts a protocol, it agrees to provide an implementation for all the requirements of that protocol.

```swift
protocol Drivable {
    var speed: Double { get set }
    func accelerate(by value: Double)
    func brake()
}

struct Car: Drivable {
    var speed: Double = 0.0
    func accelerate(by value: Double) {
        speed += value
        print("Car accelerating to \(speed) mph")
    }
    func brake() {
        speed = 0.0
        print("Car stopped")
    }
}

class Bicycle: Drivable {
    var speed: Double = 0.0
    func accelerate(by value: Double) {
        speed += value / 2 // Bicycles are slower
        print("Bicycle accelerating to \(speed) mph")
    }
    func brake() {
        speed = 0.0
        print("Bicycle stopped")
    }
}
```
Here, `Car` and `Bicycle` are two distinct concrete types, both conforming to `Drivable`.

## What Exactly is an Existential Type?

An existential type is a way to refer to *any* value whose type conforms to a given protocol, without knowing its specific underlying type. It's essentially a "box" that can hold a value of *any* type, as long as that type fulfills the requirements of the specified protocol.

In Swift 5.6 and later, you explicitly declare an existential type using the `any` keyword before the protocol name. For example, `any Drivable` means "a value of some type that conforms to `Drivable`."

Consider a scenario where you want a collection of `Drivable` objects, but you don't care if they are `Car`s, `Bicycle`s, or something else, as long as they can `accelerate` and `brake`.

```swift
let myCar = Car()
let myBicycle = Bicycle()

// An array of concrete types (not existential)
let vehicles: [Drivable] = [myCar, myBicycle] // Implicit 'any' conversion pre-Swift 5.6, explicit 'any Drivable' in Swift 5.6+

// Explicitly using 'any'
let anotherVehicle: any Drivable = Car()
let yetAnotherVehicle: any Drivable = Bicycle()

for vehicle in vehicles {
    vehicle.accelerate(by: 10.0)
    print("Current speed: \(vehicle.speed)")
}
```
Notice that `vehicles` is an array of `any Drivable`. Each element in the array is an existential container holding a value of a *specific* concrete type (`Car` or `Bicycle`), but when you access `vehicle` within the loop, its specific type is "erased" to `any Drivable`. You can only call methods and access properties defined by the `Drivable` protocol.

## The Box Metaphor

A good way to visualize an existential type is as a *box*. This box has a label on the outside indicating the protocol it holds (e.g., `any Drivable`). Inside the box, there's the actual concrete value (e.g., a `Car` instance or a `Bicycle` instance) and some metadata about its specific type.

When you interact with the box, you only see the protocol label. You can ask the box to perform actions defined by the protocol, but you can't ask it to do something specific to the `Car` type if it happens to contain a `Car` (unless you cast it back, which defeats some of the purpose of existentials).

```
┌──────────────────┐
│  Existential Box │
│ (e.g., any Shape)│
├──────────────────┤
│ Runtime Type Info│
│ (e.g., Circle)   │
├──────────────────┤
│ Concrete Value   │
│ (Circle instance)│
└──────────────────┘
```

This "boxing" mechanism is what enables existential types to hold values of different concrete types. However, this flexibility comes with a trade-off: runtime overhead.

## When to Use Existential Types

Existential types are powerful tools when flexibility and heterogeneity are more important than compile-time type specificity or absolute performance.

1.  **Heterogeneous Collections**: Storing a collection of objects that conform to the same protocol but are of different concrete types.
    ```swift
    protocol Drawable {
        func draw()
    }

    struct Circle: Drawable {
        let radius: Double
        func draw() { print("Drawing a circle with radius \(radius)") }
    }

    struct Square: Drawable {
        let side: Double
        func draw() { print("Drawing a square with side \(side)") }
    }

    let shapes: [any Drawable] = [Circle(radius: 5.0), Square(side: 10.0)]

    for shape in shapes {
        shape.draw() // Dynamically dispatches to Circle.draw() or Square.draw()
    }
    ```

2.  **API Flexibility**: When designing APIs where callers can provide any type conforming to a protocol, but the API itself doesn't need to be generic over that specific type.
    ```swift
    func process(item: any Equatable) {
        // You can compare 'item' with other 'Equatable' things,
        // but you don't know its concrete type at compile time.
        // let anotherItem: any Equatable = 5
        // if item == anotherItem { /* ... */ } // This would require item to be Self, not possible directly.
        // More on this limitation later.
    }
    ```
    (Note: `Equatable` itself has `Self` requirements which make it problematic for direct existential use. We'll explore this limitation in a moment.)

3.  **Dependency Inversion**: When a high-level module depends on an abstraction (protocol) rather than concrete implementations.
    ```swift
    protocol DataFetcher {
        func fetchData() async throws -> Data
    }

    class NetworkFetcher: DataFetcher {
        func fetchData() async throws -> Data {
            print("Fetching data from network...")
            return Data() // Simulate network call
        }
    }

    class MockFetcher: DataFetcher {
        func fetchData() async throws -> Data {
            print("Fetching data from mock...")
            return Data([0x01, 0x02]) // Simulate mock data
        }
    }

    // A view model that depends on 'any DataFetcher'
    class ViewModel {
        let fetcher: any DataFetcher

        init(fetcher: any DataFetcher) {
            self.fetcher = fetcher
        }

        func loadContent() async {
            do {
                let data = try await fetcher.fetchData()
                print("Data loaded: \(data.count) bytes")
            } catch {
                print("Failed to load data: \(error)")
            }
        }
    }

    let viewModel = ViewModel(fetcher: NetworkFetcher())
    // await viewModel.loadContent() // In a real async context

    let mockViewModel = ViewModel(fetcher: MockFetcher())
    // await mockViewModel.loadContent() // In a real async context
    ```
    This pattern is great for testing and swapping implementations without changing the `ViewModel` itself.

## Performance Considerations

The "box" metaphor isn't just an analogy; it's how existential types are often implemented under the hood. When you create an existential type, Swift needs to allocate memory for this box on the heap (if the concrete type's size is unknown or too large for stack allocation) and store the actual value inside it. This process is called **boxing**.

Additionally, when you call a method on an existential type (e.g., `vehicle.accelerate()`), Swift cannot know at compile time which specific `accelerate` implementation to call (`Car`'s or `Bicycle`'s). It has to look up the correct method at runtime using a **dynamic dispatch** mechanism (typically a vtable or witness table lookup).

Both boxing and dynamic dispatch introduce a small amount of overhead compared to direct calls on concrete types or statically dispatched generic code. For most applications, this overhead is negligible, but in highly performance-critical loops or algorithms, it can become a factor.

## Limitations of Existential Types

While flexible, existential types have some notable limitations:

1.  **Associated Types**: Protocols with associated types (PATs) cannot be used directly as existential types without the `any` keyword. With `any`, you can now use them, but the associated type remains opaque within the existential.
    ```swift
    protocol Container {
        associatedtype Item
        var items: [Item] { get }
    }

    struct IntContainer: Container {
        typealias Item = Int
        var items = [1, 2, 3]
    }

    // This is now allowed with 'any'
    let myContainer: any Container = IntContainer()
    // print(myContainer.items) // Error: Member 'items' cannot be used on value of type 'any Container'; its 'Self' constraint is not met
    // This happens because 'items' return type is `[Item]`, where `Item` is an associated type.
    // The compiler can't guarantee what `Item` is for an 'any Container'.
    ```
    To access `items`, you'd typically need to use generics or cast:
    ```swift
    func processContainer<T: Container>(container: T) {
        print(container.items) // Works with generics
    }
    processContainer(container: myContainer as! IntContainer) // Works with casting
    ```

2.  **`Self` or `Self`-like Requirements**: Protocols that require `Self` to be used in method signatures (e.g., `static func == (lhs: Self, rhs: Self)`) often make the protocol unusable as an existential type directly because the compiler can't guarantee that the `Self` types inside the box are the same.
    ```swift
    protocol MyComparable {
        func isSame(as other: Self) -> Bool
    }

    struct MyStruct: MyComparable {
        let id: Int
        func isSame(as other: MyStruct) -> Bool {
            return self.id == other.id
        }
    }

    let s1 = MyStruct(id: 1)
    let s2 = MyStruct(id: 2)

    // This won't compile:
    // let comparable: any MyComparable = s1
    // let anotherComparable: any MyComparable = s2
    // comparable.isSame(as: anotherComparable) // Error: Protocol 'MyComparable' can only be used as a generic constraint because it has Self or associated type requirements.

    // The explicit 'any' keyword in Swift 5.6+ makes this error more clear.
    // To work around this, you'd need to cast or use generics.
    ```
    The problem is that `comparable` and `anotherComparable` might be different concrete types at runtime, even if they both conform to `MyComparable`. The `isSame(as:)` method expects `other` to be of the *exact same concrete type* as `self` (`Self`). The existential `any MyComparable` erases this specific type information.

## Existentials vs. Generics vs. Opaque Types

These three concepts are often confused, but they serve distinct purposes:

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 800 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Comparison diagram of Existential Types, Generics, and Opaque Types in Swift.">
  <title>Existentials vs. Generics vs. Opaque Types</title>

  <!-- Headers -->
  <rect x="50" y="30" width="220" height="40" fill="#2A8367" rx="5" ry="5"/>
  <text x="160" y="55" font-family="Verdana" font-size="16" fill="white" text-anchor="middle">Existential Type (any P)</text>

  <rect x="290" y="30" width="220" height="40" fill="#1565c0" rx="5" ry="5"/>
  <text x="400" y="55" font-family="Verdana" font-size="16" fill="white" text-anchor="middle">Generics (<T: P>)</text>

  <rect x="530" y="30" width="220" height="40" fill="#F04B3E" rx="5" ry="5"/>
  <text x="640" y="55" font-family="Verdana" font-size="16" fill="white" text-anchor="middle">Opaque Type (some P)</text>

  <!-- Row 1: Type Identity -->
  <rect x="50" y="80" width="220" height="50" fill="#E0F2F1" stroke="#2A8367"/>
  <text x="160" y="100" font-family="Verdana" font-size="14" fill="#2A8367" text-anchor="middle">Type Erased (Known at Runtime)</text>
  <text x="160" y="118" font-family="Verdana" font-size="12" fill="#666" text-anchor="middle">Concrete type hidden from compiler</text>

  <rect x="290" y="80" width="220" height="50" fill="#BBDEFB" stroke="#1565c0"/>
  <text x="400" y="100" font-family="Verdana" font-size="14" fill="#1565c0" text-anchor="middle">Type Known (at Compile Time)</text>
  <text x="400" y="118" font-family="Verdana" font-size="12" fill="#666" text-anchor="middle">Specific type parameter</text>

  <rect x="530" y="80" width="220" height="50" fill="#FFCDD2" stroke="#F04B3E"/>
  <text x="640" y="100" font-family="Verdana" font-size="14" fill="#F04B3E" text-anchor="middle">Type Known (Compiler-Internal)</text>
  <text x="640" y="118" font-family="Verdana" font-size="12" fill="#666" text-anchor="middle">Specific type hidden from caller</text>

  <!-- Row 2: Performance -->
  <rect x="50" y="140" width="220" height="50" fill="#E0F2F1" stroke="#2A8367"/>
  <text x="160" y="165" font-family="Verdana" font-size="14" fill="#2A8367" text-anchor="middle">Runtime Overhead (Boxing, Dynamic Dispatch)</text>

  <rect x="290" y="140" width="220" height="50" fill="#BBDEFB" stroke="#1565c0"/>
  <text x="400" y="165" font-family="Verdana" font-size="14" fill="#1565c0" text-anchor="middle">Zero Overhead (Static Dispatch)</text>

  <rect x="530" y="140" width="220" height="50" fill="#FFCDD2" stroke="#F04B3E"/>
  <text x="640" y="165" font-family="Verdana" font-size="14" fill="#F04B3E" text-anchor="middle">Zero Overhead (Static Dispatch)</text>

  <!-- Row 3: Use Cases -->
  <rect x="50" y="200" width="220" height="60" fill="#E0F2F1" stroke="#2A8367"/>
  <text x="160" y="220" font-family="Verdana" font-size="14" fill="#2A8367" text-anchor="middle">Heterogeneous Collections,</text>
  <text x="160" y="238" font-family="Verdana" font-size="14" fill="#2A8367" text-anchor="middle">API Flexibility</text>

  <rect x="290" y="200" width="220" height="60" fill="#BBDEFB" stroke="#1565c0"/>
  <text x="400" y="220" font-family="Verdana" font-size="14" fill="#1565c0" text-anchor="middle">Compile-time Type Safety,</text>
  <text x="400" y="238" font-family="Verdana" font-size="14" fill="#1565c0" text-anchor="middle">Algorithms</text>

  <rect x="530" y="200" width="220" height="60" fill="#FFCDD2" stroke="#F04B3E"/>
  <text x="640" y="220" font-family="Verdana" font-size="14" fill="#F04B3E" text-anchor="middle">Module Boundaries,</text>
  <text x="640" y="238" font-family="Verdana" font-size="14" fill="#F04B3E" text-anchor="middle">Abstract Return Types</text>

</svg>
</div>

*   **Existential Types (`any P`)**:
    *   **What they are**: A value of *some* concrete type `T` where `T` conforms to protocol `P`. The specific type `T` is **erased** and only known at runtime.
    *   **When to use**: When you need to store or pass around values of different concrete types that share a common protocol interface. Ideal for heterogeneous collections.
    *   **Performance**: Involves runtime overhead due to boxing and dynamic dispatch.

*   **Generics (`<T: P>`)**:
    *   **What they are**: A placeholder type `T` that represents a *specific but unknown* concrete type that conforms to protocol `P`. The specific type `T` is **known at compile time**.
    *   **When to use**: When you need compile-time type safety and static dispatch, allowing the compiler to optimize code. Ideal for algorithms that work on a single, consistent type.
    *   **Performance**: Zero runtime overhead; performs static dispatch.

*   **Opaque Types (`some P`)**:
    *   **What they are**: A placeholder for a *specific, fixed concrete type* that conforms to protocol `P`. The specific type is **known by the compiler** but hidden from the caller. It's like a "reverse generic."
    *   **When to use**: Primarily for return types where a function wants to return a specific, concrete type that conforms to a protocol, but doesn't want to expose that concrete type to its callers. Commonly used in SwiftUI (`some View`).
    *   **Performance**: Zero runtime overhead; performs static dispatch.

The key takeaway is that `any P` means "I don't know the specific type, and I don't care, as long as it's a P." `some P` means "I know the specific type, but I'm not telling you what it is, just that it's a P." Generics mean "I'm going to work with a specific type `T` that conforms to `P`, and you, the caller, will tell me what `T` is."

## The `any` Keyword (Swift 5.6+)

Before Swift 5.6, using a protocol name as a type (e.g., `let item: Drivable`) implicitly created an existential type. This implicit behavior sometimes led to confusion, especially with protocols that couldn't actually be used as existentials due to `Self` or associated type requirements.

The introduction of the `any` keyword in Swift 5.6 made existential types explicit. Now, if you want a value to be an existential, you write `any ProtocolName`. If you try to use a protocol with `Self` or associated type requirements as a type without `any`, the compiler will guide you towards using generics or explicitly acknowledge the existential behavior with `any`. This clarity helps developers understand when they are opting into the runtime characteristics of existential types.

## Practical Example: A Drawing App

Let's combine these concepts into a simple drawing application example.

```swift
// 1. Define a protocol for drawable objects
protocol Drawable {
    var id: UUID { get }
    func draw(in context: String) // Simulate drawing to a canvas context
    mutating func move(byX deltaX: Double, byY deltaY: Double)
}

// 2. Create concrete types conforming to Drawable
struct Point: Drawable {
    let id = UUID()
    var x: Double
    var y: Double

    func draw(in context: String) {
        print("Drawing Point(\(x), \(y)) in \(context)")
    }

    mutating func move(byX deltaX: Double, byY deltaY: Double) {
        x += deltaX
        y += deltaY
    }
}

struct Line: Drawable {
    let id = UUID()
    var start: Point
    var end: Point

    func draw(in context: String) {
        print("Drawing Line from \(start.x),\(start.y) to \(end.x),\(end.y) in \(context)")
    }

    mutating func move(byX deltaX: Double, byY deltaY: Double) {
        start.move(byX: deltaX, byY: deltaY)
        end.move(byX: deltaX, byY: deltaY)
    }
}

struct Rectangle: Drawable {
    let id = UUID()
    var origin: Point
    var width: Double
    var height: Double

    func draw(in context: String) {
        print("Drawing Rectangle at (\(origin.x),\(origin.y)) with size \(width)x\(height) in \(context)")
    }

    mutating func move(byX deltaX: Double, byY deltaY: Double) {
        origin.move(byX: deltaX, byY: deltaY)
    }
}

// 3. Create a Canvas that holds a collection of any Drawable
struct Canvas {
    var drawables: [any Drawable] = []

    mutating func add(_ drawable: any Drawable) {
        drawables.append(drawable)
    }

    func render() {
        print("\n--- Rendering Canvas ---")
        for drawable in drawables {
            drawable.draw(in: "Screen Context")
        }
        print("------------------------\n")
    }

    mutating func moveAll(byX deltaX: Double, byY deltaY: Double) {
        for i in drawables.indices {
            drawables[i].move(byX: deltaX, byY: deltaY)
        }
    }
}

// 4. Usage
var myCanvas = Canvas()

var p1 = Point(x: 10, y: 20)
var l1 = Line(start: Point(x: 0, y: 0), end: Point(x: 50, y: 50))
var r1 = Rectangle(origin: Point(x: 100, y: 100), width: 75, height: 25)

myCanvas.add(p1)
myCanvas.add(l1)
myCanvas.add(r1)

myCanvas.render()

// Move all elements
myCanvas.moveAll(byX: 5, byY: 5)
myCanvas.render()
```
In this example, `myCanvas.drawables` is an array of existential types `[any Drawable]`. The `Canvas` doesn't need to know the specific type of each `Drawable` it holds; it just knows they all conform to `Drawable` and can respond to `draw()` and `move()` calls. This demonstrates the power of existentials for creating flexible, heterogeneous collections.

## Summary

Existential types in Swift, explicitly marked with `any`, provide a powerful mechanism for writing flexible code that operates on values conforming to a protocol without knowing their concrete types at compile time. They are ideal for heterogeneous collections, flexible API designs, and dependency inversion. However, this flexibility comes with potential runtime overhead (boxing and dynamic dispatch) and limitations concerning protocols with `Self` or associated type requirements. Understanding when to choose existentials over generics or opaque types is key to writing efficient and maintainable Swift code.

Happy Swifting!
