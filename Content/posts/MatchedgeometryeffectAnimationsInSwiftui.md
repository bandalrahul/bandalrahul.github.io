---
title: matchedGeometryEffect Animations in SwiftUI
date: 2026-09-21 15:31
description: Learn how to create seamless, identity-based animations between different views and states in SwiftUI using the powerful matchedGeometryEffect modifier.
tags: SwiftUI, iOS, Development
---

# matchedGeometryEffect Animations in SwiftUI

SwiftUI's declarative nature makes creating delightful user interfaces a breeze, and animations are no exception. For many common scenarios, simply wrapping state changes in `withAnimation { ... }` is enough to bring your UI to life. But what happens when you want to animate a view that conceptually "moves" from one position or parent view to another, perhaps even changing its size or shape along the way? Standard `withAnimation` often results in the old view fading out and the new one fading in, breaking the visual continuity.

This is where SwiftUI's powerful `matchedGeometryEffect` modifier comes into play. It's designed specifically for creating smooth, identity-based transitions between views that represent the same underlying content but exist in different layout states or even different view hierarchies. Think of an image thumbnail seamlessly expanding into a full-screen viewer, or an item in a list flying into a detail card. These are the kinds of magical transitions `matchedGeometryEffect` enables.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Conceptual diagram of matchedGeometryEffect animating a view's position and size">
  <title>Conceptual matchedGeometryEffect Animation</title>

  <!-- Before State -->
  <rect x="50" y="80" width="80" height="60" fill="#2A8367" rx="8" ry="8"/>
  <text x="90" y="110" font-family="Arial" font-size="16" fill="white" text-anchor="middle">View A</text>
  <text x="90" y="160" font-family="Arial" font-size="14" fill="#333" text-anchor="middle">Initial State</text>

  <!-- Arrow -->
  <line x1="150" y1="110" x2="450" y2="110" stroke="#1565c0" stroke-width="2" stroke-dasharray="5,5"/>
  <polygon points="440,105 450,110 440,115" fill="#1565c0" />
  <text x="300" y="90" font-family="Arial" font-size="14" fill="#1565c0" text-anchor="middle">matchedGeometryEffect</text>

  <!-- After State -->
  <rect x="470" y="50" width="100" height="120" fill="#F04B3E" rx="8" ry="8"/>
  <text x="520" y="110" font-family="Arial" font-size="16" fill="white" text-anchor="middle">View B</text>
  <text x="520" y="180" font-family="Arial" font-size="14" fill="#333" text-anchor="middle">Final State</text>
</svg>
</div>

## Understanding `matchedGeometryEffect`

At its core, `matchedGeometryEffect` tells SwiftUI: "These two (or more) views are actually the same thing, just presented differently." When a state change causes one view to disappear and another to appear (or change position), SwiftUI will automatically animate the transition of the "matching" view's geometry.

To use `matchedGeometryEffect`, you need three main components:

1.  **A unique `id`**: This is a `Hashable` value that uniquely identifies the view you want to animate. It tells SwiftUI *which* view instances are conceptually the same.
2.  **A `Namespace.ID`**: This acts as a scope or container for your matched animations. All views that should animate together (i.e., share the same `id` for a specific transition) must belong to the same namespace.
3.  **The `matchedGeometryEffect` modifier**: Applied to the views participating in the animation, linking them via their `id` and `namespace`.

Let's look at the signature:

```swift
func matchedGeometryEffect<ID>(
    id: ID,
    in: Namespace.ID,
    properties: MatchedGeometryProperties = .frame,
    anchor: UnitPoint = .center,
    isSource: Bool = true
) -> some View where ID : Hashable
```

-   `id`: The unique identifier for the view.
-   `in`: The namespace for this animation.
-   `properties`: Which geometric properties of the view to animate. The default is `.frame`, which animates both position and size. Other options include `.position`, `.size`, or `.identity` (which animates nothing, useful for setting `isSource` to `false`).
-   `anchor`: The point within the view that acts as the anchor for the animation. Defaults to `.center`.
-   `isSource`: A boolean indicating if this view is the "source" of the animation. If multiple views share the same `id` in a namespace, only one should typically be the source. When the source view is removed, the non-source view will animate from its position. Defaults to `true`.

## Basic Usage Example: A Moving Rectangle

Let's start with a simple example where a rectangle moves from one side of the screen to another and changes size based on a tapped state.

First, you need to declare a namespace. This is typically done as a `@Namespace` property wrapper in the parent view where the animation occurs.

