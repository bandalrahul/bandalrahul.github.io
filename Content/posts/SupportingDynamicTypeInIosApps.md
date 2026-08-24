---
title: Supporting Dynamic Type in iOS Apps
date: 2026-08-24 09:38
description: Learn how to implement Dynamic Type in your iOS apps using UIKit and SwiftUI to provide an accessible and responsive user experience for all users.
tags: Accessibility, iOS, Development
---

# Supporting Dynamic Type in iOS Apps

In the world of iOS development, creating beautiful and functional apps is a given. But truly great apps go beyond aesthetics and core features – they are inclusive and accessible to everyone. One of the most fundamental aspects of accessibility on iOS is **Dynamic Type**. It empowers users to adjust the size of text displayed on their device, ensuring that your app remains readable and usable regardless of their visual preferences or needs.

Imagine a user with impaired vision struggling to read tiny text in your app, or a user who simply prefers larger fonts for comfort. Without Dynamic Type support, your app might become unusable for them, leading to frustration and potentially uninstalls. By embracing Dynamic Type, you're not just complying with accessibility guidelines; you're significantly enhancing the user experience for a broader audience.

This article will guide you through the process of implementing Dynamic Type in both UIKit and SwiftUI, ensuring your app's text scales gracefully and maintains its layout integrity across all content size categories.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Illustration of Dynamic Type scaling text on an iPhone">
  <title>Dynamic Type in Action</title>

  <!-- Phone 1 (Normal Text) -->
  <rect x="50" y="20" width="200" height="180" rx="15" ry="15" fill="#f0f0f0" stroke="#333" stroke-width="2"/>
  <rect x="60" y="30" width="180" height="15" rx="5" ry="5" fill="#ccc"/>
  <text x="150" y="42" font-family="SF Pro Text" font-size="10" text-anchor="middle" fill="#333">Normal Text Size</text>
  <rect x="70" y="60" width="160" height="20" rx="5" ry="5" fill="#fff" stroke="#999" stroke-width="1"/>
  <text x="150" y="75" font-family="SF Pro Text" font-size="14" text-anchor="middle" fill="#333">App Title</text>
  <rect x="70" y="90" width="160" height="60" rx="5" ry="5" fill="#fff" stroke="#999" stroke-width="1"/>
  <text x="150" y="105" font-family="SF Pro Text" font-size="12" text-anchor="middle" fill="#333">This is some body</text>
  <text x="150" y="120" font-family="SF Pro Text" font-size="12" text-anchor="middle" fill="#333">text at a default</text>
  <text x="150" y="135" font-family="SF Pro Text" font-size="12" text-anchor="middle" fill="#333">size. It fits well.</text>
  <rect x="70" y="160" width="160" height="20" rx="5" ry="5" fill="#2A8367"/>
  <text x="150" y="175" font-family="SF Pro Text" font-size="12" text-anchor="middle" fill="#fff">Action Button</text>

  <!-- Arrow -->
  <line x1="260" y1="110" x2="340" y2="110" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="300" y="100" font-family="SF Pro Text" font-size="14" text-anchor="middle" fill="#1565c0">Dynamic Type</text>
  <text x="300" y="125" font-family="SF Pro Text" font-size="14" text-anchor="middle" fill="#1565c0">Scaling</text>

  <!-- Phone 2 (Large Text) -->
  <rect x="350" y="20" width="200" height="180" rx="15" ry="15" fill="#f0f0f0" stroke="#333" stroke-width="2"/>
  <rect x="360" y="30" width="180" height="15" rx="5" ry="5" fill="#ccc"/>
  <text x="450" y="42" font-family="SF Pro Text" font-size="10" text-anchor="middle" fill="#333">Larger Text Size</text>
  <rect x="370" y="60" width="160" height="30" rx="5" ry="5" fill="#fff" stroke="#999" stroke-width="1"/>
  <text x="450" y="80" font-family="SF Pro Text" font-size="20" text-anchor="middle" fill="#333">App Title</text>
  <rect x="370" y="95" width="160" height="70" rx="5" ry="5" fill="#fff" stroke="#999" stroke-width="1"/>
  <text x="450" y="115" font-family="SF Pro Text" font-size="16" text-anchor="middle" fill="#333">This is some body</text>
  <text x="450" y="135" font-family="SF Pro Text" font-size="16" text-anchor="middle" fill="#333">text at a larger size.</text>
  <text x="450" y="155" font-family="SF Pro Text" font-size="16" text-anchor="middle" fill="#333">It still fits well.</text>
  <rect x="370" y="170" width="160" height="30" rx="5" ry="5" fill="#2A8367"/>
  <text x="450" y="190" font-family="SF Pro Text" font-size="16" text-anchor="middle" fill="#fff">Action Button</text>

  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#1565c0" />
    </marker>
  </defs>
