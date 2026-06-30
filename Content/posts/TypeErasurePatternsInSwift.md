---
title: Type Erasure Patterns in Swift
date: 2026-06-30 11:40
description: Explore type erasure in Swift to overcome limitations of generics and protocols, enabling flexible, type-safe code for complex architectures.
tags: Swift, iOS, Architecture
---

# Type Erasure Patterns in Swift

Swift is a language that champions strong typing and protocol-oriented programming. Generics and protocols are powerful tools that allow us to write flexible, reusable, and type-safe code. However, there are specific scenarios where these powerful features seem to hit a wall, particularly when working with protocols that declare `associatedtype` requirements (often called "protocols with associated types" or PATs).

Imagine you're building a system where different components need to conform to a common protocol, but each component might handle a slightly different data type. How do you store these diverse components in a single collection, or pass them around uniformly, without losing type safety or resorting to `Any`? This is where type erasure comes to the rescue.

In this article, we'll dive deep into type erasure patterns in Swift, understanding the problem they solve, how to implement them, and when to wisely apply them in your iOS or Swift applications.

## The Problem: When Protocols Become Too Specific

Let's start by illustrating the problem that type erasure aims to solve. Consider a common pattern: a `Validator` protocol.

```swift
protocol Validator {
    associatedtype Value
    func isValid(_ value: Value) -> Bool
}
```

This protocol is wonderfully flexible. We can create concrete validators for different types:

```swift
struct EmailValidator: Validator {
    func isValid(_ value: String) -> Bool {
        return value.contains("@") && value.contains(".") // Simplified
    }
}

struct PasswordValidator: Validator {
    func isValid(_ value: String) -> Bool {
        return value.count >= 8 && value.rangeOfCharacter(from: .letters) != nil && value.rangeOfCharacter(from: .decimalDigits) != nil
    }
}

struct AgeValidator: Validator {
    func isValid(_ value: Int) -> Bool {
        return value >= 18
    }
}
```

Now, suppose you want to create a collection of `Validator` instances. You might intuitively try to do this:

```swift
// This won't compile!
// let stringValidators: [any Validator] = [EmailValidator(), PasswordValidator()]
// let allValidators: [any Validator] = [EmailValidator(), AgeValidator()]
```

If you try the above, Swift's compiler will greet you with an error like: **"Protocol 'Validator' can only be used as a generic constraint because it has Self or associated type requirements."**

Why does this happen? When a protocol has an `associatedtype`, it means the protocol's definition depends on a specific type that the conforming type provides. The `Validator` protocol, for example, isn't just a `Validator`; it's a `Validator where Value == String` or a `Validator where Value == Int`. The compiler needs to know the specific `Value` type at compile time to ensure type safety.

When you declare `[any Validator]`, you're asking for a collection where each element could be *any* `Validator`, regardless of its `Value` type. This ambiguity makes it impossible for the compiler to guarantee that `isValid(_:)` can be called safely on every element, as the `Value` type might differ.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Diagram illustrating the compilation error when trying to store different concrete types of a protocol with an associated type in a collection without type erasure.">
  <title>The Problem: Storing Protocol Types with Associated Types</title>

  <!-- Protocol Box -->
  <rect x="220" y="10" width="160" height="50" rx="5" ry="5" fill="#2A8367" stroke="#000" stroke-width="2"/>
  <text x="300" y="40" font-family="Arial, sans-serif" font-size="16" fill="#FFF" text-anchor="middle">protocol <tspan font-weight="bold">Validator</tspan></text>
  <text x="300" y="58" font-family="Arial, sans-serif" font-size="12" fill="#FFF" text-anchor="middle">associatedtype Value</text>

  <!-- Concrete Type EmailValidator -->
  <rect x="50" y="90" width="160" height="50" rx="5" ry="5" fill="#F0F0F0" stroke="#000" stroke-width="2"/>
  <text x="130" y="120" font-family="Arial, sans-serif" font-size="16" fill="#000" text-anchor="middle">EmailValidator</text>
  <text x="130" y="138" font-family="Arial, sans-serif" font-size="12" fill="#000" text-anchor="middle">conforms to Validator (Value=String)</text>

  <!-- Concrete Type PasswordValidator -->
  <rect x="390" y="90" width="160" height="50" rx="5" ry="5" fill="#F0F0F0" stroke="#000" stroke-width="2"/>
  <text x="470" y="120" font-family="Arial, sans-serif" font-size="16" fill="#000" text-anchor="middle">PasswordValidator</text>
  <text x="470" y="138" font-family="Arial, sans-serif" font-size="12" fill="#000" text-anchor="middle">conforms to Validator (Value=String)</text>

  <!-- Arrows to Protocol -->
  <line x1="130" y1="90" x2="270" y2="60" stroke="#000" stroke-width="2" marker-end="url(#arrowhead)"/>
  <line x1="470" y1="90" x2="330" y2="60" stroke="#000" stroke-width="2" marker-end="url(#arrowhead)"/>

  <!-- Collection Box (Problem) -->
  <rect x="190" y="160" width="220" height="50" rx="5" ry="5" fill="#F04B3E" stroke="#000" stroke-width="2"/>
  <text x="300" y="190" font-family="Arial, sans-serif" font-size="16" fill="#FFF" text-anchor="middle">let validators: [any Validator]</text>
  <text x="300" y="208" font-family="Arial, sans-serif" font-size="12" fill="#FFF" text-anchor="middle">(Error: 'Validator' has associated type requirements)</text>

  <!-- Arrow from types to collection (dashed, indicating attempt) -->
  <line x1="130" y1="140" x2="240" y2="160" stroke="#F04B3E" stroke-width="2" stroke-dasharray="5,5"/>
  <line x1="470" y1="140" x2="360" y2="160" stroke="#F04B3E" stroke-width="2" stroke-dasharray="5,5"/>

  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#000" />
    </marker>
  </defs>
