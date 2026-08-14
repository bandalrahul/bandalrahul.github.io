---
title: Introduction to App Clips for iOS Developers
date: 2026-08-14 09:52
description: Discover App Clips, Apple's feature for instant app experiences. Learn how to integrate, share code, and handle invocations for your iOS projects.
tags: iOS, Development, Apple
---

# Introduction to App Clips for iOS Developers

In the fast-paced world of mobile applications, friction is the enemy of engagement. Users want instant access to functionality, without the commitment of a full download. Apple recognized this need with the introduction of App Clips at WWDC 2020 – a brilliant feature designed to provide a lightweight, focused experience of your app precisely when and where it's needed most.

For iOS developers, App Clips open up exciting new avenues for discoverability and user acquisition. Imagine a user needing to pay for parking, rent a scooter, or order a coffee. Instead of searching the App Store, downloading, and setting up a full app, an App Clip allows them to complete that specific task in seconds, often without even unlocking their phone.

This article will guide you through the essentials of App Clips, from understanding their core purpose and architecture to implementing them in your existing iOS projects. We'll cover how App Clips work, how to set them up, and best practices for delivering a seamless, instant experience.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Various ways users can discover and launch an App Clip">
  <title>App Clip Discovery Methods</title>

  <!-- Styles -->
  <defs>
    <style>
      .box { fill: #f0f0f0; stroke: #ccc; stroke-width: 1; rx: 8; ry: 8; }
      .label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 14px; fill: #333; text-anchor: middle; }
      .arrow { stroke: #1565c0; stroke-width: 2; marker-end: url(#arrowhead); }
      .marker-color { fill: #1565c0; }
    </style>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="8" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" class="marker-color" />
    </marker>
  </defs>

  <!-- Entry Points -->
  <rect x="20" y="20" width="100" height="40" class="box" />
  <text x="70" y="45" class="label">NFC Tag</text>

  <rect x="140" y="20" width="100" height="40" class="box" />
  <text x="190" y="45" class="label">QR Code</text>

  <rect x="260" y="20" width="100" height="40" class="box" />
  <text x="310" y="45" class="label">Safari Banner</text>

  <rect x="380" y="20" width="100" height="40" class="box" />
  <text x="430" y="45" class="label">iMessage</text>

  <rect x="500" y="20" width="80" height="40" class="box" />
  <text x="540" y="45" class="label">Maps</text>

  <!-- App Clip Icon -->
  <rect x="250" y="100" width="100" height="100" class="box" style="fill: #2A8367; stroke: #2A8367;" />
  <text x="300" y="155" class="label" style="fill: white; font-weight: bold;">App Clip</text>
  <text x="300" y="175" class="label" style="fill: white;">(Instant Experience)</text>

  <!-- Arrows to App Clip -->
  <line x1="70" y1="60" x2="280" y2="100" class="arrow" />
  <line x1="190" y1="60" x2="280" y2="100" class="arrow" />
  <line x1="310" y1="60" x2="310" y2="100" class="arrow" />
  <line x1="430" y1="60" x2="320" y2="100" class="arrow" />
  <line x1="540" y1="60" x2="320" y2="100" class="arrow" />
</svg>
</div>

## The Problem App Clips Solve

Before App Clips, if a user encountered a situation where an app could be useful (e.g., renting a bike), they had two options:
1.  **Download the full app**: This involves finding it on the App Store, waiting for the download, installing, and then potentially going through an onboarding process. This can be a significant barrier for a one-off or quick task.
2.  **Abandon the task**: If the friction is too high, the user might simply choose not to use the service.

App Clips bridge this gap by offering a "just in time" experience. They are small parts of your app, designed for specific, immediate use cases. Think of them as miniature versions of your app that launch almost instantly, allowing users to complete a task and then decide if they want the full app.

## Core Characteristics of App Clips

App Clips are not just stripped-down versions of your app; they have unique characteristics and constraints:

*   **Small Size**: App Clips must be under 15 MB. This is crucial for instant downloads and launches.
*   **Ephemeral**: App Clips are not permanently installed on a user's device. The system may remove them after a period of inactivity or if storage is low. They don't appear on the home screen.
*   **Focused Task**: Each App Clip should be designed for a single, well-defined task. Don't try to cram all your app's functionality into an App Clip.
*   **Privacy-First**: App Clips have limited access to sensitive user data, protecting user privacy. For example, they cannot access `HealthKit`, `HomeKit`, or `Motion and Fitness` data. They also cannot use `Bluetooth` in the background or access `Contacts`.
*   **No Background Activity**: App Clips cannot perform background processing.
*   **Call to Action**: After completing a task, App Clips should offer a clear path to download the full app.

## How App Clips Work: Invocation and Associated Domains

The magic of App Clips lies in their invocation mechanism. Unlike full apps, which are launched by tapping an icon, App Clips are launched through specific "invocation experiences." These experiences are tied to a URL that your server hosts.

When a user interacts with one of the following, an App Clip can be presented:

*   **App Clip Codes**: Physical tags (NFC-enabled or QR codes) that Apple provides tools to generate.
*   **NFC Tags**: Tapping an iPhone on a physical NFC tag.
*   **QR Codes**: Scanning a QR code with the Camera app.
*   **Safari Smart App Banners**: A banner displayed at the top of a webpage in Safari.
*   **Links in Messages**: Tapping a link shared in the Messages app.
*   **Places in Maps**: Tapping a link associated with a business location in Apple Maps.

All these invocation methods ultimately resolve to a URL. Your app needs to tell iOS which URLs correspond to which App Clip experiences. This is done through **Associated Domains**.

### Associated Domains Configuration

To link your App Clip to a specific URL, you need to:

1.  **Add the Associated Domains capability** to both your main app target and your App Clip target in Xcode.
2.  **Add an `appclips:` entry** to your `Associated Domains` list for each domain that will host your App Clip invocation URLs. For example: `appclips:yourdomain.com`.
3.  **Host an `apple-app-site-association` file** on your web server at `yourdomain.com/.well-known/apple-app-site-association`. This JSON file tells iOS which App Clips (and full apps) are associated with which paths on your domain.

Example `apple-app-site-association` file:

```json
{
  "appclips": {
    "apps": [
      "ABCDEFGHIJ.com.yourcompany.YourApp.Clip"
    ]
  },
  "applinks": {
    "details": [
      {
        "appIDs": [ "ABCDEFGHIJ.com.yourcompany.YourApp" ],
        "components": [
          {
            "paths": [ "/checkout/*", "/order/*" ]
          }
        ]
      }
    ]
  }
}
```

Replace `ABCDEFGHIJ` with your Team ID and `com.yourcompany.YourApp.Clip` with your App Clip's bundle identifier. The `applinks` section is for Universal Links for your full app, which often share the same domain.

## Implementing an App Clip

Now, let's get practical. Adding an App Clip to your existing iOS project.

### 1. Add an App Clip Target

In Xcode, go to `File > New > Target...`. Search for "App Clip" and select it.
Provide a product name (e.g., "YourAppClip") and ensure "Embed in Application" is set to your main app. This creates a new target with its own `Info.plist` and a basic `ContentView` (if SwiftUI) or `ViewController` (if UIKit).

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Architecture diagram showing shared code between main app and App Clip target">
  <title>App Clip and Main App Shared Code Architecture</title>

  <!-- Styles -->
  <defs>
    <style>
      .box { fill: #f0f0f0; stroke: #ccc; stroke-width: 1; rx: 8; ry: 8; }
      .label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 14px; fill: #333; text-anchor: middle; }
      .arrow { stroke: #1565c0; stroke-width: 2; marker-end: url(#arrowhead); }
      .marker-color { fill: #1565c0; }
    </style>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="8" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" class="marker-color" />
    </marker>
  </defs>

  <!-- Main App Target -->
  <rect x="20" y="70" width="150" height="80" class="box" style="fill: #2A8367;" />
  <text x="95" y="105" class="label" style="fill: white; font-weight: bold;">Main App Target</text>
  <text x="95" y="125" class="label" style="fill: white;">(Full Functionality)</text>

  <!-- App Clip Target -->
  <rect x="430" y="70" width="150" height="80" class="box" style="fill: #F04B3E;" />
  <text x="505" y="105" class="label" style="fill: white; font-weight: bold;">App Clip Target</text>
  <text x="505" y="125" class="label" style="fill: white;">(Focused Task)</text>

  <!-- Shared Code -->
  <rect x="225" y="20" width="150" height="40" class="box" />
  <text x="300" y="45" class="label">Shared Code (Framework/Group)</text>

  <!-- Arrows -->
  <line x1="300" y1="60" x2="300" y2="90" style="stroke: #333; stroke-width: 1;" />
  <polyline points="300,90 200,90 200,105" class="arrow" style="stroke: #333;" />
  <polyline points="300,90 400,90 400,105" class="arrow" style="stroke: #333;" />

  <text x="200" y="80" class="label" style="text-anchor: end; font-size: 12px; fill: #1565c0;">Uses</text>
  <text x="400" y="80" class="label" style="text-anchor: start; font-size: 12px; fill: #1565c0;">Uses</text>

</svg>
</div>

### 2. Share Code Between Targets

To keep your App Clip size small and maintain consistency, you'll want to share as much code as possible between your main app and the App Clip.

For each file you want to share:
*   Select the file in the Project Navigator.
*   In the File Inspector (right sidebar), under "Target Membership", check the box for both your main app target and your App Clip target.

For larger, more complex shared logic, consider creating a **shared framework** that both your main app and App Clip link against. This is often a cleaner approach for substantial common functionality.

### 3. Handle Invocation URLs

When an App Clip is launched, it receives the invocation URL. You handle this URL in your App Clip's `SceneDelegate` (for UIKit) or `App` struct (for SwiftUI).

#### SwiftUI Example:

```swift
// YourAppClipApp.swift
import SwiftUI

@main
struct YourAppClipApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .onContinueUserActivity(NSUserActivityTypeBrowsingWeb) { userActivity in
                    // Handle the invocation URL
                    guard let incomingURL = userActivity.webpageURL else { return }
                    handleAppClipInvocation(url: incomingURL)
                }
        }
    }

    func handleAppClipInvocation(url: URL) {
        print("App Clip invoked with URL: \(url)")
        // Parse URL parameters and navigate your App Clip UI accordingly
        // Example: url.host, url.path, URLComponents(url: url, resolvingAgainstBaseURL: false)?.queryItems
        if let components = URLComponents(url: url, resolvingAgainstBaseURL: false),
           let queryItems = components.queryItems {
            for item in queryItems {
                print("Query item: \(item.name) = \(item.value ?? "")")
            }
        }
    }
}
```

#### UIKit Example:

```swift
// SceneDelegate.swift in your App Clip target
import UIKit

class SceneDelegate: UIResponder, UIWindowSceneDelegate {

    var window: UIWindow?

    func scene(_ scene: UIScene, continue userActivity: NSUserActivity) {
        // Handle the invocation URL
        guard userActivity.activityType == NSUserActivityTypeBrowsingWeb,
              let incomingURL = userActivity.webpageURL else { return }

        handleAppClipInvocation(url: incomingURL)
    }

    func handleAppClipInvocation(url: URL) {
        print("App Clip invoked with URL: \(url)")
        // Parse URL parameters and navigate your App Clip UI accordingly
        // Example: url.host, url.path, URLComponents(url: url, resolvingAgainstBaseURL: false)?.queryItems
        if let components = URLComponents(url: url, resolvingAgainstBaseURL: false),
           let queryItems = components.queryItems {
            for item in queryItems {
                print("Query item: \(item.name) = \(item.value ?? "")")
            }
        }
        
        // Update UI based on URL
        if let rootVC = window?.rootViewController as? AppClipMainViewController {
            rootVC.configure(with: url) // Assuming you have a method to update the VC
        }
    }
}
```

This is where you'll parse the URL to determine what task the user wants to accomplish and configure your App Clip's UI accordingly.

```
┌─────────────────┐     ┌───────────────────────────────────┐     ┌───────────────────────┐
│ User Action     │     │ iOS System (Handles Invocation)   │     │ App Clip Target       │
│ (NFC, QR, Safari) ────► │ (Resolves URL, Launches App Clip) ────► │ (Receives URL,       │
└─────────────────┘     └───────────────────────────────────┘     │ Configures UI)        │
                                                                  └───────────────────────┘
```

### 4. Provide a Call to Action for the Full App

After a user completes a task in your App Clip, you should offer a clear path to download the full app. This is typically done using `SKOverlay` (for SwiftUI) or `SKStoreProductViewController` (for UIKit), which presents an App Store banner or sheet.

#### SwiftUI Example with `SKOverlay`:

```swift
import SwiftUI
import StoreKit

struct ContentView: View {
    @State private var showAppStoreOverlay = false

    var body: some View {
        VStack {
            Text("Welcome to the App Clip!")
                .font(.title)
                .padding()

            Button("Complete Task") {
                // Simulate task completion
                print("Task completed!")
                showAppStoreOverlay = true
            }
            .buttonStyle(.borderedProminent)
            .tint(.green)

            Spacer()
        }
        .appStoreOverlay(isPresented: $showAppStoreOverlay) {
            SKOverlay.AppClipConfiguration(position: .bottom)
        }
    }
}
```

#### UIKit Example with `SKStoreProductViewController`:

```swift
import UIKit
import StoreKit

class AppClipMainViewController: UIViewController {

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemBackground

        let completeTaskButton = UIButton(type: .system)
        completeTaskButton.setTitle("Complete Task", for: .normal)
        completeTaskButton.addTarget(self, action: #selector(didTapCompleteTask), for: .touchUpInside)
        completeTaskButton.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(completeTaskButton)

        NSLayoutConstraint.activate([
            completeTaskButton.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            completeTaskButton.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }

    @objc private func didTapCompleteTask() {
        print("Task completed!")
        presentAppStoreOverlay()
    }

    private func presentAppStoreOverlay() {
        // You'll need your app's Apple ID for this.
        // Replace 123456789 with your actual app ID.
        let parameters = [SKStoreProductParameterITunesItemIdentifier: 123456789]
        let storeVC = SKStoreProductViewController()
        storeVC.delegate = self
        storeVC.loadProduct(withParameters: parameters) { [weak self] success, error in
            if success {
                self?.present(storeVC, animated: true, completion: nil)
            } else if let error = error {
                print("Error loading App Store product: \(error.localizedDescription)")
            }
        }
    }
}

extension AppClipMainViewController: SKStoreProductViewControllerDelegate {
    func productViewControllerDidFinish(_ viewController: SKStoreProductViewController) {
        viewController.dismiss(animated: true, completion: nil)
    }
}
```

Note: `SKOverlay` is generally preferred for App Clips as it provides a less intrusive, system-managed banner.

### 5. Configure Experience in App Store Connect

After developing your App Clip, you need to configure its invocation experiences in App Store Connect. Go to your app's page, then "App Clips" tab. Here you can define:

*   **Default App Clip Experience**: Based on your app's primary associated domain, this is a fallback for general links.
*   **Advanced App Clip Experiences**: For specific URLs or locations, allowing you to customize the title, subtitle, image, and action button text that users see before launching the App Clip. This is crucial for tailored experiences.

## User Experience (UX) Considerations

A successful App Clip hinges on a great user experience:

*   **Keep it Simple**: Focus on one core task. Don't overwhelm the user with options.
*   **Fast Loading**: Minimize initial data fetches and asset loading. Every second counts.
*   **Minimal Setup**: Avoid extensive onboarding or account creation. Leverage Sign in with Apple for quick authentication if necessary.
*   **Clear Value Proposition**: The invocation card should clearly communicate what the App Clip does.
*   **Seamless Transition**: If the user decides to download the full app, ensure any data or state from the App Clip is transferred smoothly. You can use `NSUserActivity` for this.

## App Clip vs. Full App

It's important to understand the fundamental differences:

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 280" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Comparison table of App Clip versus Full App features and constraints">
  <title>App Clip vs. Full App Comparison</title>

  <!-- Styles -->
  <defs>
    <style>
      .header-box { fill: #1565c0; stroke: #1565c0; stroke-width: 1; }
      .header-text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 16px; fill: white; font-weight: bold; text-anchor: middle; }
      .row-box { fill: #f0f0f0; stroke: #ccc; stroke-width: 1; }
      .row-label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 14px; fill: #333; text-anchor: start; }
      .row-value { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 14px; fill: #333; text-anchor: middle; }
    </style>
  </defs>

  <!-- Table Headers -->
  <rect x="20" y="20" width="180" height="40" class="header-box" />
  <text x="110" y="45" class="header-text">Feature</text>

  <rect x="200" y="20" width="180" height="40" class="header-box" />
  <text x="290" y="45" class="header-text">App Clip</text>

  <rect x="380" y="20" width="180" height="40" class="header-box" />
  <text x="470" y="45" class="header-text">Full App</text>

  <!-- Row 1: Size -->
  <rect x="20" y="60" width="180" height="40" class="row-box" />
  <text x="30" y="85" class="row-label">Max Size</text>
  <rect x="200" y="60" width="180" height="40" class="row-box" />
  <text x="290" y="85" class="row-value">~15 MB</text>
  <rect x="380" y="60" width="180" height="40" class="row-box" />
  <text x="470" y="85" class="row-value">No Limit</text>

  <!-- Row 2: Installation -->
  <rect x="20" y="100" width="180" height="40" class="row-box" />
  <text x="30" y="125" class="row-label">Installation</text>
  <rect x="200" y="100" width="180" height="40" class="row-box" />
  <text x="290" y="125" class="row-value">Ephemeral</text>
  <rect x="380" y="100" width="180" height="40" class="row-box" />
  <text x="470" y="125" class="row-value">Permanent</text>

  <!-- Row 3: Discovery -->
  <rect x="20" y="140" width="180" height="40" class="row-box" />
  <text x="30" y="165" class="row-label">Discovery</text>
  <rect x="200" y="140" width="180" height="40" class="row-box" />
  <text x="290" y="165" class="row-value">Contextual (URL)</text>
  <rect x="380" y="140" width="180" height="40" class="row-box" />
  <text x="470" y="165" class="row-value">App Store, Home Screen</text>

  <!-- Row 4: Home Screen Icon -->
  <rect x="20" y="180" width="180" height="40" class="row-box" />
  <text x="30" y="205" class="row-label">Home Screen Icon</text>
  <rect x="200" y="180" width="180" height="40" class="row-box" />
  <text x="290" y="205" class="row-value">No</text>
  <rect x="380" y="180" width="180" height="40" class="row-box" />
  <text x="470" y="205" class="row-value">Yes</text>

  <!-- Row 5: Capabilities -->
  <rect x="20" y="220" width="180" height="40" class="row-box" />
  <text x="30" y="245" class="row-label">Capabilities</text>
  <rect x="200" y="220" width="180" height="40" class="row-box" />
  <text x="290" y="245" class="row-value">Limited</text>
  <rect x="380" y="220" width="180" height="40" class="row-box" />
  <text x="470" y="245" class="row-value">Full</text>

</svg>
</div>

## Summary

App Clips offer a powerful way to provide immediate value to users, significantly reducing the barrier to entry for your app's core functionality. By understanding their ephemeral nature, size constraints, and URL-driven invocation, you can design and implement App Clips that enhance user experience and drive full app adoption. Focus on a single, quick task, optimize for speed, and always provide a clear path to the full app experience.

Happy Swifting!
