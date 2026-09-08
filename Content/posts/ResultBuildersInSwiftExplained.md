---
title: Result Builders in Swift Explained
date: 2026-09-08 13:12
description: Discover Swift Result Builders, a powerful feature for creating declarative DSLs, simplifying complex view constructions, and enhancing code readability beyond SwiftUI.
tags: Swift, iOS, Programming
---

# Result Builders in Swift Explained

If you've spent any time with SwiftUI, you've undoubtedly encountered `@ViewBuilder`. This seemingly magical attribute allows you to write declarative UI code, combining multiple views, conditional logic, and loops into a single, cohesive block. But `@ViewBuilder` isn't a special SwiftUI-only construct; it's an instance of a powerful Swift language feature called **Result Builders**.

Result Builders, introduced in Swift 5.4, provide a way to construct complex data structures incrementally using a declarative, domain-specific syntax. They transform a sequence of expressions within a closure into a single, cohesive result. Think of them as a compiler-supported way to build mini-DSLs (Domain-Specific Languages) right within your Swift code, making it more readable and expressive.

In this article, we'll peel back the layers of Result Builders, understand how they work, and learn how to create our own custom builders for various scenarios beyond just UI.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Before and After Result Builders">
  <title>Before and After Result Builders</title>
  <!-- Background rect -->
  <rect x="0" y="0" width="600" height="220" fill="#f9f9f9" rx="10"/>

  <!-- Before Section -->
  <text x="150" y="30" font-family="Helvetica Neue, Helvetica, Arial, sans-serif" font-size="18" font-weight="bold" fill="#333">Before: Manual Construction</text>
  <rect x="20" y="50" width="260" height="150" rx="8" ry="8" stroke="#F04B3E" stroke-width="2" fill="none"/>
  <text x="30" y="75" font-family="Menlo, monospace" font-size="14" fill="#333">var items: [String] = []</text>
  <text x="30" y="95" font-family="Menlo, monospace" font-size="14" fill="#333">items.append("Item 1")</text>
  <text x="30" y="115" font-family="Menlo, monospace" font-size="14" fill="#333">if condition {</text>
  <text x="45" y="135" font-family="Menlo, monospace" font-size="14" fill="#333">  items.append("Conditional Item")</text>
  <text x="30" y="155" font-family="Menlo, monospace" font-size="14" fill="#333">}</text>
  <text x="30" y="175" font-family="Menlo, monospace" font-size="14" fill="#333">items.append("Item 3")</text>

  <!-- Arrow -->
  <path d="M290 125 L310 125 L300 115 M310 125 L300 135" stroke="#1565c0" stroke-width="2" fill="none"/>
  <text x="285" y="105" font-family="Helvetica Neue, Helvetica, Arial, sans-serif" font-size="14" fill="#1565c0">Simplified by</text>

  <!-- After Section -->
  <text x="450" y="30" font-family="Helvetica Neue, Helvetica, Arial, sans-serif" font-size="18" font-weight="bold" fill="#333">After: Result Builder</text>
  <rect x="320" y="50" width="260" height="150" rx="8" ry="8" stroke="#2A8367" stroke-width="2" fill="none"/>
  <text x="330" y="75" font-family="Menlo, monospace" font-size="14" fill="#333">MyBuilder {</text>
  <text x="345" y="95" font-family="Menlo, monospace" font-size="14" fill="#333">  "Item 1"</text>
  <text x="345" y="115" font-family="Menlo, monospace" font-size="14" fill="#333">  if condition {</text>
  <text x="360" y="135" font-family="Menlo, monospace" font-size="14" fill="#333">    "Conditional Item"</text>
  <text x="345" y="155" font-family="Menlo, monospace" font-size="14" fill="#333">  }</text>
  <text x="345" y="175" font-family="Menlo, monospace" font-size="14" fill="#333">  "Item 3"</text>
  <text x="330" y="195" font-family="Menlo, monospace" font-size="14" fill="#333">}</text>
</svg>
</div>

## The Problem Result Builders Solve

Imagine you're building a list of configuration settings, or perhaps a complex data model, where elements might be conditionally included or repeated. Without Result Builders, you'd typically end up with code like this:

```swift
func buildConfigurationManually(includeFeatureA: Bool, itemCount: Int) -> [String] {
    var configItems: [String] = []

    configItems.append("BaseSetting: Enabled")

    if includeFeatureA {
        configItems.append("FeatureA: Active")
        configItems.append("FeatureA_Option: ValueX")
    }

    for i in 1...itemCount {
        configItems.append("RepeatedItem: \(i)")
    }

    configItems.append("FinalSetting: Complete")

    return configItems
}

let myConfig = buildConfigurationManually(includeFeatureA: true, itemCount: 2)
print(myConfig)
// Output: ["BaseSetting: Enabled", "FeatureA: Active", "FeatureA_Option: ValueX", "RepeatedItem: 1", "RepeatedItem: 2", "FinalSetting: Complete"]
```

This code works, but it's imperative and verbose. Each item needs an explicit `append` call, and conditional logic or loops break the flow. This is precisely the kind of boilerplate that Result Builders aim to eliminate, allowing for a more declarative and readable syntax.

## Understanding the Core Concept

At its heart, a Result Builder is a type (typically a `struct` or `enum`) annotated with the `@resultBuilder` attribute. This type defines a set of static methods that the Swift compiler uses to transform a sequence of expressions within a closure into a single, coherent result.

When you use a Result Builder, the compiler doesn't execute the closure's expressions in the usual way. Instead, it "translates" them into a series of calls to the builder's static methods. Each expression, conditional statement, or loop within the builder-annotated closure is mapped to a specific `build` method.

Let's break down the essential static methods you'll typically implement in a Result Builder:

*   `static func buildBlock(_ components: Component...) -> Component`
*   `static func buildExpression(_ expression: Expression) -> Component`
*   `static func buildEither(first component: Component) -> Component`
*   `static func buildEither(second component: Component) -> Component`
*   `static func buildOptional(_ component: Component?) -> Component`
*   `static func buildArray(_ components: [Component]) -> Component`

`Component` and `Expression` here are placeholders for the types your builder works with. `Component` is the intermediate type produced by each `build` method, which might be the final result type or a type that can be combined further. `Expression` is the type of individual statements within the builder block.

## Building a Custom Result Builder: HTMLBuilder

To truly grasp Result Builders, let's create a practical example: an `HTMLBuilder` that allows us to construct simple HTML structures using a declarative Swift syntax.

First, we need a way to represent our HTML nodes. We'll use a simple `struct` with an `enum` for the node type:

```swift
struct HTMLNode {
    enum NodeType {
        case text(String)
        case element(String, [HTMLNode]) // Tag name and children
    }
    let type: NodeType

    // A helper to render the node to a string
    var render: String {
        switch type {
        case .text(let content):
            return content
        case .element(let tag, let children):
            let childrenString = children.map { $0.render }.joined()
            return "<\(tag)>\(childrenString)</\(tag)>"
        }
    }
}
```

Now, let's define our `HTMLBuilder` struct and start implementing its static `build` methods.

### 1. `buildBlock`: Combining Multiple Components

The `buildBlock` method is the most fundamental. It takes multiple `Component` instances (which are `HTMLNode`s in our case) and combines them into a single `Component`. Since we want to build an array of nodes, our `buildBlock` will simply return the array of nodes it receives.

```swift
@resultBuilder
struct HTMLBuilder {
    // The core method to combine multiple nodes into a single array of nodes.
    static func buildBlock(_ components: HTMLNode...) -> [HTMLNode] {
        components
    }
}
```

### 2. `buildExpression`: Transforming Individual Expressions

When you write a single expression inside a Result Builder block (e.g., `"Hello"` or `HTMLNode.p { ... }`), the compiler calls `buildExpression`. We'll need two versions: one for plain strings (which become text nodes) and one for already-formed `HTMLNode` instances.

```swift
@resultBuilder
struct HTMLBuilder {
    static func buildBlock(_ components: HTMLNode...) -> [HTMLNode] {
        components
    }

    // Transforms a String literal into an HTMLNode (a text node).
    static func buildExpression(_ expression: String) -> HTMLNode {
        .init(type: .text(expression))
    }

    // Allows direct inclusion of an already-formed HTMLNode.
    static func func buildExpression(_ expression: HTMLNode) -> HTMLNode {
        expression
    }
}
```

Now, we can define helper functions that accept our `@HTMLBuilder` closure. This is similar to how SwiftUI views accept `@ViewBuilder` closures.