</svg>
</div>

## Swift's Existential Types (`any Protocol`) and Opaque Types (`some Protocol`)

Before diving into type erasure, it's worth briefly clarifying Swift's built-in ways to handle protocols:

*   **`some Protocol` (Opaque Types):** Introduced in Swift 5.1, `some Protocol` is used as a *return type* to indicate that a function returns a concrete type that conforms to a protocol, but the caller doesn't need to know the exact type. The *same* concrete type is always returned. It's like an "inverse generic." It doesn't solve the collection problem.
*   **`any Protocol` (Existential Types):** Introduced in Swift 5.6, `any Protocol` explicitly denotes an existential type, meaning "some value of *any* concrete type that conforms to this protocol." While it makes the intent clearer, it still cannot be used with protocols that have `Self` or `associatedtype` requirements because the compiler cannot guarantee the `associatedtype` at runtime across different concrete types.

This is precisely the gap that type erasure fills.

## The Solution: Type Erasure

Type erasure is a design pattern where you wrap a concrete type that conforms to a protocol with associated types inside a non-generic (or generically constrained) wrapper struct or class. This wrapper then conforms to the *same* protocol, but it "erases" the specific generic details of the wrapped type, presenting a uniform interface.

The wrapper essentially holds a reference to the underlying concrete type and forwards all protocol method calls to it. By making the wrapper generic over the associated types themselves (e.g., `AnyValidator<Value>`), we effectively fix the associated type, allowing us to store different concrete types that share that same associated type.

### Practical Example: Creating `AnyValidator`

Let's create our `AnyValidator` type eraser for the `Validator` protocol:

```swift
struct AnyValidator<V>: Validator {
    typealias Value = V

    // A private closure that captures the 'isValid' method of the wrapped validator
    private let _isValid: (V) -> Bool

    // The initializer takes any concrete type 'T' that conforms to Validator,
    // as long as its 'Value' type matches 'V'.
    init<T: Validator>(_ validator: T) where T.Value == V {
        _isValid = validator.isValid
    }

    // Forward the protocol requirement to the captured closure
    func isValid(_ value: V) -> Bool {
        return _isValid(value)
    }
}
```

Let's break down `AnyValidator`:

1.  **`struct AnyValidator<V>: Validator`**: It's a generic struct, where `V` represents the `Value` associated type of the `Validator` protocol. Crucially, `AnyValidator` itself conforms to `Validator`.
2.  **`typealias Value = V`**: This line explicitly tells the compiler that `AnyValidator`'s `Value` associated type is the generic type `V`. This "fixes" the associated type for `AnyValidator`, making it a concrete type for the `Validator` protocol (e.g., `AnyValidator<String>`).
3.  **`private let _isValid: (V) -> Bool`**: This is the core of the type erasure. Instead of storing the `validator` instance directly, we store a closure that captures the `isValid` method of the concrete validator passed into the initializer. This allows us to invoke the original validator's logic without needing to know its specific type.
4.  **`init<T: Validator>(_ validator: T) where T.Value == V`**: The initializer is generic over `T`, the concrete validator type. The `where T.Value == V` clause is vital: it ensures that *only* validators whose `Value` type matches `AnyValidator`'s `V` can be wrapped. This preserves type safety.
5.  **`func isValid(_ value: V) -> Bool`**: This simply calls the stored `_isValid` closure, forwarding the `value`.

