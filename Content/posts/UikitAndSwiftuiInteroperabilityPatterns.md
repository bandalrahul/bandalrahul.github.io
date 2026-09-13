---
title: UIKit and SwiftUI Interoperability Patterns
date: 2026-09-13 13:33
description: Learn how to seamlessly integrate UIKit and SwiftUI in your iOS apps, embedding each framework within the other using UIHostingController, UIViewRepresentable, and UIViewControllerRepresentable.
tags: UIKit, SwiftUI, iOS
---

# UIKit and SwiftUI Interoperability Patterns

As iOS developers, we often find ourselves working on projects that started in the UIKit era but are now embracing SwiftUI for new features and UI components. Or perhaps you're building a new app in SwiftUI but need to leverage a complex, existing UIKit component or a third-party library that doesn't yet have a SwiftUI equivalent. In these scenarios, knowing how to seamlessly integrate UIKit and SwiftUI is not just a "nice-to-have" skill – it's essential.

This article will guide you through the core patterns for interoperability, demonstrating how to embed SwiftUI views within UIKit view hierarchies and vice versa. We'll explore `UIHostingController`, `UIViewRepresentable`, and `UIViewControllerRepresentable`, along with strategies for handling data flow and events across the framework boundary.

## Embedding SwiftUI in UIKit with `UIHostingController`

The most common scenario for integrating SwiftUI into an existing UIKit application is when you want to use a new SwiftUI-powered component within a `UIViewController` or `UIView`. Apple provides `UIHostingController` specifically for this purpose.

`UIHostingController` is a subclass of `UIViewController` that acts as a container for a SwiftUI view hierarchy. You simply initialize it with your root SwiftUI view, and then you can embed its view (`hostingController.view`) into any UIKit view hierarchy, just like any other `UIView`.

Here's how you can use it:

```swift
import UIKit
import SwiftUI

// Our SwiftUI View
struct MySwiftUIComponent: View {
    @State private var counter = 0
    let title: String
    var onIncrement: ((Int) -> Void)?

    var body: some View {
        VStack {
            Text(title)
                .font(.headline)
            Text("Counter: \(counter)")
                .font(.largeTitle)
                .padding()
            Button("Increment") {
                counter += 1
                onIncrement?(counter)
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
        .background(Color.green.opacity(0.1))
        .cornerRadius(10)
    }
}

// Our UIKit ViewController
class UIKitViewController: UIViewController {

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemBackground
        setupSwiftUIComponent()
    }

    private func setupSwiftUIComponent() {
        // 1. Create an instance of your SwiftUI view
        let swiftUIView = MySwiftUIComponent(title: "Hello from SwiftUI!") { newCount in
            print("SwiftUI counter incremented to: \(newCount)")
            // You can update UIKit UI here based on SwiftUI events
        }

        // 2. Create a UIHostingController with your SwiftUI view
        let hostingController = UIHostingController(rootView: swiftUIView)

        // 3. Add the hosting controller as a child view controller
        addChild(hostingController)

        // 4. Add the hosting controller's view to the UIKit view hierarchy
        view.addSubview(hostingController.view)

        // 5. Tell the hosting controller that it's moved to a parent
        hostingController.didMove(toParent: self)

        // 6. Set up Auto Layout constraints for the SwiftUI view
        hostingController.view.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            hostingController.view.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            hostingController.view.centerYAnchor.constraint(equalTo: view.centerYAnchor),
            hostingController.view.leadingAnchor.constraint(greaterThanOrEqualTo: view.leadingAnchor, constant: 20),
            hostingController.view.trailingAnchor.constraint(lessThanOrEqualTo: view.trailingAnchor, constant: -20)
        ])
    }
}
```

