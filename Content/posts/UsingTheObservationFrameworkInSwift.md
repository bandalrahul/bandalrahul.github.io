---
title: Using the Observation Framework in Swift
date: 2026-07-01 11:54
description: Dive into Swift's Observation framework for simpler, more performant state management in SwiftUI, replacing @ObservableObject and @Published.
tags: Swift, iOS, SwiftUI
---

# Using the Observation Framework in Swift

For years, managing mutable state and reacting to its changes in SwiftUI has largely relied on Combine's `ObservableObject` protocol and the `@Published` property wrapper. While functional, this approach often felt a bit heavy, requiring boilerplate and sometimes leading to less granular updates than desired.

With Swift 5.9 and iOS 17, Apple introduced the **Observation framework**, a powerful new way to observe changes in your data models. This framework brings a more streamlined, performant, and Swifty approach to state management, deeply integrated with the language and SwiftUI. If you've been looking for a simpler way to build reactive UIs, you're in for a treat!

In this article, we'll explore the Observation framework, understand its core components, and see how it revolutionizes state management in SwiftUI.

## The Evolution of State Management: Before and After `@Observable`

Before the Observation framework, if you wanted a class to publish changes to its properties so SwiftUI views could react, you'd typically conform to the `ObservableObject` protocol and mark your properties with `@Published`.

Consider a simple `UserProfile` class:

```swift
import Foundation
import Combine

class UserProfile: ObservableObject {
    @Published var username: String
    @Published var email: String
    @Published var isActive: Bool
    
    init(username: String, email: String, isActive: Bool) {
        self.username = username
        self.email = email
        self.isActive = isActive
    }
    
    func toggleActivity() {
        isActive.toggle()
    }
}
```

This setup works, but it has a few characteristics:
*   **Boilerplate**: You need `ObservableObject` conformance and `@Published` for each property.
*   **Combine Dependency**: It relies on Combine, which is a powerful framework but might be overkill for simple state observation.
*   **Performance**: `@Published` uses `willSet` internally, which means any property marked `@Published` will trigger `objectWillChange.send()` *before* the property actually changes. This can sometimes lead to broader invalidations than necessary.

The Observation framework offers a dramatically simpler and more efficient alternative using the `@Observable` macro.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 700 250" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Comparison of ObservableObject with @Published versus @Observable macro">
  <title>ObservableObject vs. @Observable</title>

  <!-- Title for the diagram -->
  <text x="350" y="30" font-family="Arial, sans-serif" font-size="20" font-weight="bold" text-anchor="middle" fill="#333">State Management Evolution</text>

  <!-- Left Side: ObservableObject -->
  <rect x="50" y="60" width="280" height="170" rx="10" ry="10" fill="#F0F0F0" stroke="#F04B3E" stroke-width="2"/>
  <text x="190" y="85" font-family="Arial, sans-serif" font-size="16" font-weight="bold" text-anchor="middle" fill="#F04B3E">Before: ObservableObject & @Published</text>

  <rect x="70" y="100" width="240" height="40" rx="5" ry="5" fill="#FFF" stroke="#CCC"/>
  <text x="190" y="125" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">class MyModel: ObservableObject {</text>

  <rect x="70" y="145" width="240" height="40" rx="5" ry="5" fill="#FFF" stroke="#CCC"/>
  <text x="190" y="170" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">  @Published var value: String</text>

  <rect x="70" y="190" width="240" height="40" rx="5" ry="5" fill="#FFF" stroke="#CCC"/>
  <text x="190" y="215" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">}</text>

  <!-- Arrow in the middle -->
  <line x1="335" y1="145" x2="365" y2="145" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowhead)"/>
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#1565c0" />
    </marker>
  </defs>
  <text x="350" y="130" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#1565c0">Simpler</text>
  <text x="350" y="165" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#1565c0">Faster</text>


  <!-- Right Side: @Observable -->
  <rect x="370" y="60" width="280" height="170" rx="10" ry="10" fill="#F0F0F0" stroke="#2A8367" stroke-width="2"/>
  <text x="510" y="85" font-family="Arial, sans-serif" font-size="16" font-weight="bold" text-anchor="middle" fill="#2A8367">After: @Observable Macro</text>

  <rect x="390" y="100" width="240" height="40" rx="5" ry="5" fill="#FFF" stroke="#CCC"/>
  <text x="510" y="125" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">@Observable</text>

  <rect x="390" y="145" width="240" height="40" rx="5" ry="5" fill="#FFF" stroke="#CCC"/>
  <text x="510" y="170" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">class MyModel {</text>

  <rect x="390" y="190" width="240" height="40" rx="5" ry="5" fill="#FFF" stroke="#CCC"/>
  <text x="510" y="215" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">  var value: String</text>

  <rect x="390" y="235" width="240" height="0" rx="5" ry="5" fill="#FFF" stroke="#CCC"/>
  <text x="510" y="215" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">}</text>