Now, we can use `AnyValidator` to solve our collection problem:

```swift
let emailValidator = EmailValidator()
let passwordValidator = PasswordValidator()
let ageValidator = AgeValidator() // Value is Int

// Wrap our concrete validators with AnyValidator<String>
let anyEmailValidator = AnyValidator(emailValidator)
let anyPasswordValidator = AnyValidator(passwordValidator)

// Now we can put them into a collection!
let stringValidators: [AnyValidator<String>] = [anyEmailValidator, anyPasswordValidator]

print("--- String Validators ---")
for validator in stringValidators {
    print("Is 'test@example.com' valid? \(validator.isValid("test@example.com"))")
    print("Is 'short' valid? \(validator.isValid("short"))")
}

// We can also create a collection for Int validators:
let anyAgeValidator = AnyValidator(ageValidator)
let intValidators: [AnyValidator<Int>] = [anyAgeValidator]

print("\n--- Int Validators ---")
for validator in intValidators {
    print("Is 17 valid? \(validator.isValid(17))")
    print("Is 20 valid? \(validator.isValid(20))")
}
```

This works beautifully! We've successfully stored different concrete types (`EmailValidator`, `PasswordValidator`) in a single collection (`[AnyValidator<String>]`) by erasing their specific structural types while retaining their shared `Value` type.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 280" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Diagram illustrating how type erasure with AnyValidator<String> allows storing different concrete validator types in a collection.">
  <title>Type Erasure with AnyValidator<String></title>

  <!-- Concrete Type EmailValidator -->
  <rect x="50" y="10" width="160" height="50" rx="5" ry="5" fill="#F0F0F0" stroke="#000" stroke-width="2"/>
  <text x="130" y="40" font-family="Arial, sans-serif" font-size="16" fill="#000" text-anchor="middle">EmailValidator</text>
  <text x="130" y="58" font-family="Arial, sans-serif" font-size="12" fill="#000" text-anchor="middle">conforms to Validator (Value=String)</text>

  <!-- Concrete Type PasswordValidator -->
  <rect x="390" y="10" width="160" height="50" rx="5" ry="5" fill="#F0F0F0" stroke="#000" stroke-width="2"/>
  <text x="470" y="40" font-family="Arial, sans-serif" font-size="16" fill="#000" text-anchor="middle">PasswordValidator</text>
  <text x="470" y="58" font-family="Arial, sans-serif" font-size="12" fill="#000" text-anchor="middle">conforms to Validator (Value=String)</text>

  <!-- AnyValidator Box -->
  <rect x="220" y="100" width="160" height="70" rx="5" ry="5" fill="#1565c0" stroke="#000" stroke-width="2"/>
  <text x="300" y="130" font-family="Arial, sans-serif" font-size="16" fill="#FFF" text-anchor="middle">AnyValidator&lt;String&gt;</text>
  <text x="300" y="148" font-family="Arial, sans-serif" font-size="12" fill="#FFF" text-anchor="middle">conforms to Validator (Value=String)</text>
  <text x="300" y="166" font-family="Arial, sans-serif" font-size="10" fill="#FFF" text-anchor="middle">(wraps concrete Validator)</text>

  <!-- Arrows from Concrete Types to AnyValidator -->
  <line x1="130" y1="60" x2="270" y2="100" stroke="#000" stroke-width="2" marker-end="url(#arrowhead)"/>
  <line x1="470" y1="60" x2="330" y2="100" stroke="#000" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="210" y="85" font-family="Arial, sans-serif" font-size="10" fill="#000" text-anchor="middle">init(EmailValidator)</text>
  <text x="390" y="85" font-family="Arial, sans-serif" font-size="10" fill="#000" text-anchor="middle">init(PasswordValidator)</text>

  <!-- Collection Box (Solution) -->
  <rect x="190" y="210" width="220" height="50" rx="5" ry="5" fill="#2A8367" stroke="#000" stroke-width="2"/>
  <text x="300" y="240" font-family="Arial, sans-serif" font-size="16" fill="#FFF" text-anchor="middle">let validators: [AnyValidator&lt;String&gt;]</text>
  <text x="300" y="258" font-family="Arial, sans-serif" font-size="12" fill="#FFF" text-anchor="middle">(Works! Heterogeneous collection)</text>

  <!-- Arrows from AnyValidator to Collection -->
  <line x1="300" y1="170" x2="300" y2="210" stroke="#000" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="300" y="195" font-family="Arial, sans-serif" font-size="10" fill="#000" text-anchor="middle">add to collection</text>

  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#000" />
    </marker>
  </defs>