</svg>
</div>

## Understanding Dynamic Type and Content Size Categories

Dynamic Type is an accessibility feature that allows users to choose their preferred text size from a range of predefined options. These options are represented by `UIContentSizeCategory` in UIKit (and implicitly handled in SwiftUI). Users can adjust this setting in **Settings > Accessibility > Display & Text Size > Larger Text**.

The system provides several content size categories:
*   **Default sizes**: `extraSmall`, `small`, `medium`, `large` (default), `extraLarge`, `extraExtraLarge`, `extraExtraExtraLarge`.
*   **Accessibility sizes**: `accessibilityMedium`, `accessibilityLarge`, `accessibilityExtraLarge`, `accessibilityExtraExtraLarge`, `accessibilityExtraExtraExtraLarge`.

When a user changes their preferred text size, the system sends out a notification, prompting apps to update their UI. The key to supporting Dynamic Type is to use **semantic text styles** rather than hardcoding point sizes. Semantic styles like `body`, `title1`, `headline`, `caption1`, etc., are mapped by the system to appropriate point sizes for each content size category. This ensures consistency and adaptability.

## Implementing Dynamic Type in UIKit

UIKit offers robust support for Dynamic Type, but it requires a few explicit steps to ensure your UI elements adapt correctly.

### 1. Using Preferred Fonts for System Text Styles

The most straightforward way to support Dynamic Type for standard UI elements like `UILabel`, `UITextField`, and `UITextView` is to use `UIFont.preferredFont(forTextStyle:)`.

```swift
import UIKit

class DynamicTypeLabelViewController: UIViewController {

    private let titleLabel: UILabel = {
        let label = UILabel()
        label.translatesAutoresizingMaskIntoConstraints = false
        label.text = "Welcome to My App"
        // Use a semantic text style for the title
        label.font = UIFont.preferredFont(forTextStyle: .largeTitle)
        // This is crucial: enables automatic font scaling
        label.adjustsFontForContentSizeCategory = true
        label.numberOfLines = 0 // Allow label to wrap text
        label.textAlignment = .center
        return label
    }()

    private let bodyLabel: UILabel = {
        let label = UILabel()
        label.translatesAutoresizingMaskIntoConstraints = false
        label.text = "This is a longer piece of text that demonstrates how Dynamic Type adjusts the font size and layout to accommodate user preferences. It ensures readability for all users."
        // Use a semantic text style for the body
        label.font = UIFont.preferredFont(forTextStyle: .body)
        label.adjustsFontForContentSizeCategory = true
        label.numberOfLines = 0 // Allow label to wrap text
        return label
    }()

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemBackground
        setupLayout()
    }

    private func setupLayout() {
        view.addSubview(titleLabel)
        view.addSubview(bodyLabel)

        NSLayoutConstraint.activate([
            titleLabel.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 20),
            titleLabel.leadingAnchor.constraint(equalTo: view.readableContentGuide.leadingAnchor, constant: 20),
            titleLabel.trailingAnchor.constraint(equalTo: view.readableContentGuide.trailingAnchor, constant: -20),

            bodyLabel.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 30),
            bodyLabel.leadingAnchor.constraint(equalTo: view.readableContentGuide.leadingAnchor, constant: 20),
            bodyLabel.trailingAnchor.constraint(equalTo: view.readableContentGuide.trailingAnchor, constant: -20),
        ])
    }

    // This method is called when the trait collection changes (including content size category)
    override func traitCollectionDidChange(_ previousTraitCollection: UITraitCollection?) {
        super.traitCollectionDidChange(previousTraitCollection)
        if traitCollection.preferredContentSizeCategory != previousTraitCollection?.preferredContentSizeCategory {
            // Re-layout or update views if necessary.
            // For labels with adjustsFontForContentSizeCategory = true, this is often handled automatically.
            // However, if you have custom views or complex layouts, you might need to trigger an update.
            view.setNeedsLayout()
            view.layoutIfNeeded()
        }
    }
}
```
**Key points**:
*   `UIFont.preferredFont(forTextStyle: .body)`: Creates a font instance that automatically scales with the user's preferred content size category.
*   `label.adjustsFontForContentSizeCategory = true`: This property is crucial. When set to `true`, the label automatically updates its font when the `UIContentSizeCategory` changes, without requiring you to manually re-assign the font.
*   `label.numberOfLines = 0`: Allows the label to use as many lines as needed to display its content, preventing truncation when text size increases.
*   `traitCollectionDidChange(_:)`: This method is called when the environment's traits (like content size category, display scale, user interface style) change. While `adjustsFontForContentSizeCategory` handles font updates, you might need to use this to trigger layout updates for custom views or to re-evaluate complex constraints.