In this example, we create a simple `MySwiftUIComponent` that displays a counter. We then embed this component into a `UIKitViewController` using `UIHostingController`. Notice how we pass data (`title`) to the SwiftUI view via its initializer and receive events (`onIncrement`) via a closure. This is a robust way to communicate between the two frameworks when SwiftUI is nested inside UIKit.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Embedding SwiftUI in UIKit using UIHostingController">
  <title>Embedding SwiftUI in UIKit using UIHostingController</title>
  <!-- UIKit ViewController -->
  <rect x="50" y="30" width="200" height="160" rx="10" ry="10" fill="#1565c0" opacity="0.1" stroke="#1565c0" stroke-width="2"/>
  <text x="150" y="55" font-family="Arial" font-size="16" fill="#1565c0" text-anchor="middle">UIKitViewController</text>

  <!-- UIHostingController -->
  <rect x="70" y="70" width="160" height="100" rx="8" ry="8" fill="#2A8367" opacity="0.1" stroke="#2A8367" stroke-width="2"/>
  <text x="150" y="95" font-family="Arial" font-size="14" fill="#2A8367" text-anchor="middle">UIHostingController</text>

  <!-- SwiftUI View -->
  <rect x="90" y="110" width="120" height="40" rx="6" ry="6" fill="#F04B3E" opacity="0.1" stroke="#F04B3E" stroke-width="2"/>
  <text x="150" y="135" font-family="Arial" font-size="12" fill="#F04B3E" text-anchor="middle">SwiftUI View</text>

  <!-- Arrows and Labels -->
  <path d="M250 110 H300 V110 H250" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowhead)"/>
  <path d="M300 110 L350 110" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="300" y="100" font-family="Arial" font-size="12" fill="#1565c0" text-anchor="middle">Embed</text>

  <rect x="350" y="70" width="200" height="100" rx="10" ry="10" fill="#F04B3E" opacity="0.1" stroke="#F04B3E" stroke-width="2"/>
  <text x="450" y="95" font-family="Arial" font-size="16" fill="#F04B3E" text-anchor="middle">SwiftUI View Hierarchy</text>
  <rect x="370" y="110" width="160" height="40" rx="8" ry="8" fill="#2A8367" opacity="0.1" stroke="#2A8367" stroke-width="2"/>
  <text x="450" y="135" font-family="Arial" font-size="14" fill="#2A8367" text-anchor="middle">SwiftUI Component</text>

  <path d="M250 110 C280 80, 320 80, 350 110" fill="none" stroke="#2A8367" stroke-width="2"/>
  <path d="M250 110 C280 140, 320 140, 350 110" fill="none" stroke="#F04B3E" stroke-width="2"/>

  <!-- More detailed flow for UIHostingController -->
  <rect x="300" y="30" width="250" height="160" rx="10" ry="10" fill="#2A8367" opacity="0.1" stroke="#2A8367" stroke-width="2"/>
  <text x="425" y="55" font-family="Arial" font-size="16" fill="#2A8367" text-anchor="middle">UIHostingController</text>

  <rect x="320" y="70" width="210" height="100" rx="8" ry="8" fill="#F04B3E" opacity="0.1" stroke="#F04B3E" stroke-width="2"/>
  <text x="425" y="95" font-family="Arial" font-size="14" fill="#F04B3E" text-anchor="middle">Root SwiftUI View</text>
  <text x="425" y="120" font-family="Arial" font-size="12" fill="#F04B3E" text-anchor="middle">(@State, @Binding, etc.)</text>
  <text x="425" y="145" font-family="Arial" font-size="12" fill="#F04B3E" text-anchor="middle">Actions (Closures/Delegates)</text>

  <path d="M250 110 H290" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="270" y="100" font-family="Arial" font-size="12" fill="#1565c0" text-anchor="middle">`view`</text>

  <path d="M300 170 V190 H200 V170" fill="none" stroke="#F04B3E" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="250" y="185" font-family="Arial" font-size="12" fill="#F04B3E" text-anchor="middle">Events Back to UIKit</text>

  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#1565c0" />
    </marker>
  </defs>
</svg>
</div>

## Embedding UIKit in SwiftUI

Embedding UIKit views and view controllers within a SwiftUI hierarchy is slightly more involved but equally powerful. SwiftUI provides two specific protocols for this: `UIViewRepresentable` for `UIView` subclasses and `UIViewControllerRepresentable` for `UIViewController` subclasses.

### `UIViewRepresentable`

When you need to integrate a custom `UIView` or a `UIView`-based control into SwiftUI, `UIViewRepresentable` is your go-to. You create a struct that conforms to this protocol, and it requires two methods:

1.  `makeUIView(context:)`: This method is responsible for creating and configuring your UIKit view. It's called once when the view is first created.
2.  `updateUIView(_:context:)`: This method is called whenever SwiftUI detects changes in the data you're passing to your `Representable` struct. You use it to update the UIKit view's properties.

Let's embed a `UILabel` with custom styling into a SwiftUI view:

