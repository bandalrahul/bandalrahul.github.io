---
title: Understanding Computed Properties in Swift
date: 2026-10-30 15:37
description: Explore Swift's computed properties, how they differ from stored properties, and master their practical use with getters and setters in your iOS apps.
tags: Swift, iOS, Programming
---

# Understanding Computed Properties in Swift

As Swift developers, we constantly work with properties to store and manage data within our types. While *stored properties* are straightforward data holders, Swift offers a powerful alternative for values that need to be calculated rather than directly stored: *computed properties*. These properties don't store a value themselves; instead, they provide a getter to retrieve a value and an optional setter to indirectly modify other stored properties.

Understanding computed properties is fundamental to writing clean, efficient, and expressive Swift code. They allow you to derive values, perform transformations, and maintain consistency across your data models without cluttering them with unnecessary storage. In this article, we'll dive deep into computed properties, exploring their syntax, use cases, and how they differ from other property behaviors in Swift.

## Stored Properties vs. Computed Properties: The Core Difference

Before we get into the nitty-gritty of computed properties, let's clarify how they differ from their more common counterparts: stored properties.

**Stored Properties** are exactly what they sound like: they store a value as part of an instance of a class or structure. When you declare a variable or constant property, it typically becomes a stored property. They occupy a certain amount of memory for each instance, and their value is directly accessible and modifiable (if `var`).

**Computed Properties**, on the other hand, do not store a value. Instead, they provide a `getter` (to retrieve a value) and an optional `setter` (to set a value). The value they "return" is calculated every time it's accessed, based on other stored properties or external data. This means they don't take up any additional memory for storage themselves, only for the code that defines their getter and setter logic.

Think of it this way: a stored property is like a physical box holding an item, while a computed property is like a recipe that tells you how to make an item from ingredients you already have.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Comparison of Stored Properties and Computed Properties in Swift">
  <title>Stored Property vs. Computed Property</title>

  <!-- Stored Property Box -->
  <rect x="50" y="40" width="220" height="150" rx="10" ry="10" fill="#E0F2F1" stroke="#2A8367" stroke-width="2"/>
  <text x="160" y="70" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="#2A8367" text-anchor="middle">Stored Property</text>
  <text x="160" y="110" font-family="Arial, sans-serif" font-size="16" fill="#333" text-anchor="middle">Holds a specific value</text>
  <text x="160" y="140" font-family="Arial, sans-serif" font-size="16" fill="#333" text-anchor="middle">Occupies memory</text>
  <text x="160" y="170" font-family="Arial, sans-serif" font-size="16" fill="#333" text-anchor="middle">Can have observers</text>

  <!-- Arrow -->
  <line x1="280" y1="115" x2="320" y2="115" stroke="#1565c0" stroke-width="3" marker-end="url(#arrowhead)"/>
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#1565c0" />
    </marker>
  </defs>

  <!-- Computed Property Box -->
  <rect x="330" y="40" width="220" height="150" rx="10" ry="10" fill="#E3F2FD" stroke="#1565c0" stroke-width="2"/>
  <text x="440" y="70" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="#1565c0" text-anchor="middle">Computed Property</text>
  <text x="440" y="110" font-family="Arial, sans-serif" font-size="16" fill="#333" text-anchor="middle">Calculates a value</text>
  <text x="440" y="140" font-family="Arial, sans-serif" font-size="16" fill="#333" text-anchor="middle">No dedicated storage</text>
  <text x="440" y="170" font-family="Arial, sans-serif" font-size="16" fill="#333" text-anchor="middle">Uses `get` and `set`</text>
</svg>
</div>

## Basic Syntax: Getters and Setters