### 2. Scaling Custom Fonts with `UIFontMetrics`

If your app uses custom fonts, you can still make them adapt to Dynamic Type using `UIFontMetrics`. This class provides methods to scale your custom font based on a specific `UIContentSizeCategory`.

```swift
import UIKit

extension UIFont {
    static func scaledCustomFont(named name: String, baseSize: CGFloat, forTextStyle textStyle: UIFont.TextStyle) -> UIFont {
        guard let customFont = UIFont(name: name, size: baseSize) else {
            fatalError("Failed to load the \(name) font.")
        }
        // Scale the custom font based on the provided text style
        return UIFontMetrics(forTextStyle: textStyle).scaledFont(for: customFont)
    }
}

class CustomFontViewController: UIViewController {

    private let customTitleLabel: UILabel = {
        let label = UILabel()
        label.translatesAutoresizingMaskIntoConstraints = false
        label.text = "Custom Font Title"
        // Use the scaled custom font
        label.font = .scaledCustomFont(named: "Georgia", baseSize: 24, forTextStyle: .title1)
        label.adjustsFontForContentSizeCategory = true
        label.numberOfLines = 0
        label.textAlignment = .center
        return label
    }()

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemBackground
        setupLayout()
    }

    private func setupLayout() {
        view.addSubview(customTitleLabel)
        NSLayoutConstraint.activate([
            customTitleLabel.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            customTitleLabel.centerYAnchor.constraint(equalTo: view.centerYAnchor),
            customTitleLabel.leadingAnchor.constraint(equalTo: view.readableContentGuide.leadingAnchor, constant: 20),
            customTitleLabel.trailingAnchor.constraint(equalTo: view.readableContentGuide.trailingAnchor, constant: -20),
        ])
    }
}
```
In this example, we define an extension for `UIFont` to create a scaled custom font. You provide a base size for your custom font, and `UIFontMetrics` handles the scaling relative to a chosen system text style. This ensures your custom font scales proportionally to how system fonts would, maintaining a consistent user experience.

```
┌───────────────────┐     ┌───────────────────────┐
│ User changes      │     │ App receives          │
│ Content Size      │───┐ │ UIContentSizeCategory │
│ Category in       │   │ │ didChangeNotification │
│ Settings          │   │ └───────────────────────┘
└───────────────────┘   │             │
                        │             ▼
                        │   ┌───────────────────────┐
                        └──►│ `traitCollectionDidChange`│
                            │ (for VCs/Views)       │
                            └───────────────────────┘
                                      │
                                      ▼
                      ┌─────────────────────────────────┐
                      │ UI elements with                │
                      │ `adjustsFontForContentSizeCategory = true` │
                      │ automatically update their fonts│
                      └─────────────────────────────────┘
```

## Implementing Dynamic Type in SwiftUI

SwiftUI makes supporting Dynamic Type remarkably straightforward. By default, `Text` views automatically adapt to the user's preferred content size category when you use the system-provided `Font` styles.

### 1. Using System `Font` Styles

When you apply a system font style to a `Text` view, SwiftUI automatically handles the scaling.

```swift
import SwiftUI

struct DynamicTypeView: View {
    var body: some View {
        VStack(spacing: 20) {
            Text("Welcome to My SwiftUI App")
                .font(.largeTitle) // Automatically scales
                .multilineTextAlignment(.center)

            Text("This is a body of text that demonstrates how SwiftUI's Text views inherently support Dynamic Type, adapting their size based on user preferences.")
                .font(.body) // Automatically scales
                .multilineTextAlignment(.leading)
        }
        .padding()
    }
}
```
That's it! SwiftUI's `Text` view, when combined with semantic `Font` styles like `.largeTitle`, `.body`, `.headline`, `.caption`, etc., will automatically adjust its size. You don't need to observe notifications or set specific properties like `adjustsFontForContentSizeCategory`.

### 2. Scaling Custom Fonts in SwiftUI