```swift
import SwiftUI
import UIKit

struct CustomUILabel: UIViewRepresentable {
    var text: String
    var textColor: UIColor
    var font: UIFont

    func makeUIView(context: Context) -> UILabel {
        let label = UILabel()
        label.textAlignment = .center
        label.numberOfLines = 0
        return label
    }

    func updateUIView(_ uiView: UILabel, context: Context) {
        uiView.text = text
        uiView.textColor = textColor
        uiView.font = font
    }
}

struct ContentView: View {
    @State private var message = "Hello from UIKit!"
    @State private var fontSize: CGFloat = 20

    var body: some View {
        VStack {
            CustomUILabel(text: message, textColor: .red, font: .systemFont(ofSize: fontSize, weight: .bold))
                .frame(height: 100) // Give the UIKit view a frame in SwiftUI

            Slider(value: $fontSize, in: 10...40) {
                Text("Font Size")
            }
            .padding()

            Button("Change Message") {
                message = "Updated message at \(Date().formatted(date: .omitted, time: .shortened))"
            }
            .buttonStyle(.bordered)
        }
        .navigationTitle("UIKit in SwiftUI")
    }
}
```

In this example, `CustomUILabel` wraps a `UILabel`. The `updateUIView` method ensures that any changes to `text`, `textColor`, or `font` in the SwiftUI parent (`ContentView`) are reflected in the underlying UIKit `UILabel`.

### `UIViewControllerRepresentable`

Similar to `UIViewRepresentable`, `UIViewControllerRepresentable` allows you to embed entire `UIViewController` hierarchies within SwiftUI. This is particularly useful for complex UIKit controllers like `UIImagePickerController`, `UINavigationController`, or custom view controllers that manage their own complex layouts and lifecycles.

It also requires `makeUIViewController(context:)` and `updateUIViewController(_:context:)`.

```swift
import SwiftUI
import UIKit

// A simple UIKit view controller to embed
class MyCustomUIKitVC: UIViewController {
    var titleText: String = "Default Title" {
        didSet {
            label.text = titleText
        }
    }
    private let label = UILabel()

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemTeal
        label.textAlignment = .center
        label.font = .preferredFont(forTextStyle: .title1)
        label.text = titleText
        label.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(label)

        NSLayoutConstraint.activate([
            label.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            label.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }
}

// SwiftUI wrapper for MyCustomUIKitVC
struct MyRepresentedViewController: UIViewControllerRepresentable {
    @Binding var dynamicTitle: String

    func makeUIViewController(context: Context) -> MyCustomUIKitVC {
        let vc = MyCustomUIKitVC()
        vc.titleText = dynamicTitle
        return vc
    }

    func updateUIViewController(_ uiViewController: MyCustomUIKitVC, context: Context) {
        uiViewController.titleText = dynamicTitle
    }
}

struct RepresentedVCView: View {
    @State private var currentTitle = "Hello from a UIKit VC!"

    var body: some View {
        VStack {
            MyRepresentedViewController(dynamicTitle: $currentTitle)
                .frame(height: 200) // SwiftUI frame for the UIKit VC's view

            TextField("Enter new title", text: $currentTitle)
                .textFieldStyle(.roundedBorder)
                .padding()
        }
        .navigationTitle("Represented UIViewController")
    }
}
```
Here, `MyRepresentedViewController` wraps `MyCustomUIKitVC`. We use a `@Binding` to pass `currentTitle` from SwiftUI to the `UIViewController`, ensuring that changes in the `TextField` are reflected in the embedded UIKit view controller.

### Handling Events and Callbacks with `Coordinator`

When UIKit components need to communicate events or data back to their SwiftUI host, the `Coordinator` pattern within `Representable` types becomes invaluable. A `Coordinator` is a custom class that you define inside your `Representable` struct. It acts as a delegate or target for UIKit events and translates them into SwiftUI-friendly actions (e.g., updating `@Binding` properties, calling closures).