Computed properties are declared using the `var` keyword (they cannot be `let` because their value can change based on the underlying stored properties, even if they don't store it themselves). They require a type annotation and a block containing a `get` clause, and optionally a `set` clause.

Here’s a classic example: a `Temperature` struct that can convert between Celsius and Fahrenheit.

```swift
struct Temperature {
    var celsius: Double // A stored property

    var fahrenheit: Double { // A computed property
        get {
            return (celsius * 9 / 5) + 32
        }
        set(newFahrenheit) { // The setter takes a parameter for the new value
            celsius = (newFahrenheit - 32) * 5 / 9
        }
    }

    var kelvin: Double { // Another computed property, read-only
        return celsius + 273.15
    }
}

var currentTemp = Temperature(celsius: 25)
print("Celsius: \(currentTemp.celsius)°C")       // Output: Celsius: 25.0°C
print("Fahrenheit: \(currentTemp.fahrenheit)°F") // Output: Fahrenheit: 77.0°F
print("Kelvin: \(currentTemp.kelvin)K")           // Output: Kelvin: 298.15K

currentTemp.fahrenheit = 98.6 // Use the setter
print("New Celsius: \(currentTemp.celsius)°C")   // Output: New Celsius: 37.0°C
print("New Fahrenheit: \(currentTemp.fahrenheit)°F") // Output: New Fahrenheit: 98.6°F
```

In this example:
*   `celsius` is a stored property.
*   `fahrenheit` is a computed property with both a `getter` and a `setter`.
    *   The `get` block calculates and returns the Fahrenheit equivalent of the `celsius` value.
    *   The `set` block takes a `newFahrenheit` value and uses it to update the underlying `celsius` stored property.
*   `kelvin` is a read-only computed property, only providing a `get` block.

### Shorthand Setter Declaration

In the `set` block, the new value being assigned to the computed property is automatically available as `newValue`. You can omit the parameter name in the `set` declaration, and Swift will provide `newValue` by default.

```swift
struct Temperature {
    var celsius: Double

    var fahrenheit: Double {
        get {
            return (celsius * 9 / 5) + 32
        }
        set { // 'newValue' is implicitly available here
            celsius = (newValue - 32) * 5 / 9
        }
    }
}
```

This shorthand is commonly used for brevity.

### Read-Only Computed Properties

If a computed property only has a `getter` and no `setter`, it's considered a **read-only computed property**. These are very common for deriving values that shouldn't be directly set.

You can simplify the declaration of a read-only computed property even further by omitting the `get` keyword and its braces entirely, as long as the entire body of the property is just its getter logic.

```swift
struct Person {
    var firstName: String
    var lastName: String

    // Read-only computed property (full syntax)
    var fullNameVerbose: String {
        get {
            return "\(firstName) \(lastName)"
        }
    }

    // Read-only computed property (shorthand syntax)
    var fullName: String {
        "\(firstName) \(lastName)" // Implicit 'return' for single-expression getters
    }

    var initials: String {
        "\(firstName.first ?? Character(" "))\(lastName.first ?? Character(" "))"
    }
}

let user = Person(firstName: "Rahul", lastName: "Sharma")
print(user.fullName)   // Output: Rahul Sharma
print(user.initials)   // Output: R S
// user.fullName = "Jane Doe" // This would result in a compile-time error
```

The `fullName` property is a perfect example of how read-only computed properties provide a convenient interface to derived data without exposing the underlying storage or logic.

## Computed Properties vs. Property Observers

A common point of confusion for new Swift developers is distinguishing between computed properties and property observers (`willSet` and `didSet`). While both involve code execution when a property is accessed or changed, their purposes are fundamentally different:

*   **Computed Properties**: Calculate a value on demand. They do *not* store a value themselves. Their `get` and `set` blocks define *how* the value is computed or *how* other stored properties are affected when an attempt is made to "set" the computed property. They are declared with `var` and a `{ get { ... } set { ... } }` block.

*   **Property Observers (`willSet` and `didSet`)**: Respond to changes in a *stored property*. They are attached to stored properties (or overridden stored properties of a superclass) and are called *before* (`willSet`) or *after* (`didSet`) the stored property's value is changed. They do not calculate or define the property's value; they merely react to its modification.

Here's a visual to help distinguish them:

```
┌───────────────────┐        ┌───────────────────────┐
│  Stored Properties  │        │  Computed Properties  │
├───────────────────┤        ├───────────────────────┤
│ - Holds a value     │        │ - Calculates a value    │
│ - Occupies memory   │        │ - No dedicated storage  │
│ - Can use `willSet` │        │ - Uses `get` for retrieval│
│ - Can use `didSet`  │        │ - Uses `set` for updates  │
│ (Responds to change)│        │ (Defines logic)       │
└───────────────────┘        └───────────────────────┘
```

You cannot attach property observers to computed properties because computed properties don't actually *store* a value for observers to observe. If you need to react to changes that affect a computed property, you would attach observers to the *stored properties* that the computed property depends on.

## When to Use Computed Properties

Computed properties are incredibly versatile and should be used whenever a property's value can be logically derived from other existing data rather than being stored independently. Here are some common scenarios:

1.  **Derived Values**: When a property's value is a direct calculation or transformation of one or more other properties. Examples include:
    *   `area` of a `Rectangle` from its `width` and `height`.
    *   `age` of a `Person` from their `birthDate`.
    *   `fullName` from `firstName` and `lastName`.

2.  **Unit Conversions**: Like our `Temperature` example, when you need to represent a value in different units (e.g., meters vs. feet, Celsius vs. Fahrenheit).

3.  **Convenience Accessors**: To provide a more convenient or user-friendly way to access or modify underlying data, potentially involving complex logic.

4.  **Data Validation/Transformation on Setting**: When a property is set, you might want to perform validation or transform the input before storing it in an underlying private stored property.

5.  **Simplifying Complex Logic**: Encapsulating complex logic within a property makes your code cleaner and easier to read.

## Practical Example: User Profile Progress

Let's consider a `UserProfile` struct in an iOS app. We might want to display a progress bar showing how complete a user's profile is, based on various stored properties. This is a perfect use case for a read-only computed property.

```swift
import Foundation // For URL

struct UserProfile {
    var username: String = ""
    var email: String = ""
    var profilePictureURL: URL?
    var bio: String?
    var phoneNumber: String?
    var hasCompletedOnboarding: Bool = false

    // A read-only computed property to calculate profile completion percentage
    var profileCompletionPercentage: Double {
        var completedSteps = 0
        let totalSteps = 6 // Total potential steps for profile completion

        if !username.isEmpty { completedSteps += 1 }
        if !email.isEmpty { completedSteps += 1 }
        if profilePictureURL != nil { completedSteps += 1 }
        if bio != nil && !bio!.isEmpty { completedSteps += 1 }
        if phoneNumber != nil && !phoneNumber!.isEmpty { completedSteps += 1 }
        if hasCompletedOnboarding { completedSteps += 1 }

        return (Double(completedSteps) / Double(totalSteps)) * 100
    }
}

var newUserProfile = UserProfile()
print("Initial profile completion: \(newUserProfile.profileCompletionPercentage)%") // Output: 0.0%

newUserProfile.username = "swift_rahul"
newUserProfile.email = "rahul@example.com"
newUserProfile.profilePictureURL = URL(string: "https://example.com/pic.png")

print("After basic info: \(newUserProfile.profileCompletionPercentage)%") // Output: 50.0%

newUserProfile.bio = "iOS developer passionate about Swift."
newUserProfile.hasCompletedOnboarding = true

print("After more updates: \(newUserProfile.profileCompletionPercentage)%") // Output: 83.333...%
```

In this example, `profileCompletionPercentage` is a computed property that aggregates the state of several stored properties and provides a single, meaningful value. It recalculates every time it's accessed, ensuring it always reflects the current profile status.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 700 280" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Data flow for a computed property deriving value from multiple stored properties">
  <title>Computed Property Data Flow: User Profile Progress</title>

  <!-- Input Properties -->
  <rect x="50" y="20" width="100" height="40" rx="5" ry="5" fill="#F0F4C3" stroke="#2A8367" stroke-width="1"/>
  <text x="100" y="45" font-family="Arial, sans-serif" font-size="14" fill="#333" text-anchor="middle">username</text>

  <rect x="50" y="70" width="100" height="40" rx="5" ry="5" fill="#F0F4C3" stroke="#2A8367" stroke-width="1"/>
  <text x="100" y="95" font-family="Arial, sans-serif" font-size="14" fill="#333" text-anchor="middle">email</text>

  <rect x="50" y="120" width="100" height="40" rx="5" ry="5" fill="#F0F4C3" stroke="#2A8367" stroke-width="1"/>
  <text x="100" y="145" font-family="Arial, sans-serif" font-size="14" fill="#333" text-anchor="middle">bio</text>

  <rect x="50" y="170" width="100" height="40" rx="5" ry="5" fill="#F0F4C3" stroke="#2A8367" stroke-width="1"/>
  <text x="100" y="195" font-family="Arial, sans-serif" font-size="14" fill="#333" text-anchor="middle">hasCompletedOnboarding</text>

  <!-- Arrows to Calculation Logic -->
  <line x1="150" y1="40" x2="250" y2="120" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowhead2)"/>
  <line x1="150" y1="90" x2="250" y2="120" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowhead2)"/>
  <line x1="150" y1="140" x2="250" y2="120" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowhead2)"/>
  <line x1="150" y1="190" x2="250" y2="120" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowhead2)"/>

  <!-- Calculation Logic Box -->
  <rect x="250" y="90" width="200" height="60" rx="10" ry="10" fill="#E3F2FD" stroke="#1565c0" stroke-width="2"/>
  <text x="350" y="125" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#1565c0" text-anchor="middle">Calculation Logic</text>
  <text x="350" y="145" font-family="Arial, sans-serif" font-size="12" fill="#333" text-anchor="middle">(Count completed steps)</text>


  <!-- Arrow to Output -->
  <line x1="450" y1="120" x2="550" y2="120" stroke="#1565c0" stroke-width="3" marker-end="url(#arrowhead2)"/>
  <defs>
    <marker id="arrowhead2" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#1565c0" />
    </marker>
  </defs>

  <!-- Output Computed Property -->
  <rect x="550" y="90" width="120" height="60" rx="10" ry="10" fill="#E0F2F1" stroke="#2A8367" stroke-width="2"/>
  <text x="610" y="125" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#2A8367" text-anchor="middle">profileCompletionPercentage</text>