```swift
extension HTMLNode {
    static func p(@HTMLBuilder _ content: () -> [HTMLNode]) -> HTMLNode {
        .init(type: .element("p", content()))
    }
    static func div(@HTMLBuilder _ content: () -> [HTMLNode]) -> HTMLNode {
        .init(type: .element("div", content()))
    }
    static func h1(@HTMLBuilder _ content: () -> [HTMLNode]) -> HTMLNode {
        .init(type: .element("h1", content()))
    }
    // ... add more HTML tags as needed
}

// Basic usage:
let simplePage = HTMLNode.div {
    HTMLNode.h1 { "Welcome!" }
    HTMLNode.p { "This is a paragraph." }
}
print(simplePage.render)
// Output: <div><h1>Welcome!</h1><p>This is a paragraph.</p></div>
```

### 3. `buildEither(first:)` and `buildEither(second:)`: Handling `if` Statements

Result Builders support conditional compilation using `if` and `else`. When the compiler encounters an `if` statement, it uses `buildEither(first:)` for the `if` block and `buildEither(second:)` for the `else` block. These methods typically return a type that can represent either one of two possibilities. In our case, since both `if` and `else` blocks produce `[HTMLNode]`, we can simply return the component directly.

```swift
@resultBuilder
struct HTMLBuilder {
    // ... existing buildBlock and buildExpression methods ...

    // Handles the 'true' branch of an 'if' statement.
    static func buildEither(first component: [HTMLNode]) -> [HTMLNode] {
        component
    }

    // Handles the 'false' branch (the 'else' block) of an 'if' statement.
    static func buildEither(second component: [HTMLNode]) -> [HTMLNode] {
        component
    }
}

// Conditional usage:
let isLoggedIn = true
let conditionalPage = HTMLNode.div {
    HTMLNode.h1 { "Conditional Content" }
    if isLoggedIn {
        HTMLNode.p { "Welcome back, user!" }
    } else {
        HTMLNode.p { "Please log in." }
    }
}
print(conditionalPage.render)
// Output: <div><h1>Conditional Content</h1><p>Welcome back, user!</p></div>
```

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 280" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Result Builder Compiler Flow">
  <title>Result Builder Compiler Flow</title>
  <!-- Background rect -->
  <rect x="0" y="0" width="600" height="280" fill="#f9f9f9" rx="10"/>

  <!-- Nodes -->
  <rect x="20" y="50" width="150" height="50" rx="5" ry="5" fill="#1565c0"/>
  <text x="95" y="77" text-anchor="middle" font-family="Helvetica Neue, Helvetica, Arial, sans-serif" font-size="16" fill="white">Expression</text>

  <rect x="220" y="50" width="150" height="50" rx="5" ry="5" fill="#1565c0"/>
  <text x="295" y="77" text-anchor="middle" font-family="Helvetica Neue, Helvetica, Arial, sans-serif" font-size="16" fill="white">If/Else</text>

  <rect x="420" y="50" width="150" height="50" rx="5" ry="5" fill="#1565c0"/>
  <text x="495" y="77" text-anchor="middle" font-family="Helvetica Neue, Helvetica, Arial, sans-serif" font-size="16" fill="white">For Loop</text>

  <rect x="20" y="180" width="150" height="50" rx="5" ry="5" fill="#2A8367"/>
  <text x="95" y="207" text-anchor="middle" font-family="Helvetica Neue, Helvetica, Arial, sans-serif" font-size="16" fill="white">buildExpression</text>

  <rect x="220" y="180" width="150" height="50" rx="5" ry="5" fill="#2A8367"/>
  <text x="295" y="207" text-anchor="middle" font-family="Helvetica Neue, Helvetica, Arial, sans-serif" font-size="16" fill="white">buildEither</text>

  <rect x="420" y="180" width="150" height="50" rx="5" ry="5" fill="#2A8367"/>
  <text x="495" y="207" text-anchor="middle" font-family="Helvetica Neue, Helvetica, Arial, sans-serif" font-size="16" fill="white">buildArray</text>

  <rect x="220" y="230" width="150" height="30" rx="5" ry="5" fill="#2A8367"/>
  <text x="295" y="249" text-anchor="middle" font-family="Helvetica Neue, Helvetica, Arial, sans-serif" font-size="12" fill="white">(for optional)</text>


  <!-- Arrows -->
  <path d="M95 100 L95 180" stroke="#F04B3E" stroke-width="2" marker-end="url(#arrowhead)" />
  <path d="M295 100 L295 180" stroke="#F04B3E" stroke-width="2" marker-end="url(#arrowhead)" />
  <path d="M495 100 L495 180" stroke="#F04B3E" stroke-width="2" marker-end="url(#arrowhead)" />

  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#F04B3E" />
    </marker>
  </defs>

  <!-- Text labels for flow -->
  <text x="300" y="20" font-family="Helvetica Neue, Helvetica, Arial, sans-serif" font-size="18" font-weight="bold" fill="#333">Compiler Mapping</text>
  <text x="295" y="145" text-anchor="middle" font-family="Helvetica Neue, Helvetica, Arial, sans-serif" font-size="14" fill="#F04B3E">Maps To</text>