```swift
import SwiftUI

struct MatchedGeometryBasicExample: View {
    @State private var showLargeRectangle = false
    @Namespace private var animationNamespace // Declare the namespace

    var body: some View {
        VStack {
            Spacer()

            if showLargeRectangle {
                Rectangle()
                    .fill(.blue)
                    .frame(width: 200, height: 150)
                    .matchedGeometryEffect(id: "myRectangle", in: animationNamespace) // Source
                    .onTapGesture {
                        withAnimation(.easeInOut(duration: 0.7)) {
                            showLargeRectangle.toggle()
                        }
                    }
            } else {
                Rectangle()
                    .fill(.green)
                    .frame(width: 100, height: 80)
                    .matchedGeometryEffect(id: "myRectangle", in: animationNamespace) // Destination
                    .onTapGesture {
                        withAnimation(.easeInOut(duration: 0.7)) {
                            showLargeRectangle.toggle()
                        }
                    }
            }

            Spacer()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.gray.opacity(0.1))
    }
}

struct MatchedGeometryBasicExample_Previews: PreviewProvider {
    static var previews: some View {
        MatchedGeometryBasicExample()
    }
}
```

In this example:
-   We declare `@Namespace private var animationNamespace`.
-   Both `Rectangle` views use `matchedGeometryEffect(id: "myRectangle", in: animationNamespace)`.
-   When `showLargeRectangle` toggles, one `Rectangle` disappears and the other appears. Because they share the same `id` and `namespace`, SwiftUI understands they are the "same" visual element and animates the transition of their frame (position and size).
-   The `fill` color also changes, but that's not part of `matchedGeometryEffect` itself; SwiftUI's standard animation system handles that.

The `isSource` parameter defaults to `true`. In scenarios where one view is conditionally removed and another appears, like in an `if/else` block, SwiftUI is smart enough to figure out which view is "disappearing" and which is "appearing" and handles the source/destination roles automatically. You typically only need to explicitly set `isSource: false` in more complex scenarios, like when you have multiple instances of a view with the same ID, but only one should be the "primary" animator.

```
┌─────────────────┐
│ @Namespace      │
│ animationNamespace│
└─────────────────┘
         │
         ▼
┌───────────────────────────────────────────────────────────┐
│                     Parent View                           │
│ (e.g., MatchedGeometryBasicExample)                       │
│                                                           │
│ ┌───────────────────────────────────┐                     │
│ │   View 1 (e.g., Small Rectangle)  │                     │
│ │ .matchedGeometryEffect(id: "item", in: animationNamespace)│
│ └───────────────────────────────────┘                     │
│              (When `showLargeRectangle` is false)         │
│                                                           │
│                                                           │
│ ┌───────────────────────────────────┐                     │
│ │   View 2 (e.g., Large Rectangle)  │                     │
│ │ .matchedGeometryEffect(id: "item", in: animationNamespace)│
│ └───────────────────────────────────┘                     │
│              (When `showLargeRectangle` is true)          │
│                                                           │
└───────────────────────────────────────────────────────────┘
         │
         ▼
┌───────────────────────────────────────────────────────────┐
│    SwiftUI Animation Engine                               │
│    - Tracks "item" geometry within "animationNamespace"   │
│    - Animates transition between View 1 and View 2's      │
│      geometry (position, size) when state changes.        │
└───────────────────────────────────────────────────────────┘
```

## Diving Deeper into `properties` and `anchor`

The `properties` parameter is crucial for fine-tuning your animations:

*   `.frame` (default): Animates both the view's position and size. This is the most common choice.
*   `.position`: Animates only the view's center point. The size remains fixed or changes instantly.
*   `.size`: Animates only the view's dimensions. The position remains fixed or changes instantly.
*   `.identity`: Animates nothing. Useful if you want to use the `matchedGeometryEffect` to establish a match but don't want any geometry animation for that specific view (e.g., if another view with the same ID is the primary animator).

The `anchor` parameter determines the point within the view that SwiftUI uses as a reference for the animation. For example, if you animate a view from top-left to bottom-right, and its size also changes, the animation will pivot around the specified anchor.

*   `.center` (default): The animation pivots around the center of the view.
*   `.topLeading`, `.bottomTrailing`, etc.: The animation pivots around the specified corner or edge.

Experimenting with `properties` and `anchor` can lead to subtle but significant differences in the feel of your animations.

## Practical Use Case: Expanding/Collapsing Card

A classic use case for `matchedGeometryEffect` is an item in a list or grid that expands into a full-screen detail view, or a card that flips/expands in place. Let's build a simplified version of an expanding card.