Similar to UIKit, you can also use custom fonts with Dynamic Type support in SwiftUI using the `.custom()` modifier with the `relativeTo` parameter.

```swift
import SwiftUI

struct CustomDynamicTypeView: View {
    var body: some View {
        VStack(spacing: 20) {
            Text("Custom Font Title")
                // Use a custom font, scaling relative to .title1
                .font(.custom("Georgia", size: 24, relativeTo: .title1))
                .multilineTextAlignment(.center)

            Text("This text uses a custom font and still benefits from Dynamic Type scaling, thanks to the relativeTo parameter.")
                // Use a custom font, scaling relative to .body
                .font(.custom("Georgia", size: 17, relativeTo: .body))
                .multilineTextAlignment(.leading)
        }
        .padding()
    }
}
```
The `relativeTo` parameter is key here. It tells SwiftUI to scale your `size` for the custom font in the same way the system would scale the specified `textStyle`. For example, `.custom("Georgia", size: 24, relativeTo: .title1)` means "use Georgia at 24pt when the system's `.title1` is 24pt, and scale it proportionally for other content size categories."

## Advanced Considerations and Best Practices

### Layout Adjustments

Supporting Dynamic Type isn't just about text scaling; it's also about ensuring your layout remains functional and aesthetically pleasing.

*   **UIKit**:
    *   **Auto Layout**: Design your constraints to be flexible. Avoid fixed heights where text can expand. Use `UILayoutPriority` to allow content to push against constraints.
    *   **`UIStackView`**: A powerful tool for adaptive layouts. Use `UIStackView` to arrange content vertically or horizontally, allowing elements to grow or shrink as needed. `distribution` and `alignment` properties are crucial.
    *   **`readableContentGuide`**: Use this layout guide to ensure your text doesn't span the entire width of large screens, improving readability.

*   **SwiftUI**:
    *   **`VStack` / `HStack`**: SwiftUI's layout containers are inherently flexible. They will naturally adjust to accommodate larger text.
    *   **Prioritize Vertical Growth**: When text grows, it usually needs more vertical space. Design your layouts to primarily expand vertically. Consider how your layout will look if a label suddenly takes up 3-4 lines instead of 1.
    *   **`minimumScaleFactor` (UIKit) / `minimumScaleFactor` (SwiftUI `Text`)**: While `numberOfLines = 0` (UIKit) or `lineLimit(nil)` (SwiftUI) is preferred, if you absolutely must constrain text to a single line, `minimumScaleFactor` can prevent truncation by shrinking the text. However, use this sparingly as it can defeat the purpose of Dynamic Type.

### Testing Dynamic Type

Testing is crucial to ensure your app behaves correctly across all content size categories.