```swift
import SwiftUI
import UIKit

// A UIKit view that has an action
class MyInteractiveUIView: UIView {
    var onButtonTap: (() -> Void)?

    private lazy var button: UIButton = {
        let btn = UIButton(type: .system)
        btn.setTitle("Tap Me (UIKit)", for: .normal)
        btn.addTarget(self, action: #selector(buttonTapped), for: .touchUpInside)
        return btn
    }()

    override init(frame: CGRect) {
        super.init(frame: frame)
        setupView()
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    private func setupView() {
        backgroundColor = .systemYellow.withAlphaComponent(0.2)
        addSubview(button)
        button.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            button.centerXAnchor.constraint(equalTo: centerXAnchor),
            button.centerYAnchor.constraint(equalTo: centerYAnchor)
        ])
    }

    @objc private func buttonTapped() {
        onButtonTap?()
    }
}

// SwiftUI wrapper with Coordinator
struct InteractiveUIKitView: UIViewRepresentable {
    @Binding var tapCount: Int

    func makeUIView(context: Context) -> MyInteractiveUIView {
        let uiView = MyInteractiveUIView()
        uiView.onButtonTap = context.coordinator.buttonTapped // Assign SwiftUI callback to UIKit
        return uiView
    }

    func updateUIView(_ uiView: MyInteractiveUIView, context: Context) {
        // No updates needed from SwiftUI to UIKit in this specific example,
        // but this is where you'd update properties of uiView if needed.
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(parent: self)
    }

    class Coordinator: NSObject {
        var parent: InteractiveUIKitView

        init(parent: InteractiveUIKitView) {
            self.parent = parent
        }

        @objc func buttonTapped() {
            parent.tapCount += 1 // Update SwiftUI state via binding
        }
    }
}

struct InteractiveViewContainer: View {
    @State private var taps = 0

    var body: some View {
        VStack {
            InteractiveUIKitView(tapCount: $taps)
                .frame(height: 150)
                .padding()

            Text("Taps from UIKit: \(taps)")
                .font(.title2)
        }
        .navigationTitle("UIKit Events in SwiftUI")
    }
}
```

In `InteractiveUIKitView`, the `Coordinator` class acts as the `target` for the `MyInteractiveUIView`'s button tap. When the UIKit button is tapped, `Coordinator.buttonTapped()` is called, which then updates the SwiftUI `@Binding` property `tapCount`. This is the canonical way to send events from UIKit back to SwiftUI.

```
┌───────────────────────────┐     ┌────────────────────────────┐
│   SwiftUI Representable   │     │      Coordinator           │
│ (e.g., InteractiveUIKitView)│     │ (e.g., InteractiveUIKitView.Coordinator) │
├───────────────────────────┤     ├────────────────────────────┤
│ - @Binding tapCount       │◄────┤ - updates parent.tapCount  │
│ - makeUIView()            │     │ - receives UIKit events    │
│ - updateUIView()          │     └────────────────────────────┘
│ - makeCoordinator()       │
└───────────────────────────┘
          │ (assigns)
          │ onButtonTap = context.coordinator.buttonTapped
          ▼
┌───────────────────────────┐
│     UIKit View/VC         │
│ (e.g., MyInteractiveUIView) │
├───────────────────────────┤
│ - var onButtonTap: (() -> Void)? │
│ - buttonTapped() calls onButtonTap? │
└───────────────────────────┘
```

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 700 250" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Data Flow and Event Handling in Representable Views">
  <title>Data Flow and Event Handling in Representable Views</title>

  <!-- SwiftUI View -->
  <rect x="50" y="30" width="180" height="100" rx="10" ry="10" fill="#F04B3E" opacity="0.1" stroke="#F04B3E" stroke-width="2"/>
  <text x="140" y="55" font-family="Arial" font-size="16" fill="#F04B3E" text-anchor="middle">SwiftUI Parent View</text>
  <text x="140" y="80" font-family="Arial" font-size="12" fill="#F04B3E" text-anchor="middle">(@State, @Binding)</text>
  <text x="140" y="100" font-family="Arial" font-size="12" fill="#F04B3E" text-anchor="middle">Data Source</text>

  <!-- Representable Struct -->
  <rect x="260" y="30" width="180" height="180" rx="10" ry="10" fill="#2A8367" opacity="0.1" stroke="#2A8367" stroke-width="2"/>
  <text x="350" y="55" font-family="Arial" font-size="16" fill="#2A8367" text-anchor="middle">Representable Struct</text>
  <text x="350" y="80" font-family="Arial" font-size="12" fill="#2A8367" text-anchor="middle">(UIViewRepresentable / UIViewControllerRepresentable)</text>
  <text x="350" y="105" font-family="Arial" font-size="12" fill="#2A8367" text-anchor="middle">makeUIView/VC(context:)</text>
  <text x="350" y="125" font-family="Arial" font-size="12" fill="#2A8367" text-anchor="middle">updateUIView/VC(_:context:)</text>
  <text x="350" y="145" font-family="Arial" font-size="12" fill="#2A8367" text-anchor="middle">makeCoordinator()</text>

  <!-- Coordinator Class -->
  <rect x="470" y="30" width="180" height="100" rx="10" ry="10" fill="#1565c0" opacity="0.1" stroke="#1565c0" stroke-width="2"/>
  <text x="560" y="55" font-family="Arial" font-size="16" fill="#1565c0" text-anchor="middle">Coordinator</text>
  <text x="560" y="80" font-family="Arial" font-size="12" fill="#1565c0" text-anchor="middle">(Delegate, Target)</text>
  <text x="560" y="100" font-family="Arial" font-size="12" fill="#1565c0" text-anchor="middle">Event Handlers</text>

  <!-- UIKit View/VC -->
  <rect x="260" y="190" width="180" height="40" rx="10" ry="10" fill="#1565c0" opacity="0.1" stroke="#1565c0" stroke-width="2"/>
  <text x="350" y="215" font-family="Arial" font-size="16" fill="#1565c0" text-anchor="middle">UIKit View / ViewController</text>

  <!-- Arrows -->
  <!-- Data flow from SwiftUI Parent to Representable -->
  <path d="M230 75 H255" stroke="#F04B3E" stroke-width="2" marker-end="url(#arrowheadRed)"/>
  <text x="240" y="65" font-family="Arial" font-size="10" fill="#F04B3E" text-anchor="middle">Data</text>

  <!-- Data flow from Representable to UIKit View/VC (initial creation & updates) -->
  <path d="M350 155 V185" stroke="#2A8367" stroke-width="2" marker-end="url(#arrowheadGreen)"/>
  <text x="360" y="170" font-family="Arial" font-size="10" fill="#2A8367" text-anchor="start">Configure UI</text>

  <!-- Event flow from UIKit View/VC to Coordinator -->
  <path d="M440 200 H465 L465 110 L455 110" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowheadBlue)"/>
  <text x="450" y="185" font-family="Arial" font-size="10" fill="#1565c0" text-anchor="middle">Events</text>

  <!-- Event flow from Coordinator to Representable (updates @Binding) -->
  <path d="M470 75 H445" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowheadBlue)"/>
  <text x="455" y="65" font-family="Arial" font-size="10" fill="#1565c0" text-anchor="middle">Update</text>

  <!-- Data flow from Representable (via @Binding) to SwiftUI Parent -->
  <path d="M260 75 H235" stroke="#F04B3E" stroke-width="2" marker-end="url(#arrowheadRed)"/>
  <text x="245" y="90" font-family="Arial" font-size="10" fill="#F04B3E" text-anchor="middle">@Binding Update</text>

  <defs>
    <marker id="arrowheadRed" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#F04B3E" />
    </marker>
    <marker id="arrowheadGreen" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#2A8367" />
    </marker>
    <marker id="arrowheadBlue" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#1565c0" />
    </marker>
  </defs>