</svg>
</div>

### 4. `buildOptional`: Handling `if let` or `if` without `else`

When you have an `if` statement without an `else` branch, or an `if let` binding that might fail, the compiler wraps the result of the successful branch in an `Optional`. Your `buildOptional` method then handles this.

```swift
@resultBuilder
struct HTMLBuilder {
    // ... existing methods ...

    // Handles optional components (e.g., 'if condition { ... }' without an 'else').
    static func buildOptional(_ component: [HTMLNode]?) -> [HTMLNode] {
        component ?? [] // If nil, provide an empty array of nodes
    }
}

// Optional usage:
let maybeMessage: String? = "Secret message!"
let optionalPage = HTMLNode.div {
    HTMLNode.h1 { "Optional Content" }
    if let message = maybeMessage {
        HTMLNode.p { message }
    }
    // If 'maybeMessage' was nil, nothing would be rendered here.
}
print(optionalPage.render)
// Output: <div><h1>Optional Content</h1><p>Secret message!</p></div>
```

### 5. `buildArray`: Handling `for` Loops

For `for-in` loops, the compiler calls `buildArray`, passing an array of `Component` arrays (one for each iteration). You'll typically `flatMap` these into a single array.

```swift
@resultBuilder
struct HTMLBuilder {
    // ... existing methods ...

    // Handles 'for-in' loops, combining results from each iteration.
    static func buildArray(_ components: [[HTMLNode]]) -> [HTMLNode] {
        components.flatMap { $0 }
    }
}

// Loop usage:
let listPage = HTMLNode.div {
    HTMLNode.h1 { "List of Items" }
    for i in 1...3 {
        HTMLNode.p { "Item \(i)" }
    }
}
print(listPage.render)
// Output: <div><h1>List of Items</h1><p>Item 1</p><p>Item 2</p><p>Item 3</p></div>
```

### The Complete `HTMLBuilder`

Putting it all together, our `HTMLBuilder` now supports expressions, conditionals, and loops, letting us construct complex HTML declaratively:

```swift
// Final HTMLNode and HTMLBuilder Definitions (for clarity)
struct HTMLNode {
    enum NodeType {
        case text(String)
        case element(String, [HTMLNode])
    }
    let type: NodeType

    var render: String {
        switch type {
        case .text(let content):
            return content
        case .element(let tag, let children):
            let childrenString = children.map { $0.render }.joined()
            return "<\(tag)>\(childrenString)</\(tag)>"
        }
    }
}

@resultBuilder
struct HTMLBuilder {
    static func buildBlock(_ components: HTMLNode...) -> [HTMLNode] {
        components
    }

    static func buildExpression(_ expression: String) -> HTMLNode {
        .init(type: .text(expression))
    }

    static func buildExpression(_ expression: HTMLNode) -> HTMLNode {
        expression
    }

    static func buildEither(first component: [HTMLNode]) -> [HTMLNode] {
        component
    }

    static func buildEither(second component: [HTMLNode]) -> [HTMLNode] {
        component
    }

    static func buildOptional(_ component: [HTMLNode]?) -> [HTMLNode] {
        component ?? []
    }

    static func buildArray(_ components: [[HTMLNode]]) -> [HTMLNode] {
        components.flatMap { $0 }
    }
}

extension HTMLNode {
    static func p(@HTMLBuilder _ content: () -> [HTMLNode]) -> HTMLNode {
        .init(type: .element("p", content()))
    }
    static func div(@HTMLBuilder _ content: () -> [HTMLNode]) -> HTMLNode {
        .init(type: .element("div", content()))
    }
    static func h1(@HTMLBuilder _ content: () -> [HTMLNode]) -> HTMLNode {
        .init(type: .element("h1", content()))
    }
    static func ul(@HTMLBuilder _ content: () -> [HTMLNode]) -> HTMLNode {
        .init(type: .element("ul", content()))
    }
    static func li(@HTMLBuilder _ content: () -> [HTMLNode]) -> HTMLNode {
        .init(type: .element("li", content()))
    }
}

let userLoggedIn = true
let featuredProducts = ["Laptop", "Monitor", "Keyboard"]

let completePage = HTMLNode.div {
    HTMLNode.h1 { "My Awesome Page" }
    HTMLNode.p { "Welcome to our website!" }

    if userLoggedIn {
        HTMLNode.p { "You are currently logged in." }
        HTMLNode.div {
            "Here are some featured products:"
            HTMLNode.ul {
                for product in featuredProducts {
                    HTMLNode.li { product }
                }
            }
        }
    } else {
        HTMLNode.p { "Please log in to see personalized content." }
    }

    let footerText: String? = "Copyright 2026"
    if let text = footerText {
        HTMLNode.p { text }
    }
}

print(completePage.render)
/*
Output:
<div>
    <h1>My Awesome Page</h1>
    <p>Welcome to our website!</p>
    <p>You are currently logged in.</p>
    <div>Here are some featured products:
        <ul>
            <li>Laptop</li>
            <li>Monitor</li>
            <li>Keyboard</li>
        </ul>
    </div>
    <p>Copyright 2026</p>
</div>
*/
```