</svg>
</div>

## Introducing `@Observable`

The `@Observable` macro is the cornerstone of the new framework. You apply it to a class, and the Swift compiler automatically synthesizes the necessary code to make its properties observable. This means you no longer need `ObservableObject` conformance or `@Published` property wrappers.

Let's refactor our `UserProfile` class using `@Observable`:

```swift
import Foundation
import Observation // Import the Observation framework

@Observable
class UserProfile {
    var username: String
    var email: String
    var isActive: Bool
    
    init(username: String, email: String, isActive: Bool) {
        self.username = username
        self.email = email
        self.isActive = isActive
    }
    
    func toggleActivity() {
        isActive.toggle()
    }
}
```

Notice the difference:
*   We've added `@Observable` above the class definition.
*   We removed `ObservableObject` conformance.
*   We removed `@Published` from the properties. They are now just regular `var` properties.
*   We need to `import Observation`.

That's it! The compiler now handles all the plumbing to make `UserProfile`'s properties observable. This significantly reduces boilerplate and makes your model code cleaner and easier to read.

### How `@Observable` Works Internally (Simplified)

When you mark a class with `@Observable`, the macro transforms your code. Essentially, it injects code that:
1.  Provides a mechanism for observers to register interest in property changes.
2.  Notifies registered observers whenever one of its observed properties changes.