*   **Xcode Environment Overrides**: In Xcode, when running your app on a simulator or device, you can use the Debug Bar at the bottom of the canvas/debug area. Click the "Environment Overrides" button (looks like two overlapping rectangles) and select "Text Size" to quickly change the content size category without leaving Xcode.
*   **Accessibility Inspector**: This tool (found in Xcode > Open Developer Tool > Accessibility Inspector) allows you to test various accessibility features, including Dynamic Type, and helps identify elements that aren't scaling correctly.
*   **Real Devices**: Always test on actual devices, as simulator behavior can sometimes differ slightly.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 280" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Comparison of fixed font size versus dynamic type with changing text size">
  <title>Fixed vs. Dynamic Type Layout</title>

  <!-- Group 1: Fixed Size (Normal) -->
  <text x="150" y="30" font-family="SF Pro Text" font-size="16" text-anchor="middle" fill="#333">Fixed Font Size (Normal)</text>
  <rect x="50" y="50" width="200" height="100" rx="8" ry="8" fill="#f0f0f0" stroke="#999" stroke-width="1"/>
  <text x="150" y="75" font-family="SF Pro Text" font-size="16" text-anchor="middle" fill="#333">Title</text>
  <text x="150" y="105" font-family="SF Pro Text" font-size="12" text-anchor="middle" fill="#333">Body text fits here.</text>
  <rect x="70" y="125" width="160" height="20" rx="5" ry="5" fill="#2A8367"/>
  <text x="150" y="140" font-family="SF Pro Text" font-size="12" text-anchor="middle" fill="#fff">Button</text>

  <!-- Group 2: Fixed Size (Large) -->
  <text x="150" y="180" font-family="SF Pro Text" font-size="16" text-anchor="middle" fill="#F04B3E">Fixed Font Size (Large)</text>
  <rect x="50" y="200" width="200" height="70" rx="8" ry="8" fill="#f0f0f0" stroke="#F04B3E" stroke-width="2"/>
  <text x="150" y="220" font-family="SF Pro Text" font-size="16" text-anchor="middle" fill="#F04B3E">Title</text>
  <text x="150" y="240" font-family="SF Pro Text" font-size="12" text-anchor="middle" fill="#F04B3E">Body text fits here.</text>
  <text x="150" y="255" font-family="SF Pro Text" font-size="10" text-anchor="middle" fill="#F04B3E">Truncated!</text>
  <rect x="70" y="255" width="160" height="20" rx="5" ry="5" fill="#F04B3E"/>
  <text x="150" y="270" font-family="SF Pro Text" font-size="12" text-anchor="middle" fill="#fff">Button</text>
  <text x="150" y="165" font-family="SF Pro Text" font-size="12" text-anchor="middle" fill="#F04B3E">Text size changed, but UI is constrained.</text>


  <!-- Separator Line -->
  <line x1="300" y1="20" x2="300" y2="260" stroke="#ccc" stroke-width="1" stroke-dasharray="5,5"/>
  <text x="300" y="150" font-family="SF Pro Text" font-size="14" text-anchor="middle" fill="#1565c0">VS</text>

  <!-- Group 3: Dynamic Type (Normal) -->
  <text x="450" y="30" font-family="SF Pro Text" font-size="16" text-anchor="middle" fill="#333">Dynamic Type (Normal)</text>
  <rect x="350" y="50" width="200" height="100" rx="8" ry="8" fill="#f0f0f0" stroke="#999" stroke-width="1"/>
  <text x="450" y="75" font-family="SF Pro Text" font-size="16" text-anchor="middle" fill="#333">Title</text>
  <text x="450" y="105" font-family="SF Pro Text" font-size="12" text-anchor="middle" fill="#333">Body text fits here.</text>
  <rect x="370" y="125" width="160" height="20" rx="5" ry="5" fill="#2A8367"/>
  <text x="450" y="140" font-family="SF Pro Text" font-size="12" text-anchor="middle" fill="#fff">Button</text>

  <!-- Group 4: Dynamic Type (Large) -->
  <text x="450" y="180" font-family="SF Pro Text" font-size="16" text-anchor="middle" fill="#1565c0">Dynamic Type (Large)</text>
  <rect x="350" y="200" width="200" height="70" rx="8" ry="8" fill="#f0f0f0" stroke="#1565c0" stroke-width="2"/>
  <text x="450" y="220" font-family="SF Pro Text" font-size="20" text-anchor="middle" fill="#1565c0">Title</text>
  <text x="450" y="240" font-family="SF Pro Text" font-size="16" text-anchor="middle" fill="#1565c0">Body text fits here</text>
  <text x="450" y="255" font-family="SF Pro Text" font-size="16" text-anchor="middle" fill="#1565c0">and expands layout.</text>
  <rect x="370" y="255" width="160" height="20" rx="5" ry="5" fill="#1565c0"/>
  <text x="450" y="270" font-family="SF Pro Text" font-size="16" text-anchor="middle" fill="#fff">Button</text>
  <text x="450" y="165" font-family="SF Pro Text" font-size="12" text-anchor="middle" fill="#1565c0">UI adapts to larger text size.</text>

</svg>
</div>

### General Best Practices

*   **Always use semantic text styles**: Whether it's `UIFont.preferredFont(forTextStyle:)` or SwiftUI's `.font(.body)`, avoid hardcoding point sizes unless absolutely necessary (and then scale them with `UIFontMetrics` or `relativeTo`).
*   **Design for flexibility**: Assume text will be larger or smaller than your default. Use flexible layouts (Stack Views, `VStack`/`HStack`) that can grow and shrink.
*   **Prioritize content**: Ensure that even at extreme text sizes, the most important information is still visible and accessible.
*   **Check for truncation**: Regularly test your app with large content size categories to ensure text isn't being cut off.
*   **Don't forget images**: If images contain text, ensure they also scale or provide alternative ways to convey information.

## Summary

Supporting Dynamic Type in your iOS applications is a fundamental step towards creating inclusive and user-friendly experiences. By leveraging system-provided semantic text styles, `UIFontMetrics` for custom fonts in UIKit, and the inherent adaptability of SwiftUI's `Text` views with `relativeTo`, you can ensure your app's text scales beautifully. Remember to design flexible layouts and thoroughly test your app across all content size categories to guarantee a seamless experience for every user.

Happy Swifting!