</svg>
</div>

## Type Computed Properties

Just like stored properties, computed properties can also be associated with the type itself, rather than with an instance of that type. These are called **type computed properties** and are declared with the `static` keyword for structs and enums, or `class` for classes (which allows subclasses to override the implementation).

```swift
struct MathConstants {
    static var pi: Double {
        return 3.1415926535
    }

    static var e: Double {
        return 2.7182818284
    }

    static var goldenRatio: Double {
        return (1 + sqrt(5)) / 2
    }
}

print("Pi: \(MathConstants.pi)") // Output: Pi: 3.1415926535
print("Golden Ratio: \(MathConstants.goldenRatio)") // Output: Golden Ratio: 1.618033988749895
```

Type computed properties are useful for values that are logically tied to the type itself, and might involve some calculation, but don't need to be stored individually for each instance.

## Summary

Computed properties are a powerful feature in Swift that allow you to define properties whose values are calculated on demand rather than stored. They promote cleaner code by encapsulating derivation logic, prevent data redundancy, and ensure that your derived values are always up-to-date.

Key takeaways:
*   Computed properties provide a `get` block to retrieve a value and an optional `set` block to modify underlying stored properties.
*   They do not store a value themselves, thus saving memory for redundant data.
*   Read-only computed properties are common and can be declared with a concise shorthand.
*   They are distinct from property observers, which react to changes in *stored* properties.
*   Use them for derived values, unit conversions, convenience accessors, and encapsulating complex logic.

Mastering computed properties will significantly enhance your ability to design robust and expressive data models in Swift, leading to more maintainable and efficient iOS applications.

Happy Swifting!
