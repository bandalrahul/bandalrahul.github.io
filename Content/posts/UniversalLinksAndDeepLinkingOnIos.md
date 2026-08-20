---
title: Universal Links and Deep Linking on iOS
date: 2026-08-20 09:25
description: Learn how to implement Universal Links and custom URL schemes for deep linking in your iOS applications, enhancing user experience and app discoverability.
tags: iOS, Development, Networking
---

# Universal Links and Deep Linking on iOS

In the world of mobile applications, providing a seamless and integrated user experience is paramount. One powerful way to achieve this is through **deep linking**, which allows you to launch your app and navigate directly to specific content within it from external sources like websites, emails, or other apps. On iOS, Apple provides two primary mechanisms for deep linking: **Custom URL Schemes** and the more robust **Universal Links**.

While custom URL schemes offer a straightforward way to open your app, Universal Links are Apple's recommended approach, providing a superior user experience and enhanced security. In this article, we'll dive deep into both, with a strong focus on implementing Universal Links, and equip you with the knowledge to integrate them effectively into your iOS applications.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 700 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Comparison of Custom URL Schemes vs. Universal Links">
  <title>Comparison of Custom URL Schemes vs. Universal Links</title>

  <!-- Common Starting Point -->
  <rect x="50" y="20" width="100" height="40" rx="5" fill="#1565c0" stroke="#0D47A1" stroke-width="2"/>
  <text x="100" y="45" font-family="Arial" font-size="14" fill="white" text-anchor="middle">User Taps Link</text>

  <!-- Custom URL Scheme Path -->
  <rect x="200" y="20" width="150" height="40" rx="5" fill="#F04B3E" stroke="#D32F2F" stroke-width="2"/>
  <text x="275" y="45" font-family="Arial" font-size="14" fill="white" text-anchor="middle">Custom URL Scheme (e.g., myapp://)</text>

  <line x1="150" y1="40" x2="200" y2="40" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="175" y="30" font-family="Arial" font-size="12" fill="#1565c0" text-anchor="middle">Path A</text>

  <rect x="200" y="80" width="150" height="40" rx="5" fill="#F04B3E" stroke="#D32F2F" stroke-width="2"/>
  <text x="275" y="105" font-family="Arial" font-size="14" fill="white" text-anchor="middle">OS Tries to Open App</text>

  <line x1="275" y1="60" x2="275" y2="80" stroke="#F04B3E" stroke-width="2" marker-end="url(#arrowhead)"/>

  <rect x="200" y="140" width="150" height="40" rx="5" fill="#F04B3E" stroke="#D32F2F" stroke-width="2"/>
  <text x="275" y="165" font-family="Arial" font-size="14" fill="white" text-anchor="middle">App Opens to Content</text>

  <line x1="275" y1="120" x2="275" y2="140" stroke="#F04B3E" stroke-width="2" marker-end="url(#arrowhead)"/>

  <rect x="200" y="200" width="150" height="40" rx="5" fill="#F04B3E" stroke="#D32F2F" stroke-width="2"/>
  <text x="275" y="225" font-family="Arial" font-size="14" fill="white" text-anchor="middle">If App Not Installed: Error</text>

  <line x1="275" y1="180" x2="275" y2="200" stroke="#F04B3E" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="275" y="190" font-family="Arial" font-size="12" fill="#F04B3E" text-anchor="middle">No Fallback</text>


  <!-- Universal Link Path -->
  <rect x="450" y="20" width="200" height="40" rx="5" fill="#2A8367" stroke="#1B5E20" stroke-width="2"/>
  <text x="550" y="45" font-family="Arial" font-size="14" fill="white" text-anchor="middle">Universal Link (e.g., https://)</text>

  <line x1="150" y1="40" x2="450" y2="40" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="300" y="30" font-family="Arial" font-size="12" fill="#1565c0" text-anchor="middle">Path B</text>

  <rect x="450" y="80" width="200" height="40" rx="5" fill="#2A8367" stroke="#1B5E20" stroke-width="2"/>
  <text x="550" y="105" font-family="Arial" font-size="14" fill="white" text-anchor="middle">OS Checks Associated Domain</text>

  <line x1="550" y1="60" x2="550" y2="80" stroke="#2A8367" stroke-width="2" marker-end="url(#arrowhead)"/>

  <rect x="450" y="140" width="200" height="40" rx="5" fill="#2A8367" stroke="#1B5E20" stroke-width="2"/>
  <text x="550" y="165" font-family="Arial" font-size="14" fill="white" text-anchor="middle">If App Installed: App Opens to Content</text>

  <line x1="550" y1="120" x2="550" y2="140" stroke="#2A8367" stroke-width="2" marker-end="url(#arrowhead)"/>

  <rect x="450" y="200" width="200" height="40" rx="5" fill="#2A8367" stroke="#1B5E20" stroke-width="2"/>
  <text x="550" y="225" font-family="Arial" font-size="14" fill="white" text-anchor="middle">If App Not Installed: Website Opens</text>

  <line x1="550" y1="180" x2="550" y2="200" stroke="#2A8367" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="550" y="190" font-family="Arial" font-size="12" fill="#2A8367" text-anchor="middle">Seamless Fallback</text>

  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="currentColor" />
    </marker>
  </defs>
</svg>
</div>

## Understanding Deep Linking Concepts

Before diving into implementation, let's clarify the two main types of deep linking on iOS.

### Custom URL Schemes

Custom URL schemes allow you to register a unique scheme for your app, like `myapp://`. When a user taps a link with this scheme (e.g., `myapp://products?id=123`), iOS attempts to open your app.

Here's how it generally works:

```
┌─────────────────┐     ┌───────────────────────┐     ┌───────────────────┐
│ Browser/Other App │ ──► │ iOS (myapp:// handler) │ ──► │ Your iOS App      │
└─────────────────┘     └───────────────────────┘     └───────────────────┘
```

**Pros:**
*   **Simple to set up:** Requires minimal configuration within your app's `Info.plist`.
*   **No server-side configuration:** No need to manage files on your web server.

**Cons:**
*   **Poor user experience if app isn't installed:** If the app isn't installed, the link will fail, often with an unhelpful "Safari cannot open the page" error. There's no graceful fallback to a website.
*   **Security risks:** Multiple apps can register the same custom URL scheme, leading to "scheme squatting" where an attacker's app could intercept links meant for your app. iOS will typically open the first app installed that registered that scheme, which is unpredictable.
*   **Limited context:** It's harder to pass complex data and maintain state across app launches.

### Universal Links

Introduced in iOS 9, Universal Links are standard HTTP/HTTPS links (e.g., `https://yourdomain.com/products?id=123`) that your web server is configured to handle for your app. When a user taps a Universal Link, iOS checks if your app is installed and configured to handle that specific domain. If so, your app launches directly to the specified content without going through Safari. If not, the link opens in Safari, providing a seamless fallback to your website.

**Pros:**
*   **Seamless user experience:** Links open directly in your app if installed, or gracefully fall back to your website if not.
*   **Secure:** Only your app can open links for your verified domain, preventing scheme squatting.
*   **Standard web links:** They are regular web links, meaning they work everywhere (email, social media, etc.) and are discoverable by search engines.
*   **Better analytics:** You can track clicks on your web server.

**Cons:**
*   **Requires server-side configuration:** You need control over your web server to host a special configuration file.
*   **More complex setup:** Involves both app-side and server-side setup.

Given the significant advantages, Universal Links are the recommended approach for deep linking on iOS.

## Implementing Universal Links

Implementing Universal Links involves two main parts: server-side configuration and app-side configuration.

### 1. Server-Side Configuration: The `apple-app-site-association` File

The core of Universal Links lies in a file hosted on your web server called `apple-app-site-association` (AASA). This JSON file tells iOS which app IDs are associated with which paths on your domain.

**a. Create the AASA File:**

The AASA file must be a JSON file with a specific structure. Here's an example:

```json
{
  "applinks": {
    "apps": [],
    "details": [
      {
        "appID": "YOUR_TEAM_ID.com.yourcompany.yourapp",
        "paths": [
          "/products/*",
          "/articles/*",
          "/promo/*",
          "NOT /promo/restricted/*"
        ]
      }
    ]
  }
}
```

*   **`appID`**: This is your Apple Team ID followed by your app's Bundle Identifier. You can find your Team ID in your Apple Developer account (`Membership` section) or in Xcode under Project settings -> General -> Identity -> Team.
*   **`paths`**: An array of strings specifying which paths on your domain your app can handle.
    *   Use `*` as a wildcard to match any substring. For example, `/products/*` matches `/products/123`, `/products/new`, etc.
    *   Use `?` as a wildcard for a single character.
    *   Use `NOT` prefix to exclude specific paths. This is crucial for security and preventing unintended app launches.
*   **`apps`**: This array is deprecated and should be empty.

**b. Host the AASA File:**

The `apple-app-site-association` file must be hosted at one of two specific locations on your domain:
*   `https://yourdomain.com/apple-app-site-association`
*   `https://yourdomain.com/.well-known/apple-app-site-association`

**Crucial Hosting Requirements:**
*   **HTTPS Only:** The file *must* be served over HTTPS.
*   **No Redirects:** The file must be directly accessible without any HTTP redirects.
*   **MIME Type:** The server must serve the file with the `application/json` or `text/plain` MIME type.
*   **No File Extension:** The file name must be exactly `apple-app-site-association` without any `.json` extension.

You can verify your AASA file setup using Apple's [App Search API Validation Tool](https://search.developer.apple.com/appsearch-validation-tool/).

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 700 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Universal Link Setup Flow">
  <title>Universal Link Setup Flow</title>

  <!-- Colors -->
  <style>
    .green-fill { fill: #2A8367; stroke: #1B5E20; stroke-width: 2; }
    .blue-fill { fill: #1565c0; stroke: #0D47A1; stroke-width: 2; }
    .text-white { fill: white; font-family: Arial; font-size: 14; text-anchor: middle; }
    .text-green { fill: #2A8367; font-family: Arial; font-size: 12; text-anchor: middle; }
    .text-blue { fill: #1565c0; font-family: Arial; font-size: 12; text-anchor: middle; }
    .arrow { stroke: #1565c0; stroke-width: 2; marker-end: url(#arrowhead); }
    .arrow-green { stroke: #2A8367; stroke-width: 2; marker-end: url(#arrowhead); }
  </style>

  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="currentColor" />
    </marker>
  </defs>

  <!-- Blocks -->
  <rect x="50" y="20" width="120" height="60" rx="5" class="blue-fill"/>
  <text x="110" y="55" class="text-white">Your Web Server</text>

  <rect x="220" y="20" width="180" height="60" rx="5" class="green-fill"/>
  <text x="310" y="55" class="text-white">`apple-app-site-association` File (AASA)</text>

  <rect x="470" y="20" width="180" height="60" rx="5" class="blue-fill"/>
  <text x="560" y="55" class="text-white">Apple's CDN (for AASA Caching)</text>

  <rect x="50" y="120" width="120" height="60" rx="5" class="blue-fill"/>
  <text x="110" y="155" class="text-white">User Taps Link</text>

  <rect x="220" y="120" width="180" height="60" rx="5" class="blue-fill"/>
  <text x="310" y="155" class="text-white">iOS Device</text>

  <rect x="470" y="120" width="180" height="60" rx="5" class="green-fill"/>
  <text x="560" y="155" class="text-white">Your iOS App</text>

  <rect x="310" y="220" width="180" height="60" rx="5" class="blue-fill"/>
  <text x="400" y="255" class="text-white">Safari / Web Browser</text>

  <!-- Arrows and Labels -->
  <line x1="170" y1="50" x2="220" y2="50" class="arrow-green"/>
  <text x="195" y="40" class="text-green">Hosts</text>

  <line x1="400" y1="50" x2="470" y2="50" class="arrow-blue"/>
  <text x="435" y="40" class="text-blue">Caches</text>

  <line x1="110" y1="80" x2="110" y2="120" class="arrow"/>
  <line x1="110" y1="150" x2="220" y2="150" class="arrow"/>
  <text x="165" y="140" class="text-blue">Link to domain</text>

  <line x1="310" y1="80" x2="310" y2="120" class="arrow"/>
  <text x="310" y="100" class="text-blue">Downloads & Verifies AASA</text>

  <line x1="400" y1="150" x2="470" y2="150" class="arrow"/>
  <text x="435" y="140" class="text-green">If App Installed & Matched</text>

  <line x1="400" y1="170" x2="310" y2="220" class="arrow"/>
  <text x="355" y="200" class="text-blue">If App Not Installed/Matched</text>

</svg>
</div>

### 2. App-Side Configuration

**a. Add Associated Domains Entitlement:**

In Xcode, for your target:
1.  Go to the `Signing & Capabilities` tab.
2.  Click `+ Capability` and add `Associated Domains`.
3.  Under `Associated Domains`, add an entry for each domain that will host your Universal Links, prefixed with `applinks:`.
    *   Example: `applinks:yourdomain.com`
    *   If you have subdomains, you might add `applinks:*.yourdomain.com` or specific subdomains like `applinks:shop.yourdomain.com`.

This tells iOS that your app is capable of handling links from `yourdomain.com`. When a user installs your app, iOS will fetch the AASA file from your associated domain to confirm the association.

**b. Handle Universal Links in Your App:**

When your app is launched via a Universal Link, iOS delivers the URL to your app. How you handle it depends on your app's lifecycle structure:

*   **For UIKit apps using `AppDelegate` (older lifecycle):**
    ```swift
    func application(_ application: UIApplication, continue userActivity: NSUserActivity, restorationHandler: @escaping ([UIUserActivityRestoring]?) -> Void) -> Bool {
        guard userActivity.activityType == NSUserActivityTypeBrowsingWeb,
              let incomingURL = userActivity.webpageURL else {
            return false
        }

        print("Incoming Universal Link: \(incomingURL.absoluteString)")
        handleIncomingURL(incomingURL)
        return true
    }
    ```

*   **For SwiftUI apps or UIKit apps using `SceneDelegate` (modern lifecycle):**
    ```swift
    class SceneDelegate: UIResponder, UIWindowSceneDelegate {
        var window: UIWindow?

        func scene(_ scene: UIScene, continue userActivity: NSUserActivity) {
            guard userActivity.activityType == NSUserActivityTypeBrowsingWeb,
                  let incomingURL = userActivity.webpageURL else {
                return
            }

            print("Incoming Universal Link: \(incomingURL.absoluteString)")
            handleIncomingURL(incomingURL)
        }

        // ... other SceneDelegate methods
    }
    ```
    If you're using SwiftUI's `App` lifecycle, you can use the `onOpenURL` modifier:
    ```swift
    @main
    struct MyApp: App {
        var body: some Scene {
            WindowGroup {
                ContentView()
                    .onOpenURL { url in
                        print("Incoming URL from onOpenURL: \(url.absoluteString)")
                        handleIncomingURL(url)
                    }
            }
        }

        // Your global URL handler, or pass it down to views
        func handleIncomingURL(_ url: URL) {
            // Logic to parse the URL and navigate
            // Example:
            if url.pathComponents.contains("products") {
                if let productID = url.queryParameters?["id"] {
                    print("Navigating to product with ID: \(productID)")
                    // Trigger navigation in your app, e.g., via a Router or state change
                }
            } else if url.pathComponents.contains("articles") {
                if let articleSlug = url.lastPathComponent {
                    print("Navigating to article with slug: \(articleSlug)")
                }
            }
        }
    }
    ```

### 3. Parsing the URL and Navigation

The `handleIncomingURL` function is where you'll implement your routing logic. You'll need to parse the `URL` object to extract paths and query parameters.

A handy extension for `URL` to get query parameters:

```swift
extension URL {
    var queryParameters: [String: String]? {
        guard let components = URLComponents(url: self, resolvingAgainstBaseURL: false),
              let queryItems = components.queryItems else { return nil }

        var parameters = [String: String]()
        for item in queryItems {
            parameters[item.name] = item.value
        }
        return parameters
    }
}
```

Now, your `handleIncomingURL` can use this:

```swift
func handleIncomingURL(_ url: URL) {
    guard let host = url.host else { return }

    // Example logic for a simple routing
    switch host {
    case "yourdomain.com":
        if url.pathComponents.contains("products") {
            if let productID = url.queryParameters?["id"] {
                print("Navigating to product detail for ID: \(productID)")
                // Your app's navigation logic here
                // e.g., router.showProduct(id: productID)
            }
        } else if url.pathComponents.contains("articles") {
            if let articleSlug = url.lastPathComponent, articleSlug != "articles" {
                print("Navigating to article: \(articleSlug)")
                // e.g., router.showArticle(slug: articleSlug)
            }
        } else {
            print("Unhandled path on yourdomain.com: \(url.path)")
        }
    default:
        print("Unhandled host: \(host)")
        // Maybe open a generic home screen or log an unknown link
    }
}
```

## Testing Universal Links

Testing Universal Links can sometimes be tricky. Here are a few methods:

1.  **Notes App:** The simplest way. Type your Universal Link (e.g., `https://yourdomain.com/products/123`) into the Notes app. Long-press on the link; you should see an option to "Open in [Your App Name]". If you don't, something is wrong.
2.  **Safari:** Type your link into Safari. If your app is installed and configured correctly, the link should open directly in your app. If it opens in Safari, look for a small banner at the top of the screen that says "Open" or "Open in [Your App Name]". This banner indicates that Universal Links are working but the OS decided to open in Safari first (e.g., if you recently dismissed the app).
3.  **`xcrun simctl openurl`:** For simulators, you can use the command line:
    ```bash
    xcrun simctl openurl booted "https://yourdomain.com/products/123"
    ```
4.  **Debugging:** Set breakpoints in your `application(_:continue:restorationHandler:)` or `scene(_:continueUserActivity:)` methods to see if the URL is being received.

**Common Pitfalls:**
*   Incorrect `appID` in AASA file.
*   AASA file not served over HTTPS, with correct MIME type, or at the correct path.
*   AASA file contains redirects.
*   Incorrect `Associated Domains` entitlement (e.g., missing `applinks:` prefix).
*   App not provisioned correctly for Associated Domains.
*   Caching issues (Apple's CDN caches AASA files, sometimes taking time to update).
*   Using `UIWebView` or `WKWebView` to open a Universal Link within your own app (these will not trigger your app's Universal Link handler).

## Custom URL Schemes (When Still Useful)

While Universal Links are generally preferred, custom URL schemes still have their place, primarily for inter-app communication when you control both apps. For instance, if you have a suite of apps, one app might launch another using a custom scheme to perform a specific action.

To implement a custom URL scheme:

1.  **Register the Scheme:** In your Xcode project, open `Info.plist` (or the `Info` tab in project settings).
    *   Add a new `URL Types` array.
    *   Add a new item to `URL Types`.
    *   Set `URL Schemes` to an array containing your desired scheme (e.g., `myapp`).
    *   Set `Identifier` (e.g., `com.yourcompany.myapp.scheme`).
    *   Set `Role` to `Editor` or `Viewer`.

2.  **Handle the Scheme:**
    *   **For UIKit apps using `AppDelegate`:**
        ```swift
        func application(_ app: UIApplication, open url: URL, options: [UIApplication.OpenURLOptionsKey : Any] = [:]) -> Bool {
            print("Incoming Custom URL Scheme: \(url.absoluteString)")
            handleIncomingCustomSchemeURL(url)
            return true
        }
        ```
    *   **For SwiftUI apps or UIKit apps using `SceneDelegate`:** Use the `onOpenURL` modifier as shown for Universal Links, but handle the custom scheme logic within it. The `URL` object will start with your custom scheme (e.g., `myapp://products?id=123`).

    ```swift
    func handleIncomingCustomSchemeURL(_ url: URL) {
        if url.scheme == "myapp" {
            // Parse path and query parameters specific to your 'myapp' scheme
            if url.host == "products", let productID = url.queryParameters?["id"] {
                print("Custom scheme: Navigating to product with ID: \(productID)")
            }
        }
    }
    ```

## Summary

Deep linking is a powerful tool to enhance user engagement and provide a seamless experience in your iOS app. While custom URL schemes offer a simple solution for specific inter-app communication scenarios, **Universal Links** are the clear winner for general-purpose deep linking from web content. They provide a secure, reliable, and user-friendly way to connect your website content directly to your app, with a graceful fallback to the web if the app isn't installed.

By carefully configuring your `apple-app-site-association` file on your server and correctly handling `NSUserActivity` in your iOS app, you can unlock a superior deep linking experience for your users.

Happy Swifting!