</svg>
</div>

### Built-in Type Erasers: `AnyHashable` and `AnyCancellable`

You've likely encountered type erasure in Swift even if you didn't recognize it. Two common examples are `AnyHashable` and `AnyCancellable`.

*   **`AnyHashable`**: This struct wraps any type that conforms to the `Hashable` protocol, allowing you to store different `Hashable` types (like `Int`, `String`, `UUID`, etc.) in a single `Set` or use them as keys in a `Dictionary`. Without `AnyHashable`, you'd be restricted to `Set<Int>` or `Dictionary<String, ...>`.
*   **`AnyCancellable`**: Part of the Combine framework, `AnyCancellable` wraps any `Cancellable` instance. This is crucial because Combine's operators return various concrete `Cancellable` types. `AnyCancellable` provides a unified way to store and manage subscriptions without exposing their intricate underlying types.

These are excellent examples of how type erasure solves common problems in Swift's standard library and frameworks.

## When to Use Type Erasure

Type erasure is a powerful tool, but like any powerful tool, it should be used judiciously.

### Good Use Cases:

1.  **Heterogeneous Collections**: As demonstrated, this is the primary reason. When you need to store multiple concrete types that conform to a protocol with associated types in a single array, set, or dictionary.
2.  **Function Return Types**: When a function needs to return an instance conforming to a protocol with associated types, but you don't want to expose the specific concrete type, and `some Protocol` isn't suitable (e.g., if the concrete type can vary based on runtime conditions, or if it's a stored property).
3.  **Module Boundaries**: To create clear abstraction layers between different modules or components. A module can expose an `AnyXYZ` type, allowing consumers to interact with it via a fixed interface without coupling to the internal concrete implementations.
4.  **Dependency Injection**: When injecting dependencies that conform to protocols with associated types, type erasure can simplify the dependency graph by providing a stable, erased type.

### Considerations and Trade-offs:

1.  **Increased Complexity**: Introducing a type-erased wrapper adds another layer of abstraction and boilerplate code. It can make the code slightly harder to read and debug if not well-documented.
2.  **Runtime Overhead**: Type erasure involves dynamic dispatch (calling methods through a closure or vtable), which has a minor runtime performance cost compared to direct method calls. For most applications, this overhead is negligible, but it's worth being aware of in performance-critical sections.
3.  **Loss of Specificity**: Once a type is erased, you lose compile-time knowledge of its original concrete type. You cannot, for example, cast an `AnyValidator<String>` back to `EmailValidator` without a runtime check (`as? EmailValidator`) which defeats some of the compile-time safety benefits.

## Comparison: Before vs. After Type Erasure

Let's visualize the impact of type erasure:

```
Problem (Before Type Erasure):
┌─────────────────────────┐     ┌─────────────────────────┐
│     EmailValidator      │     │    PasswordValidator    │
│   (Validator, Value=Str)│     │  (Validator, Value=Str) │
└─────────────────────────┘     └─────────────────────────┘
            │                           │
            └───────────┬───────────────┘
                        │
                  Compiler Error
                        │
┌─────────────────────────┐
│  let validators:        │  <-- Cannot store different
│  [any Validator]        │      concrete types directly
└─────────────────────────┘

Solution (After Type Erasure):
┌─────────────────────────┐     ┌─────────────────────────┐
│     EmailValidator      │     │    PasswordValidator    │
│   (Validator, Value=Str)│     │  (Validator, Value=Str) │
└─────────────────────────┘     └─────────────────────────┘
            │                           │
            ▼                           ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│  AnyValidator<String>   │     │  AnyValidator<String>   │
│ (wraps EmailValidator)  │     │ (wraps PasswordValidator)│
└─────────────────────────┘     └─────────────────────────┘
            │                           │
            └───────────┬───────────────┘
                        ▼
┌─────────────────────────┐
│  let validators:        │  <-- Works! Heterogeneous
│  [AnyValidator<String>] │      collection of wrappers
└─────────────────────────┘
```

## Summary

Type erasure is an advanced Swift pattern that empowers you to work with protocols that have associated types in scenarios where Swift's type system would otherwise prevent it, primarily in heterogeneous collections or as function return types. By introducing a generic wrapper that captures the underlying type's behavior, you can achieve flexibility and maintain type safety. While it adds a layer of abstraction and a minimal runtime cost, it's an indispensable tool for building robust and modular Swift applications, especially when dealing with complex architectural patterns.

Happy Swifting!
