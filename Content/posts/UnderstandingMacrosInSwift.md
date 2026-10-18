---
title: Understanding Macros in Swift
date: 2026-10-18 12:54
description: Dive deep into Swift Macros, exploring their types, how they transform code at compile time, and practical use cases for reducing boilerplate.
tags: Swift, iOS, Programming
---

# Understanding Macros in Swift

Swift Macros, introduced in Swift 5.9, represent a significant evolution in how developers can generate and transform code. While many developers might be familiar with the basic concept of macros in other languages, Swift's implementation offers a safe, type-checked, and powerful way to reduce boilerplate and create highly expressive APIs without sacrificing compiler guarantees.

This article goes beyond a basic introduction, aiming to provide a deeper understanding of how Swift Macros work under the hood, their different forms, and how they integrate into the Swift compilation process. If you've ever found yourself writing repetitive code or wishing Swift had a feature that could generate code for you, understanding macros is your next step.

At its core, a Swift Macro is a piece of code that runs at compile time to transform your source code. It takes your existing Swift code as input and produces new or modified Swift code as output, which is then compiled alongside the rest of your project. This compile-time code generation is incredibly powerful for automating repetitive tasks and building domain-specific language features.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Swift Macro Transformation Flow">
  <title>Swift Macro Transformation Flow</title>
  <style>
    .box { fill: #1565c0; stroke: #1565c0; stroke-width: 2; rx: 8; ry: 8; }
    .arrow { stroke: #2A8367; stroke-width: 2; marker-end: url(#arrowhead); }
    .text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 16px; fill: white; text-anchor: middle; dominant-baseline: middle; }
    .label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 14px; fill: #333; text-anchor: middle; dominant-baseline: middle; }
  </style>
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#2A8367" />
    </marker>
  </defs>

  <!-- Source Code Box -->
  <rect x="50" y="70" width="150" height="80" class="box" />
  <text x="125" y="110" class="text">Source Code</text>
  <text x="125" y="170" class="label">Contains Macro Call</text>

  <!-- Arrow to Macro Expansion -->
  <line x1="200" y1="110" x2="270" y2="110" class="arrow" />
  <text x="235" y="90" class="label">Compile Time</text>

  <!-- Macro Expansion Box -->
  <rect x="270" y="70" width="150" height="80" class="box" />
  <text x="345" y="110" class="text">Macro Expansion</text>
  <text x="345" y="170" class="label">Generates Code</text>

  <!-- Arrow to Transformed Code -->
  <line x1="420" y1="110" x2="490" y2="110" class="arrow" />
  <text x="455" y="90" class="label">Result</text>

  <!-- Transformed Code Box -->
  <rect x="490" y="70" width="150" height="80" class="box" />
  <text x="565" y="110" class="text">Transformed Code</text>
  <text x="565" y="170" class="label">Ready for Compilation</text>
</svg>
</div>

## Types of Swift Macros

Swift Macros are categorized into two main groups: **Freestanding Macros** and **Attached Macros**. Each serves different purposes and operates on different parts of your code.

### Freestanding Macros

Freestanding macros are invoked like global functions or declarations using a `#` prefix. They stand alone and are not attached to any specific declaration.

#### Expression Macros (`#expression`)

These macros are used to generate an expression. They take arguments and return a single expression. A common example is `#stringify`, which takes an expression and returns a tuple containing the string representation of the expression and its evaluated value.

```swift
// Macro definition (conceptual, actual definition is in a plugin)
@freestanding(expression)
public macro stringify<T>(_ value: T) -> (T, String) = #externalMacro(module: "MyMacros", type: "StringifyMacro")

// Usage
func exampleStringify() {
    let x = 10
    let y = 20
    let (result, source) = #stringify(x + y * 2)
    print("The value \(result) was produced from the expression `\(source)`")
    // Expected output: "The value 50 was produced from the expression `x + y * 2`"
}
```

In this example, `#stringify(x + y * 2)` is expanded at compile time into something like `(x + y * 2, "x + y * 2")`. The magic is that the macro can inspect the *source code* of its argument.

#### Declaration Macros (`#declaration`)

Declaration macros are used to generate new declarations (e.g., new structs, classes, enums, functions, or properties). They are less common than expression macros but can be incredibly powerful for generating entire blocks of code.

```swift
// Macro definition (conceptual)
@freestanding(declaration)
public macro defineStruct<T: StringProtocol>(named: T) = #externalMacro(module: "MyMacros", type: "StructDefinitionMacro")

// Usage
#defineStruct(named: "Point")
// This macro would expand to something like:
// struct Point {
//     var x: Double
//     var y: Double
// }
```

### Attached Macros

Attached macros are applied to an existing declaration using an `@` prefix, similar to property wrappers or attribute declarations. They can modify, add to, or inspect the declaration they are attached to. There are several kinds of attached macros:

#### Peer Macros (`@peer`)

Peer macros add new sibling declarations alongside the declaration they are attached to. This is useful for generating associated types, helper functions, or other related declarations.

```swift
// Macro definition (conceptual)
@attached(peer)
public macro AddHashable() = #externalMacro(module: "MyMacros", type: "AddHashableMacro")

// Usage
@AddHashable
struct MyStruct {
    let id: UUID
    let name: String
}
// This macro could expand to add `extension MyStruct: Hashable { ... }` as a peer.
```

#### Member Macros (`@member`)

Member macros add new members (properties, methods, initializers) *inside* the declaration they are attached to. This is perfect for boilerplate code that every instance of a type needs.

```swift
// Macro definition (conceptual)
@attached(member, names: named(init))
public macro DefaultInit() = #externalMacro(module: "MyMacros", type: "DefaultInitMacro")

// Usage
@DefaultInit
struct User {
    let id: UUID
    var name: String
    var email: String
}
// Expands to add:
// init(id: UUID, name: String, email: String) {
//     self.id = id
//     self.name = name
//     self.email = email
// }
```

#### Member Attribute Macros (`@memberAttribute`)

These macros add attributes to the members of the declaration they are attached to. For example, you could add `@Observable` to all stored properties of a class.

```swift
// Macro definition (conceptual)
@attached(memberAttribute)
public macro ObservableProperties() = #externalMacro(module: "MyMacros", type: "ObservablePropertiesMacro")

// Usage
@ObservableProperties
class MyViewModel {
    var title: String = "Hello" // This would get @Observable added
    var count: Int = 0          // This would get @Observable added
}
```

#### Accessor Macros (`@accessor`)

Accessor macros add accessors (getters and setters) to a property. This is highly specialized and often used for implementing features like copy-on-write or custom storage.

```swift
// Macro definition (conceptual)
@attached(accessor)
public macro CopyOnWrite() = #externalMacro(module: "MyMacros", type: "CopyOnWriteMacro")

// Usage
struct MyValue {
    @CopyOnWrite var data: [Int] = []
}
// Expands to add custom get/set accessors for `data` that implement CoW logic.
```

#### Extension Macros (`@extension`)

Extension macros add new extensions to the type they are attached to, allowing you to conform the type to new protocols or add new functionality.

```swift
// Macro definition (conceptual)
@attached(extension, conformances: Decodable, Encodable)
public macro Codable() = #externalMacro(module: "MyMacros", type: "CodableMacro")

// Usage
@Codable
struct Product {
    let id: String
    let name: String
    let price: Double
}
// Expands to add `extension Product: Decodable { ... }` and `extension Product: Encodable { ... }`.
```

## How Macros Work: The Two-Phase Compilation

Understanding macros requires a look into the Swift compilation process. Unlike C/C++ preprocessor macros, which are textual substitutions, Swift Macros are deeply integrated with the compiler's syntax tree and perform type-checked transformations. This process occurs in two distinct phases:

1.  **Macro Expansion Phase**: When the Swift compiler encounters a macro, it doesn't immediately compile it. Instead, it invokes the associated macro *plugin*. The plugin, written in Swift using the `SwiftSyntax` library, takes the source code of the macro invocation and its arguments (represented as a syntax tree) and produces new or transformed Swift source code (also as a syntax tree). This expanded code is then returned to the compiler.
2.  **Compilation Phase**: After all macros have been expanded, the compiler proceeds with its regular compilation, treating the expanded code as if it were originally written by the developer. This includes type-checking, optimization, and code generation.

This two-phase approach ensures that the code generated by macros is just as safe and performant as manually written Swift code. The `SwiftSyntax` library is crucial here; it allows macro authors to parse, inspect, and generate Swift source code programmatically.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 250" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Swift Macro Compilation Flow">
  <title>Swift Macro Compilation Flow</title>
  <style>
    .box { fill: #1565c0; stroke: #1565c0; stroke-width: 2; rx: 8; ry: 8; }
    .compiler-box { fill: #2A8367; stroke: #2A8367; stroke-width: 2; rx: 8; ry: 8; }
    .red-box { fill: #F04B3E; stroke: #F04B3E; stroke-width: 2; rx: 8; ry: 8; }
    .arrow { stroke: #2A8367; stroke-width: 2; marker-end: url(#arrowhead); }
    .text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 16px; fill: white; text-anchor: middle; dominant-baseline: middle; }
    .label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 14px; fill: #333; text-anchor: middle; dominant-baseline: middle; }
  </style>
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#2A8367" />
    </marker>
  </defs>

  <!-- Developer Writes Code -->
  <rect x="20" y="30" width="120" height="60" class="box" />
  <text x="80" y="60" class="text">Source Code</text>
  <text x="80" y="100" class="label">with Macro Calls</text>

  <!-- Arrow to Compiler -->
  <line x1="140" y1="60" x2="190" y2="60" class="arrow" />

  <!-- Swift Compiler -->
  <rect x="190" y="30" width="120" height="60" class="compiler-box" />
  <text x="250" y="60" class="text">Swift Compiler</text>
  <text x="250" y="100" class="label">Detects Macro</text>

  <!-- Arrow to Macro Plugin -->
  <line x1="310" y1="60" x2="360" y2="60" class="arrow" />
  <text x="335" y="40" class="label">Invokes</text>

  <!-- Macro Plugin -->
  <rect x="360" y="30" width="120" height="60" class="red-box" />
  <text x="420" y="60" class="text">Macro Plugin</text>
  <text x="420" y="100" class="label">(SwiftSyntax)</text>

  <!-- Arrow back to Compiler -->
  <line x1="480" y1="60" x2="530" y2="60" class="arrow" />
  <text x="505" y="40" class="label">Returns</text>

  <!-- Expanded Code -->
  <rect x="530" y="30" width="120" height="60" class="box" />
  <text x="590" y="60" class="text">Expanded Code</text>
  <text x="590" y="100" class="label">to Compiler</text>

  <!-- Second compilation phase -->
  <line x1="320" y1="150" x2="320" y2="180" class="arrow" />
  <text x="320" y="130" class="label">Final</text>

  <!-- Final Compilation -->
  <rect x="260" y="180" width="120" height="60" class="compiler-box" />
  <text x="320" y="210" class="text">Swift Compiler</text>
  <text x="320" y="240" class="label">Compiles Expanded Code</text>
</svg>
</div>

## Macro Implementation and Project Structure

A key aspect of "understanding" macros is realizing that the macro definition (what you write in your main app target) and its *implementation* (the code that performs the transformation) live in separate modules. The implementation resides in a special Swift Package Manager (SPM) target called a "macro plugin."

This separation is crucial:
*   The macro plugin is executed by the compiler, not linked into your app.
*   It uses `SwiftSyntax` to analyze and generate code.
*   Your app target only sees the *definition* of the macro and its public interface.

Here’s a simplified view of a project structure using macros:

```
MyProject/
├── Sources/
│   ├── MyApp/
│   │   └── MyApp.swift         // Uses the macro
│   └── MyMacros/
│       ├── MyMacros.swift      // Contains macro declarations (e.g., #stringify)
│       └── MyMacrosPlugin/
│           └── Plugin.swift    // Contains macro implementations (SwiftSyntax code)
├── Tests/
│   └── MyMacrosTests/
│       └── MyMacrosTests.swift // Tests for the macro implementation
└── Package.swift               // Defines the macro package and plugin
```

The `MyMacros.swift` file in the `MyMacros` target would contain the `@freestanding(expression) public macro stringify<T>(...)` declaration. The actual logic for transforming `_ value: T` into `(T, String)` would be in `Plugin.swift` within the `MyMacrosPlugin` target.

## Practical Use Cases and Benefits

Macros excel at solving problems where repetitive code patterns are common, or where a domain-specific language (DSL) would greatly enhance readability and safety.

*   **Boilerplate Reduction**: Automatically synthesize `Codable`, `Hashable`, `Equatable`, or `Identifiable` conformance for complex types, or generate common initializers, logging methods, or property observers.
*   **Domain-Specific Languages (DSLs)**: Create custom syntax that feels native to Swift for specific domains, like UI layout, networking definitions, or data modeling. The `Observation` framework's `@Observable` macro is a prime example.
*   **Compile-Time Verification**: Enforce constraints or generate warnings/errors at compile time based on code structure, catching issues before runtime.
*   **Cross-Platform Abstractions**: Generate platform-specific code from a single, high-level declaration.
*   **Performance Optimizations**: Generate specialized code paths for different scenarios that would be cumbersome to write manually.

## Considerations and Best Practices

While powerful, macros should be used judiciously:

*   **Readability and Debugging**: Macro-generated code can sometimes be harder to debug if not well-understood. Xcode's "Expand Macro" feature is invaluable here.
*   **Complexity**: Writing macro implementations with `SwiftSyntax` can be complex. Start with simple transformations.
*   **Discoverability**: Well-documented macros are essential. Make it clear what code a macro generates.
*   **Testing**: Macro implementations should be thoroughly unit tested to ensure they generate the correct code for various inputs.

Macros are not a replacement for good API design or Swift's existing features like generics, protocols, or property wrappers. Instead, they complement these features by providing a mechanism to generate the boilerplate *around* them, making your code cleaner and more expressive.

## Summary

Swift Macros empower developers to perform compile-time code transformations, significantly reducing boilerplate and enabling new levels of expressiveness in Swift. By understanding the distinction between freestanding and attached macros, their various forms (expression, declaration, peer, member, accessor, extension), and the two-phase compilation process, you can leverage this powerful feature effectively. Remember that macro definitions and their `SwiftSyntax`-based implementations live in separate modules, a design choice that ensures safety and flexibility. When used thoughtfully, macros can elevate your Swift code to be more concise, maintainable, and robust.

Happy Swifting!