</svg>
</div>

## Best Practices and Considerations

*   **Choose the right `Representable`**: Use `UIViewRepresentable` for individual views and `UIViewControllerRepresentable` for entire view controllers or those that manage their own navigation.
*   **Minimalism**: Only wrap the necessary UIKit components. Avoid wrapping entire complex UIKit screens in `Representable` when `UIHostingController` might be a better fit for a new SwiftUI screen in an old app.
*   **Data Flow is Key**: Clearly define how data flows into your `Representable` (via regular properties, `@Binding`) and how events flow out (via `Coordinator`, closures, or delegates).
*   **Performance**: While interoperability is generally efficient, deeply nested `Representable` views or frequently updating large UIKit views can impact performance. Profile your app if you suspect issues.
*   **Lifecycle Differences**: Remember that UIKit and SwiftUI have different lifecycles. `makeUIView/VC` is called once, `updateUIView/VC` can be called many times. `Coordinator` instances are created and managed by SwiftUI.
*   **Environment**: `UIHostingController` allows you to pass SwiftUI `Environment` values to its root view, which is convenient. When embedding UIKit in SwiftUI, UIKit views don't automatically get SwiftUI environment values, but you can pass them down explicitly via properties.
*   **Gradual Migration**: These interoperability patterns are excellent for a gradual migration strategy, allowing you to rewrite parts of your app in SwiftUI without a complete overhaul.

## Summary

UIKit and SwiftUI interoperability is a cornerstone of modern iOS development, enabling developers to build powerful hybrid applications. `UIHostingController` allows you to bring the elegance of SwiftUI into existing UIKit codebases, while `UIViewRepresentable` and `UIViewControllerRepresentable` empower you to leverage the vast ecosystem of UIKit components within your SwiftUI views. By mastering these patterns and understanding how to manage data flow and events, you can seamlessly blend the best of both worlds, ensuring a smooth transition and a robust user experience.

Happy Swifting!