Crucially, this observation is **fine-grained**. Instead of notifying for *any* change (as `objectWillChange` effectively does), the Observation framework tracks *which specific properties* are accessed within an observing context (like a SwiftUI view's `body`) and only notifies when *those specific properties* change. This leads to more efficient updates.

## Integrating `@Observable` with SwiftUI

The Observation framework is designed to integrate seamlessly with SwiftUI. SwiftUI views automatically become observing contexts. When an `@Observable` object's property is accessed within a view's `body`, SwiftUI automatically registers that property for observation. If that property later changes, SwiftUI knows to re-render only the parts of the view that depend on it.

To use an `@Observable` class in SwiftUI, you typically use `@State` for local, view-owned observable objects, or `@Bindable` for observed objects that might be passed around or need two-way binding.

Let's create a SwiftUI view that uses our `UserProfile`:

```swift
import SwiftUI
import Observation

struct UserProfileView: View {
    // For view-owned observable objects
    @State private var userProfile = UserProfile(username: "Rahul", email: "rahul@example.com", isActive: true)
    
    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("User Profile")
                .font(.largeTitle)
                .padding(.bottom)
            
            HStack {
                Text("Username:")
                // Accessing properties directly makes SwiftUI observe them
                Text(userProfile.username)
                    .fontWeight(.semibold)
            }
            
            HStack {
                Text("Email:")
                Text(userProfile.email)
                    .fontWeight(.semibold)
            }
            
            Toggle(isOn: $userProfile.isActive) { // Using $ for two-way binding
                Text("Active:")
            }
            .tint(userProfile.isActive ? .green : .red)
            .padding(.vertical)
            
            Button("Update Username") {
                userProfile.username = "Rahul \(Int.random(in: 100...999))"
            }
            .buttonStyle(.borderedProminent)
            
            Button("Toggle Activity") {
                userProfile.toggleActivity()
            }
            .buttonStyle(.bordered)
        }
        .padding()
    }
}

#Preview {
    UserProfileView()
}
```

Here's how it works:
*   `@State private var userProfile = UserProfile(...)`: We declare an instance of our `@Observable` `UserProfile` class using `@State`. This tells SwiftUI to manage the lifetime of this object and re-render the view when its *observed* properties change.
*   `Text(userProfile.username)`: When `userProfile.username` is accessed, SwiftUI registers that this view depends on `username`. If `username` changes, only the parts of the view that access `username` (or its dependencies) will be re-evaluated.
*   `Toggle(isOn: $userProfile.isActive)`: For two-way binding with properties of an `@Observable` object, you use the new `@Bindable` property wrapper implicitly via the `$` syntax. SwiftUI automatically provides a binding to `isActive` which updates the property and triggers view re-renders.

### The `@Bindable` Property Wrapper

While `@State` works for view-owned observable objects, what if you pass an `@Observable` object from a parent view to a child view and want the child to modify it? That's where `@Bindable` comes in explicitly.

```swift
struct ChildProfileEditor: View {
    @Bindable var profile: UserProfile // Use @Bindable for passed-in observable objects
    
    var body: some View {
        VStack {
            TextField("Username", text: $profile.username)
                .textFieldStyle(.roundedBorder)
            
            Toggle("Active", isOn: $profile.isActive)
                .tint(.blue)
        }
        .padding()
    }
}

struct ParentView: View {
    @State private var mainUserProfile = UserProfile(username: "Master User", email: "master@example.com", isActive: true)
    
    var body: some View {
        VStack {
            Text("Current Username: \(mainUserProfile.username)")
            ChildProfileEditor(profile: mainUserProfile) // Pass the observable object directly
        }
    }
}
```

By using `@Bindable`, `ChildProfileEditor` can create bindings to `profile.username` and `profile.isActive` and modify them, with changes propagating back to `mainUserProfile` in `ParentView` and triggering updates.

```
┌─────────────────┐     ┌───────────────────┐
│  SwiftUI View   │     │  @Observable      │
│  (e.g., Parent) │ ────►│  MyDataModel      │
│  @State var     │     │  (e.g., UserProfile)│
└─────────────────┘     └───────────────────┘
         │
         │ (Passes via @Bindable)
         ▼
┌─────────────────┐
│  SwiftUI View   │
│  (e.g., Child)  │
│  @Bindable var  │
└─────────────────┘
```

This diagram illustrates how a SwiftUI View, specifically a `ParentView` holding an `@Observable` `MyDataModel` via `@State`, can pass that model down to a `ChildView` using `@Bindable`. The `ChildView` can then observe and modify the model, with changes propagating back up and causing relevant UI updates.

## Manual Observation with `withObservationTracking`

While SwiftUI automatically handles observation for you, there are scenarios where you might need to manually track changes to an `@Observable` object outside of a SwiftUI view or for specific side effects. The Observation framework provides the `withObservationTracking` function for this purpose.

`withObservationTracking` takes two closures:
1.  `_ body: () -> R`: A closure where you access the observable properties you want to track.
2.  `onChange: () -> Void`: A closure that will be executed whenever any of the properties accessed in the `body` closure change.

Let's see an example:

```swift
import Foundation
import Observation

@Observable
class Stock {
    var symbol: String
    var price: Double
    var volume: Int
    
    init(symbol: String, price: Double, volume: Int) {
        self.symbol = symbol
        self.price = price
        self.volume = volume
    }
}

func monitorStockPrice() {
    let appleStock = Stock(symbol: "AAPL", price: 170.50, volume: 10_000_000)
    
    print("Monitoring \(appleStock.symbol) price...")
    
    // Track changes to appleStock.price
    withObservationTracking {
        // Access the property we want to track
        _ = appleStock.price 
        print("Initial price observed: \(appleStock.price)")
    } onChange: {
        // This closure is called when appleStock.price changes
        print("Price of \(appleStock.symbol) changed to \(appleStock.price)!")
        // Re-establish tracking, as it's a one-shot observation by default
        monitorStockPrice() 
    }
    
    // Simulate price changes
    DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
        appleStock.price = 172.00 // This will trigger the onChange
    }
    
    DispatchQueue.main.asyncAfter(deadline: .now() + 4) {
        appleStock.volume = 12_000_000 // This will NOT trigger the onChange
        print("Volume changed, but not tracked by this observer.")
    }
    
    DispatchQueue.main.asyncAfter(deadline: .now() + 6) {
        appleStock.price = 171.80 // This will trigger the onChange again if re-tracked
    }
}

// Call the function to start monitoring
// monitorStockPrice() // Uncomment to run in a playground or console app
```

In this example, `onChange` is only triggered when `appleStock.price` changes because that's the only property accessed within the `body` closure of `withObservationTracking`. Changes to `appleStock.volume` are ignored by this specific tracking block.

A key detail is that `withObservationTracking` creates a **one-shot observation**. If you want continuous observation, you need to re-establish the tracking within the `onChange` closure itself, as shown in the example with the recursive call to `monitorStockPrice()`. Be cautious with recursive calls to avoid infinite loops if not properly managed. For long-lived observation, you'd typically store the observation token returned by `withObservationTracking` and invalidate it when no longer needed.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Flowchart of withObservationTracking function">
  <title>withObservationTracking Flow</title>

  <!-- Start Node -->
  <rect x="200" y="20" width="200" height="40" rx="10" ry="10" fill="#1565c0" stroke="#0D47A1" stroke-width="2"/>
  <text x="300" y="45" font-family="Arial, sans-serif" font-size="16" font-weight="bold" text-anchor="middle" fill="#FFFFFF">Call withObservationTracking</text>

  <!-- Arrow 1 -->
  <line x1="300" y1="60" x2="300" y2="90" stroke="#333" stroke-width="2" marker-end="url(#arrowhead-black)"/>
  <defs>
    <marker id="arrowhead-black" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
    </marker>
  </defs>

  <!-- Body Closure -->
  <rect x="100" y="90" width="400" height="50" rx="10" ry="10" fill="#F0F0F0" stroke="#2A8367" stroke-width="2"/>
  <text x="300" y="110" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">1. Execute `body` closure:</text>
  <text x="300" y="130" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">   Access properties of @Observable objects</text>

  <!-- Arrow 2 -->
  <line x1="300" y1="140" x2="300" y2="170" stroke="#333" stroke-width="2" marker-end="url(#arrowhead-black)"/>

  <!-- Decision / OnChange Trigger -->
  <rect x="50" y="170" width="500" height="40" rx="10" ry="10" fill="#F0F0F0" stroke="#F04B3E" stroke-width="2"/>
  <text x="300" y="195" font-family="Arial, sans-serif" font-size="16" font-weight="bold" text-anchor="middle" fill="#333">If any accessed property changes, execute `onChange` closure</text>

</svg>
</div>

## Performance Benefits

One of the most significant advantages of the Observation framework is its performance.
*   **Compiler-Synthesized**: The observation logic is generated by the compiler, often leading to highly optimized code.
*   **Fine-Grained Updates**: Unlike `@Published` which uses `willSet` and broadcasts a general `objectWillChange` notification, `@Observable` tracks *exactly which properties* are accessed within an observing context. This means SwiftUI only re-renders views (or parts of views) that actually depend on the changed data, minimizing unnecessary UI updates.
*   **Reduced Overhead**: Eliminating the Combine dependency for basic observation can reduce framework overhead for simpler use cases.

This fine-grained approach helps improve app responsiveness and battery life, especially in complex UIs with many interwoven data dependencies.

## Key Differences: `@ObservableObject` vs. `@Observable`

Let's summarize the key distinctions to help you decide when and where to use the new framework.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 700 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Comparison table of ObservableObject and Observable framework">
  <title>ObservableObject vs. Observable Framework Comparison</title>

  <!-- Table Header -->
  <rect x="50" y="30" width="280" height="40" fill="#F0F0F0" stroke="#333" stroke-width="1"/>
  <text x="190" y="55" font-family="Arial, sans-serif" font-size="16" font-weight="bold" text-anchor="middle" fill="#F04B3E">ObservableObject & @Published</text>

  <rect x="370" y="30" width="280" height="40" fill="#F0F0F0" stroke="#333" stroke-width="1"/>
  <text x="510" y="55" font-family="Arial, sans-serif" font-size="16" font-weight="bold" text-anchor="middle" fill="#2A8367">Observation Framework (@Observable)</text>

  <!-- Row 1: Conformance -->
  <rect x="50" y="70" width="280" height="50" fill="#FFF" stroke="#CCC" stroke-width="1"/>
  <text x="190" y="90" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">Requires conforming to `ObservableObject`</text>
  <text x="190" y="110" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">and marking properties with `@Published`.</text>

  <rect x="370" y="70" width="280" height="50" fill="#FFF" stroke="#CCC" stroke-width="1"/>
  <text x="510" y="95" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">Just apply `@Observable` macro to the class.</text>

  <!-- Row 2: Underlying Mechanism -->
  <rect x="50" y="120" width="280" height="50" fill="#F9F9F9" stroke="#CCC" stroke-width="1"/>
  <text x="190" y="140" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">Uses Combine publishers (`objectWillChange`).</text>
  <text x="190" y="160" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">Broader notifications.</text>

  <rect x="370" y="120" width="280" height="50" fill="#F9F9F9" stroke="#CCC" stroke-width="1"/>
  <text x="510" y="140" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">Compiler-synthesized observation.</text>
  <text x="510" y="160" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">Fine-grained, targeted notifications.</text>

  <!-- Row 3: SwiftUI Integration -->
  <rect x="50" y="170" width="280" height="50" fill="#FFF" stroke="#CCC" stroke-width="1"/>
  <text x="190" y="190" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">Uses `@ObservedObject`, `@StateObject`,</text>
  <text x="190" y="210" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">`@EnvironmentObject`.</text>

  <rect x="370" y="170" width="280" height="50" fill="#FFF" stroke="#CCC" stroke-width="1"/>
  <text x="510" y="190" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">Uses `@State` (for owned objects), `@Bindable`,</text>
  <text x="510" y="210" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">`@Environment(object:)`.</text>

  <!-- Row 4: Performance -->
  <rect x="50" y="220" width="280" height="50" fill="#F9F9F9" stroke="#CCC" stroke-width="1"/>
  <text x="190" y="240" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">Can lead to broader view invalidations</text>
  <text x="190" y="260" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">due to `objectWillChange`.</text>

  <rect x="370" y="220" width="280" height="50" fill="#F9F9F9" stroke="#CCC" stroke-width="1"/>
  <text x="510" y="240" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">More performant due to fine-grained, targeted</text>
  <text x="510" y="260" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">updates and compiler optimizations.</text>

</svg>
</div>

The Observation framework is a clear step forward for state management in Swift and SwiftUI. While `ObservableObject` and Combine are not deprecated and remain useful for other reactive programming patterns, `@Observable` is the recommended approach for simple data observation in SwiftUI from iOS 17 onwards.

## Summary

The Observation framework, powered by the `@Observable` macro, marks a significant improvement in how we handle mutable state in Swift and SwiftUI. It simplifies our model code by eliminating boilerplate associated with `ObservableObject` and `@Published`, offering a cleaner and more Swifty syntax. Beyond aesthetics, it provides substantial performance benefits through fine-grained observation, ensuring that SwiftUI views only update when their directly accessed dependencies change. With `@State`, `@Bindable`, and `withObservationTracking`, the framework offers robust tools for both automatic SwiftUI integration and manual control over observation, making our apps more efficient and easier to develop.

Happy Swifting!
