---
title: Understanding Result Builders in Swift
date: 2026-10-17 12:36
description: Explore Swift's Result Builders, a powerful feature for creating expressive domain-specific languages and declarative APIs in your iOS apps.
tags: Swift, iOS, Programming
---

# Understanding Result Builders in Swift

Swift is a language constantly evolving, providing developers with powerful tools to write cleaner, more expressive, and safer code. One such feature, introduced in Swift 5.4, is **Result Builders** (originally known as Function Builders). While SwiftUI developers interact with them daily without perhaps realizing it, Result Builders are a general-purpose Swift feature that allows you to create highly expressive Domain-Specific Languages (DSLs) and declarative APIs.

If you've ever written SwiftUI views, you've used a Result Builder. The way you stack `Text`, `Image`, `VStack`, and other views inside a `body` property or a `VStack` closure is made possible by a Result Builder, specifically `ViewBuilder`. But their utility extends far beyond UI.

In this article, we'll dive deep into what Result Builders are, how they work under the hood, and how you can leverage them to craft your own elegant, declarative APIs in your Swift projects.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Comparison of imperative vs. declarative code structure with Result Builders">
  <title>Imperative vs. Declarative Code with Result Builders</title>

  <!-- Imperative Box -->
  <rect x="20" y="30" width="260" height="160" rx="10" fill="#F04B3E" opacity="0.1" stroke="#F04B3E" stroke-width="2"/>
  <text x="150" y="55" font-family="Arial, sans-serif" font-size="18" fill="#F04B3E" text-anchor="middle" font-weight="bold">Imperative Code</text>
  <text x="150" y="85" font-family="Arial, sans-serif" font-size="14" fill="#333" text-anchor="middle">`var result = ""`</text>
  <text x="150" y="105" font-family="Arial, sans-serif" font-size="14" fill="#333" text-anchor="middle">`if condition {`</text>
  <text x="150" y="125" font-family="Arial, sans-serif" font-size="14" fill="#333" text-anchor="middle">`  result += "item1"`</text>
  <text x="150" y="145" font-family="Arial, sans-serif" font-size="14" fill="#333" text-anchor="middle">`}`</text>
  <text x="150" y="165" font-family="Arial, sans-serif" font-size="14" fill="#333" text-anchor="middle">`for item in items { ... }`</text>

  <!-- Arrow -->
  <path d="M290 100 L310 100 M300 90 L310 100 L300 110" stroke="#1565c0" stroke-width="2" fill="none"/>
  <text x="300" y="130" font-family="Arial, sans-serif" font-size="14" fill="#1565c0" text-anchor="middle">Transformed by</text>
  <text x="300" y="148" font-family="Arial, sans-serif" font-size="14" fill="#1565c0" text-anchor="middle">Result Builder</text>

  <!-- Declarative Box -->
  <rect x="320" y="30" width="260" height="160" rx="10" fill="#2A8367" opacity="0.1" stroke="#2A8367" stroke-width="2"/>
  <text x="450" y="55" font-family="Arial, sans-serif" font-size="18" fill="#2A8367" text-anchor="middle" font-weight="bold">Declarative Code</text>
  <text x="450" y="85" font-family="Arial, sans-serif" font-size="14" fill="#333" text-anchor="middle">`MyBuilder {`</text>
  <text x="450" y="105" font-family="Arial, sans-serif" font-size="14" fill="#333" text-anchor="middle">`  if condition {`</text>
  <text x="450" y="125" font-family="Arial, sans-serif" font-size="14" fill="#333" text-anchor="middle">`    Item1()`</text>
  <text x="450" y="145" font-family="Arial, sans-serif" font-size="14" fill="#333" text-anchor="middle">`  }`</text>
  <text x="450" y="165" font-family="Arial, sans-serif" font-size="14" fill="#333" text-anchor="middle">`  for item in items { ... }`</text>
  <text x="450" y="185" font-family="Arial, sans-serif" font-size="14" fill="#333" text-anchor="middle">`}`</text>
</svg>
</div>

## The Problem Result Builders Solve

Imagine you want to construct a complex data structure, like a list of configuration items, or even a simple array, based on conditional logic and loops. Without Result Builders, you'd typically write imperative code:

```swift
struct MenuItem {
    let name: String
    let price: Double?
    let isVegetarian: Bool
}

func buildMenuImperative(includeSpecials: Bool, vegetarianOnly: Bool) -> [MenuItem] {
    var menuItems: [MenuItem] = []

    menuItems.append(MenuItem(name: "Classic Burger", price: 12.50, isVegetarian: false))
    menuItems.append(MenuItem(name: "Fries", price: 4.00, isVegetarian: true))

    if includeSpecials {
        menuItems.append(MenuItem(name: "Daily Special Pasta", price: 18.00, isVegetarian: false))
        if vegetarianOnly {
            // This won't be added if vegetarianOnly is true and the special is not vegetarian
        } else {
            menuItems.append(MenuItem(name: "Steak Frites", price: 25.00, isVegetarian: false))
        }
    }

    if vegetarianOnly {
        // Filter out non-vegetarian items
        return menuItems.filter { $0.isVegetarian }
    } else {
        return menuItems
    }
}

let fullMenu = buildMenuImperative(includeSpecials: true, vegetarianOnly: false)
print("Full Menu: \(fullMenu.map { $0.name })")
// Output: Full Menu: ["Classic Burger", "Fries", "Daily Special Pasta", "Steak Frites"]

let veggieMenu = buildMenuImperative(includeSpecials: true, vegetarianOnly: true)
print("Veggie Menu: \(veggieMenu.map { $0.name })")
// Output: Veggie Menu: ["Fries"] -- Note: "Daily Special Pasta" might be vegetarian sometimes, but the logic above is a bit simplified.
```

This code works, but it's verbose and mixes the logic of *what* to add with *how* to add it (appending to an array). For more complex scenarios, especially nested conditions and loops, this can quickly become hard to read and maintain.

## Introducing Result Builders