```swift
import SwiftUI

struct ExpandableCardView: View {
    @State private var isExpanded = false
    @Namespace private var cardNamespace

    var body: some View {
        ZStack { // Use ZStack to place views on top of each other
            if isExpanded {
                ExpandedCardView(namespace: cardNamespace, isExpanded: $isExpanded)
                    .zIndex(1) // Ensure expanded view is on top
            } else {
                CollapsedCardView(namespace: cardNamespace, isExpanded: $isExpanded)
                    .zIndex(0) // Ensure collapsed view is below
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.black.opacity(isExpanded ? 0.4 : 0).ignoresSafeArea()) // Dim background
    }
}

struct CollapsedCardView: View {
    let namespace: Namespace.ID
    @Binding var isExpanded: Bool

    var body: some View {
        VStack(alignment: .leading) {
            Image(systemName: "photo.fill")
                .resizable()
                .scaledToFit()
                .frame(width: 80, height: 80)
                .cornerRadius(10)
                .matchedGeometryEffect(id: "cardImage", in: namespace) // Match the image

            Text("Card Title")
                .font(.headline)
                .matchedGeometryEffect(id: "cardTitle", in: namespace) // Match the title

            Text("A short description of the card content.")
                .font(.subheadline)
                .foregroundColor(.gray)
                .lineLimit(1)
                .matchedGeometryEffect(id: "cardDescription", in: namespace) // Match the description
        }
        .padding()
        .frame(width: 180, height: 220, alignment: .topLeading)
        .background(Color.white)
        .cornerRadius(15)
        .shadow(radius: 5)
        .matchedGeometryEffect(id: "cardBackground", in: namespace) // Match the entire card background
        .onTapGesture {
            withAnimation(.spring(response: 0.5, dampingFraction: 0.7, blendDuration: 0)) {
                isExpanded.toggle()
            }
        }
    }
}

struct ExpandedCardView: View {
    let namespace: Namespace.ID
    @Binding var isExpanded: Bool

    var body: some View {
        VStack(alignment: .center) {
            Image(systemName: "photo.fill")
                .resizable()
                .scaledToFit()
                .frame(width: 200, height: 200)
                .cornerRadius(20)
                .matchedGeometryEffect(id: "cardImage", in: namespace) // Match the image

            Text("Detailed Card Title")
                .font(.largeTitle)
                .matchedGeometryEffect(id: "cardTitle", in: namespace) // Match the title

            Text("This is a much longer and more detailed description of the card content. It can span multiple lines and provide more information about the item.")
                .font(.body)
                .padding(.horizontal)
                .multilineTextAlignment(.center)
                .matchedGeometryEffect(id: "cardDescription", in: namespace) // Match the description

            Spacer()

            Button("Close") {
                withAnimation(.spring(response: 0.5, dampingFraction: 0.7, blendDuration: 0)) {
                    isExpanded.toggle()
                }
            }
            .padding()
            .background(Color.blue)
            .foregroundColor(.white)
            .cornerRadius(10)
        }
        .padding()
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.white)
        .cornerRadius(25)
        .shadow(radius: 10)
        .matchedGeometryEffect(id: "cardBackground", in: namespace) // Match the entire card background
    }
}

struct ExpandableCardView_Previews: PreviewProvider {
    static var previews: some View {
        ExpandableCardView()
    }
}
```

In this example:
-   We have two separate views, `CollapsedCardView` and `ExpandedCardView`.
-   Each view contains elements (Image, Text, Text) that are conceptually the same across both states.
-   Each of these matching elements, *as well as the background itself*, gets its own `matchedGeometryEffect` with a unique `id` within the shared `cardNamespace`.
-   When `isExpanded` toggles, SwiftUI animates the geometry of each `id` from its collapsed state to its expanded state (and vice-versa).
-   `ZStack` and `zIndex` are used to ensure the expanded card appears on top of the collapsed card's space during the animation. The dimming background also animates its opacity.

This pattern allows for incredibly fluid and visually appealing transitions, making your app feel polished and responsive.

## Common Pitfalls and Best Practices

While powerful, `matchedGeometryEffect` can sometimes be tricky. Here are some common issues and tips:

1.  **Unique `id`s within a `Namespace`**: Ensure each view that you want to animate *independently* has a unique `id` within its namespace. If two distinct views share the same `id`, SwiftUI won't know which one to animate. If you have a list of items, use the item's unique ID (e.g., `UUID`) for `matchedGeometryEffect`.
2.  **Namespace Scope**: Declare your `@Namespace` at a common ancestor view that encompasses all the views participating in the `matchedGeometryEffect` animation. If the namespace is declared too low in the hierarchy, or if participating views are in different `NavigationView` stacks, it might not work.
3.  **Conditional View Existence**: For `matchedGeometryEffect` to work, the view with a given `id` must logically *exist* in both the "before" and "after" states of the animation. If you use `if someCondition { ViewA } else { ViewB }`, this works perfectly. However, if you completely remove a view (e.g., `if someCondition { ViewA }`), and there's no corresponding "destination" view with the same `id`, no animation will occur.
4.  **Modifier Order**: `matchedGeometryEffect` should generally be applied *after* layout modifiers like `frame`, `padding`, `cornerRadius`, etc. This ensures SwiftUI calculates the correct final geometry before attempting to match it.
    ```swift
    // Good: matchedGeometryEffect applied after frame and padding
    Text("Hello")
        .frame(width: 100, height: 50)
        .padding()
        .matchedGeometryEffect(id: "myText", in: namespace)

    // Potentially problematic if layout modifiers are applied after
    Text("Hello")
        .matchedGeometryEffect(id: "myText", in: namespace)
        .frame(width: 100, height: 50) // This frame might not be animated correctly
    ```