## How Result Builders Work Under the Hood

When the Swift compiler encounters a closure marked with a Result Builder attribute (like `@HTMLBuilder` or `@ViewBuilder`), it performs a source-to-source transformation. It doesn't execute the code directly. Instead, it rewrites the declarative block into a series of calls to the builder's static `build` methods.

Consider this simplified example:

```swift
// Your declarative code:
HTMLNode.div {
    "Hello"
    if condition {
        "World"
    }
}
```

The compiler essentially transforms this into something conceptually similar to:

```swift
// What the compiler "sees" and transforms:
let temp1 = HTMLBuilder.buildExpression("Hello")
let temp2: [HTMLNode]
if condition {
    temp2 = HTMLBuilder.buildEither(first: HTMLBuilder.buildExpression("World"))
} else {
    temp2 = HTMLBuilder.buildEither(second: HTMLBuilder.buildOptional(nil)) // Or an empty array if buildOptional returns that
}
let blockResult = HTMLBuilder.buildBlock(temp1, temp2.first!) // Simplified, actual buildBlock takes variadic
// Then the div initializer calls HTMLBuilder.buildBlock with the result
```
(Note: The actual transformation is more complex, especially with `buildBlock` taking variadic arguments and intermediate results, but this illustrates the concept.)

The key takeaway is that the builder methods are purely static and are called by the compiler during compilation, not at runtime by your explicit code. This is why Result Builders are often referred to as a form of "syntactic sugar" for constructing complex data.

## Benefits of Using Result Builders

1.  **Readability and Conciseness**: They allow you to define complex structures in a highly declarative and easy-to-read manner, eliminating repetitive `append` calls or manual conditional logic.
2.  **Domain-Specific Languages (DSLs)**: Result Builders are excellent for creating internal DSLs that closely resemble natural language or the domain they represent (e.g., SwiftUI's UI DSL, our HTML DSL).
3.  **Type Safety**: Because the compiler handles the transformation and type checking, you get compile-time guarantees that your constructed data conforms to the builder's expected output.
4.  **Extensibility**: By adding new `build` methods (e.g., `buildFinalResult` or custom `buildExpression` overloads), you can extend the builder's capabilities without changing existing client code.

```
┌───────────────────────┐             ┌───────────────────────────┐
│ Manual Construction   │             │ Result Builder DSL        │
├───────────────────────┤             ├───────────────────────────┤
│ - Verbose appending   │             │ - Declarative structure   │
│ - Imperative flow     │             │ - Concise syntax          │
│ - Explicit conditionals│             │ - Implicit conditional    │
│   and loops           │             │   and loop handling       │
│ - Error-prone         │             │ - Compiler-checked        │
└───────────────────────┘             └───────────────────────────┘
          ▲                                       ▲
          │ Less Readable                         │ More Readable
          │ More Boilerplate                      │ Less Boilerplate
```

## Summary

Result Builders are a powerful Swift feature that enables you to define mini-DSLs for constructing complex data structures in a declarative style. By implementing a set of static `build` methods in a type annotated with `@resultBuilder`, you guide the Swift compiler on how to transform a block of expressions, conditionals, and loops into a single, cohesive result. While SwiftUI's `@ViewBuilder` is the most prominent example, you can leverage Result Builders to simplify configuration files, data validation rules, custom data model creation, and much more, making your Swift code more expressive and maintainable.

Happy Swifting!