Result Builders allow us to transform a block of declarative statements into a single, cohesive result. The magic happens via a type annotated with the `@resultBuilder` attribute. This type contains static methods (or instance methods if it's a struct/class) that the Swift compiler uses to "build" the result from the statements within a closure.

Let's start by building a simple `ArrayBuilder` to create arrays of `String`s declaratively.

```swift
@resultBuilder
struct ArrayBuilder<Element> {
    // 1. buildBlock: Combines multiple results into a single one.
    // This is the most fundamental method.
    static func buildBlock(_ components: Element...) -> [Element] {
        components
    }

    // 2. buildExpression: Transforms an individual expression into a result.
    // Allows direct use of elements without wrapping them.
    static func buildExpression(_ expression: Element) -> [Element] {
        [expression]
    }
    
    // 3. buildOptional: Handles 'if' statements without 'else'.
    static func buildOptional(_ component: [Element]?) -> [Element] {
        component ?? []
    }

    // 4. buildEither(first:): Handles the 'if' branch of an 'if/else' statement.
    static func buildEither(first component: [Element]) -> [Element] {
        component
    }

    // 5. buildEither(second:): Handles the 'else' branch of an 'if/else' statement.
    static func buildEither(second component: [Element]) -> [Element] {
        component
    }
    
    // 6. buildArray: Handles 'for' loops.
    static func buildArray(_ components: [[Element]]) -> [Element] {
        components.flatMap { $0 }
    }
    
    // 7. buildFinalResult: Transforms the final accumulated result.
    // Useful for converting an intermediate representation to the desired final type.
    static func buildFinalResult(_ component: [Element]) -> [Element] {
        component // In this case, no final transformation needed
    }
}
```

Now, let's use our `ArrayBuilder` to construct the menu items declaratively:

```swift
func buildMenuDeclarative(@ArrayBuilder<MenuItem> _ content: () -> [MenuItem]) -> [MenuItem] {
    content()
}

let declarativeMenu = buildMenuDeclarative {
    MenuItem(name: "Classic Burger", price: 12.50, isVegetarian: false)
    MenuItem(name: "Fries", price: 4.00, isVegetarian: true)

    if true { // Simulating includeSpecials
        MenuItem(name: "Daily Special Pasta", price: 18.00, isVegetarian: false)
        if false { // Simulating !vegetarianOnly
            MenuItem(name: "Steak Frites", price: 25.00, isVegetarian: false)
        }
    }
    // No explicit 'for' loop here, but it would work similarly
}

print("Declarative Menu: \(declarativeMenu.map { $0.name })")
// Output: Declarative Menu: ["Classic Burger", "Fries", "Daily Special Pasta", "Steak Frites"]
```

Notice how much cleaner the `buildMenuDeclarative` usage is. We're just listing the `MenuItem` objects, and the builder automatically collects them into an array. The `if` statements work directly within the builder closure, and the result builder handles the conditional inclusion.

### The Core Components of a Result Builder

A result builder can implement several static methods, each responsible for transforming a specific type of statement within the builder closure. Here are the most common ones:

1.  **`buildBlock(_ components: [Component]...) -> Result`**: This is the most essential method. It takes multiple results from individual statements and combines them into a single result. The compiler calls this to combine consecutive lines of code within the builder closure.
2.  **`buildExpression(_ expression: Expression) -> Component`**: If you want to allow direct expressions (like `MenuItem(...)` in our example) without any explicit wrapping, this method transforms them into the `Component` type the builder works with.
3.  **`buildOptional(_ component: Component?) -> Component`**: Handles `if` statements without an `else` clause. If the condition is false, `component` will be `nil`.
4.  **`buildEither(first: Component) -> Component`**: Handles the `if` branch of an `if/else` statement.
5.  **`buildEither(second: Component) -> Component`**: Handles the `else` branch of an `if/else` statement.
6.  **`buildArray(_ components: [Component]) -> Component`**: Processes `for` loops. The compiler collects all results from the loop's body into an array, which is then passed to this method.
7.  **`buildLimitedAvailability(_ component: Component) -> Component`**: Used for `#available` checks.
8.  **`buildFinalResult(_ component: Component) -> FinalResult`**: Called on the final accumulated result of the entire builder closure. This is useful if your builder works with an intermediate type and needs to convert it to the desired final output type. For example, `ViewBuilder` might build a `_ViewModifier_Content` internally and then convert it to `some View` using `buildFinalResult`.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 250" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Flowchart of Result Builder component interaction">
  <title>Result Builder Component Interaction Flow</title>

  <!-- Start Node -->
  <rect x="250" y="10" width="100" height="40" rx="5" fill="#1565c0" opacity="0.1" stroke="#1565c0" stroke-width="2"/>
  <text x="300" y="35" font-family="Arial, sans-serif" font-size="14" fill="#1565c0" text-anchor="middle">Builder Closure</text>

  <!-- Process Expression -->
  <path d="M300 50 L300 70" stroke="#333" stroke-width="1"/>
  <rect x="200" y="70" width="200" height="40" rx="5" fill="#2A8367" opacity="0.1" stroke="#2A8367" stroke-width="2"/>
  <text x="300" y="95" font-family="Arial, sans-serif" font-size="14" fill="#2A8367" text-anchor="middle">`buildExpression(_:)`</text>

  <!-- Process Conditionals -->
  <path d="M300 110 L300 130" stroke="#333" stroke-width="1"/>
  <rect x="10" y="130" width="180" height="40" rx="5" fill="#F04B3E" opacity="0.1" stroke="#F04B3E" stroke-width="2"/>
  <text x="100" y="155" font-family="Arial, sans-serif" font-size="14" fill="#F04B3E" text-anchor="middle">`buildOptional(_:)`</text>
  <rect x="210" y="130" width="180" height="40" rx="5" fill="#F04B3E" opacity="0.1" stroke="#F04B3E" stroke-width="2"/>
  <text x="300" y="155" font-family="Arial, sans-serif" font-size="14" fill="#F04B3E" text-anchor="middle">`buildEither(first/second:)`</text>

  <!-- Process Loops -->
  <path d="M300 110 L450 110 L450 130" stroke="#333" stroke-width="1"/>
  <rect x="410" y="130" width="180" height="40" rx="5" fill="#F04B3E" opacity="0.1" stroke="#F04B3E" stroke-width="2"/>
  <text x="500" y="155" font-family="Arial, sans-serif" font-size="14" fill="#F04B3E" text-anchor="middle">`buildArray(_:)`</text>

  <!-- Combine with buildBlock -->
  <path d="M100 170 L100 200 L250 200" stroke="#333" stroke-width="1"/>
  <path d="M300 170 L300 200 L250 200" stroke="#333" stroke-width="1"/>
  <path d="M500 170 L500 200 L350 200" stroke="#333" stroke-width="1"/>
  <rect x="250" y="180" width="100" height="40" rx="5" fill="#1565c0" opacity="0.1" stroke="#1565c0" stroke-width="2"/>
  <text x="300" y="205" font-family="Arial, sans-serif" font-size="14" fill="#1565c0" text-anchor="middle">`buildBlock(_:)`</text>

  <!-- Final Result -->
  <path d="M300 220 L300 240" stroke="#333" stroke-width="1"/>
  <rect x="250" y="230" width="100" height="40" rx="5" fill="#2A8367" opacity="0.1" stroke="#2A8367" stroke-width="2"/>
  <text x="300" y="255" font-family="Arial, sans-serif" font-size="14" fill="#2A8367" text-anchor="middle">`buildFinalResult(_:)`</text>
</svg>
</div>

## How Result Builders Work: Compiler Transformation

The core idea behind Result Builders is that the Swift compiler transforms the declarative code you write inside a closure into a series of calls to the builder's static methods. It's syntactic sugar that makes complex constructions appear simple.

Consider this simple builder usage:

```swift
// MyBuilder {
//    "Hello"
//    if condition {
//        "World"
//    } else {
//        "Swift"
//    }
//    for item in items {
//        item.uppercased()
//    }
// }
```

The compiler transforms this into something conceptually similar to:

```swift
// let temp1 = MyBuilder.buildExpression("Hello")
// let temp2: [String]
// if condition {
//    temp2 = MyBuilder.buildEither(first: MyBuilder.buildExpression("World"))
// } else {
//    temp2 = MyBuilder.buildEither(second: MyBuilder.buildExpression("Swift"))
// }
//
// var loopResults: [[String]] = []
// for item in items {
//    loopResults.append(MyBuilder.buildExpression(item.uppercased()))
// }
// let temp3 = MyBuilder.buildArray(loopResults)
//
// let blockResult = MyBuilder.buildBlock(temp1, temp2, temp3)
// return MyBuilder.buildFinalResult(blockResult)
```

This transformation is why you don't explicitly call `append` or `filter` within a Result Builder closure; the builder methods handle that implicitly.

```
┌─────────────────────────┐        ┌───────────────────────────────┐
│   Declarative Syntax    │        │      Compiler Transformation  │
│                         │        │                               │
│  MyBuilder {            │        │  let b1 = MyBuilder.buildExpr(...) │
│    Expr1                │  ───►  │  let b2 = MyBuilder.buildEither(...) │
│    if cond { Expr2 }    │        │  let b3 = MyBuilder.buildArray(...)  │
│    for x in arr { Expr3 }│        │  let block = MyBuilder.buildBlock(b1, b2, b3) │
│  }                      │        │  return MyBuilder.buildFinalResult(block) │
└─────────────────────────┘        └───────────────────────────────┘
```

## Practical Example: A Custom HTML Builder

Let's create a more tangible example: a builder to construct simple HTML strings.

First, we need some basic HTML element types:

```swift
// Represents a simple HTML element
struct HTMLElement {
    let tag: String
    let content: String?
    let attributes: [String: String]
    let children: [HTMLElement] // For nested elements

    init(tag: String, content: String? = nil, attributes: [String: String] = [:], children: [HTMLElement] = []) {
        self.tag = tag
        self.content = content
        self.attributes = attributes
        self.children = children
    }

    func render() -> String {
        var attrString = ""
        if !attributes.isEmpty {
            attrString = attributes.map { key, value in
                " \(key)=\"\(value)\""
            }.joined()
        }

        let childrenContent = children.map { $0.render() }.joined()

        if let content = content, !content.isEmpty {
            return "<\(tag)\(attrString)>\(content)\(childrenContent)</\(tag)>"
        } else if !childrenContent.isEmpty {
            return "<\(tag)\(attrString)>\(childrenContent)</\(tag)>"
        } else {
            return "<\(tag)\(attrString)/>" // Self-closing for empty tags without children
        }
    }
}

// Convenience functions for common tags
func p(_ text: String, attributes: [String: String] = [:]) -> HTMLElement {
    HTMLElement(tag: "p", content: text, attributes: attributes)
}

func div(@HTMLBuilder _ content: () -> [HTMLElement]) -> HTMLElement {
    HTMLElement(tag: "div", children: content())
}

func h1(_ text: String, attributes: [String: String] = [:]) -> HTMLElement {
    HTMLElement(tag: "h1", content: text, attributes: attributes)
}

func ul(@HTMLBuilder _ content: () -> [HTMLElement]) -> HTMLElement {
    HTMLElement(tag: "ul", children: content())
}

func li(_ text: String, attributes: [String: String] = [:]) -> HTMLElement {
    HTMLElement(tag: "li", content: text, attributes: attributes)
}
```

Now, let's define our `HTMLBuilder`:

```swift
@resultBuilder
struct HTMLBuilder {
    // Component type for individual elements
    typealias Component = [HTMLElement]

    // 1. buildBlock: Combines multiple components (arrays of elements) into one array.
    static func buildBlock(_ components: Component...) -> Component {
        components.flatMap { $0 }
    }

    // 2. buildExpression: Allows direct HTMLElement expressions.
    static func buildExpression(_ expression: HTMLElement) -> Component {
        [expression]
    }

    // 3. buildOptional: Handles 'if' without 'else'.
    static func buildOptional(_ component: Component?) -> Component {
        component ?? []
    }

    // 4. buildEither(first:): Handles the 'if' branch.
    static func buildEither(first component: Component) -> Component {
        component
    }

    // 5. buildEither(second:): Handles the 'else' branch.
    static func buildEither(second component: Component) -> Component {
        component
    }

    // 6. buildArray: Handles 'for' loops.
    static func buildArray(_ components: [Component]) -> Component {
        components.flatMap { $0 }
    }

    // 7. buildFinalResult: Transforms the final array of elements into a single HTMLElement (e.g., a root div)
    // or just returns the array if the context expects multiple.
    // For simplicity, let's assume the top-level builder produces an array of elements.
    // If we wanted a single root element, we might wrap it in a div.
    static func buildFinalResult(_ component: Component) -> Component {
        component
    }
}

// Function to use the HTMLBuilder
func buildHTML(@HTMLBuilder _ content: () -> [HTMLElement]) -> String {
    content().map { $0.render() }.joined(separator: "\n")
}
```

With our `HTMLBuilder` in place, we can now construct HTML in a wonderfully declarative way:

```swift
let dynamicContent = "Dynamic Content"
let isLoggedIn = true
let items = ["Item 1", "Item 2", "Item 3"]

let htmlString = buildHTML {
    h1("Welcome to My Page")
    p("This is a paragraph with \(dynamicContent).")

    if isLoggedIn {
        div {
            p("You are logged in!", attributes: ["class": "success"])
            ul {
                for item in items {
                    li(item)
                }
            }
        }
    } else {
        p("Please log in to see more content.")
    }

    // Example of using buildOptional if isLoggedIn was optional
    // if let user = optionalUser {
    //    p("Welcome, \(user.name)")
    // }
}

print(htmlString)
```

This will output:

```html
<h1>Welcome to My Page</h1>
<p>This is a paragraph with Dynamic Content.</p>
<div>
<p class="success">You are logged in!</p>
<ul>
<li>Item 1</li>
<li>Item 2</li>
<li>Item 3</li>
</ul>
</div>
```

This example clearly demonstrates how Result Builders enable a concise, readable, and declarative syntax for generating complex output. The structure of the code directly mirrors the structure of the HTML, making it much easier to reason about than string concatenation or imperative array appending.

## Benefits and Considerations

**Benefits:**
*   **Declarative Syntax:** Greatly improves readability and reduces boilerplate by allowing you to express *what* you want, rather than *how* to build it.
*   **Domain-Specific Languages (DSLs):** Perfect for creating small, highly specialized languages within Swift, like for UI, configuration, or data transformations.
*   **Compositionality:** Builder blocks can be nested, allowing for complex hierarchical structures to be built up from smaller, manageable parts.
*   **Compiler-Assisted:** The compiler handles the transformation, ensuring type safety and providing helpful error messages.

**Considerations:**
*   **Learning Curve:** Understanding the compiler's transformation and the various `build` methods can take some time.
*   **Debugging:** Debugging issues within a builder closure might sometimes be less straightforward than in traditional imperative code, as the actual code being executed is generated by the compiler.
*   **Overuse:** While powerful, Result Builders are not a silver bullet. For very simple scenarios, traditional imperative code might still be clearer. They shine when you have repetitive patterns with conditional logic or loops that produce a structured output.

## Summary

Result Builders are a sophisticated Swift feature that empowers developers to define custom declarative syntaxes. By leveraging methods like `buildBlock`, `buildExpression`, `buildOptional`, `buildEither`, and `buildArray`, you can guide the Swift compiler to transform a sequence of statements into a single, structured result. This capability is fundamental to SwiftUI's elegant API and is an invaluable tool for crafting your own expressive DSLs, making your code more readable, maintainable, and delightful to work with.

Happy Swifting!