5.  **`zIndex` for Overlapping Views**: When views animate between different positions, they might temporarily overlap. Use the `.zIndex()` modifier to ensure the animating view appears on top of other content, preventing visual glitches. (As seen in the `ExpandableCardView` example).
6.  **Avoid `matchedGeometryEffect` on the same view in different states**: `matchedGeometryEffect` is for animating between *different* views that represent the same conceptual element. Applying it to a single view that merely changes its own frame or position via `@State` will not yield the desired effect; standard `withAnimation` is sufficient there.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 280" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Flow diagram of matchedGeometryEffect usage for a list item to detail view transition">
  <title>MatchedGeometryEffect Flow for List to Detail</title>

  <!-- List View -->
  <rect x="50" y="30" width="200" height="220" rx="10" ry="10" fill="#E0E0E0" stroke="#333" stroke-width="1"/>
  <text x="150" y="55" font-family="Arial" font-size="16" fill="#333" text-anchor="middle">List View</text>

  <!-- List Item 1 -->
  <rect x="60" y="70" width="180" height="40" rx="5" ry="5" fill="#2A8367"/>
  <text x="150" y="95" font-family="Arial" font-size="14" fill="white" text-anchor="middle">Item 1</text>
  <rect x="60" y="70" width="180" height="40" rx="5" ry="5" fill="none" stroke="#1565c0" stroke-dasharray="3,3" stroke-width="1"/>
  <text x="150" y="125" font-family="Arial" font-size="12" fill="#1565c0" text-anchor="middle">.matchedGeometryEffect(id: item.id, in: namespace)</text>


  <!-- List Item 2 -->
  <rect x="60" y="130" width="180" height="40" rx="5" ry="5" fill="#2A8367"/>
  <text x="150" y="155" font-family="Arial" font-size="14" fill="white" text-anchor="middle">Item 2</text>
  
  <!-- List Item 3 -->
  <rect x="60" y="190" width="180" height="40" rx="5" ry="5" fill="#2A8367"/>
  <text x="150" y="215" font-family="Arial" font-size="14" fill="white" text-anchor="middle">Item 3</text>

  <!-- Arrow to Detail View -->
  <line x1="250" y1="90" x2="350" y2="90" stroke="#1565c0" stroke-width="2"/>
  <polygon points="340,85 350,90 340,95" fill="#1565c0" />
  <text x="300" y="75" font-family="Arial" font-size="12" fill="#1565c0" text-anchor="middle">Tap Item</text>

  <!-- Detail View -->
  <rect x="380" y="30" width="200" height="220" rx="10" ry="10" fill="#E0E0E0" stroke="#333" stroke-width="1"/>
  <text x="480" y="55" font-family="Arial" font-size="16" fill="#333" text-anchor="middle">Detail View</text>

  <!-- Detail View of Item 1 -->
  <rect x="390" y="70" width="180" height="160" rx="5" ry="5" fill="#F04B3E"/>
  <text x="480" y="100" font-family="Arial" font-size="14" fill="white" text-anchor="middle">Expanded Item 1</text>
  <text x="480" y="130" font-family="Arial" font-size="12" fill="white" text-anchor="middle">More details...</text>
  <rect x="390" y="70" width="180" height="160" rx="5" ry="5" fill="none" stroke="#1565c0" stroke-dasharray="3,3" stroke-width="1"/>
  <text x="480" y="245" font-family="Arial" font-size="12" fill="#1565c0" text-anchor="middle">.matchedGeometryEffect(id: item.id, in: namespace)</text>

</svg>
</div>

## Summary

`matchedGeometryEffect` is an incredibly powerful tool in SwiftUI's animation arsenal, enabling you to create fluid and visually continuous transitions between different views that represent the same content. By leveraging a shared `id` and `Namespace.ID`, you can easily animate changes in position, size, and other geometric properties, significantly enhancing the user experience of your iOS applications. Remember to manage your namespaces, ensure unique IDs, and consider the order of modifiers for the best results.

Happy Swifting!
