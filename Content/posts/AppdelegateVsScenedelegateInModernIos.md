---
title: AppDelegate vs SceneDelegate in Modern iOS
date: 2026-09-07 14:38
description: Understand the roles of AppDelegate and SceneDelegate in modern iOS apps, how they manage app and UI lifecycles, and their interactions for multi-window support.
tags: UIKit, iOS, Development
---

# AppDelegate vs SceneDelegate in Modern iOS

For many years, the `AppDelegate` was the undisputed central hub for managing an iOS app's lifecycle. It handled everything from launch to termination, push notifications, URL schemes, and even setting up the app's initial UI `UIWindow`. Then, with iOS 13 and the advent of multi-window support on iPadOS and Mac Catalyst, Apple introduced the `SceneDelegate`. This addition often creates confusion for developers, especially when working on projects that support older iOS versions or transitioning from legacy codebases.

In this article, we'll demystify the roles of `AppDelegate` and `SceneDelegate`, explore why `SceneDelegate` came into existence, and clarify their responsibilities in modern iOS development. By the end, you'll have a clear understanding of how these two crucial components work together to manage your app's lifecycle and UI.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Evolution of iOS App Lifecycle Management">
  <title>Evolution of iOS App Lifecycle Management</title>

  <!-- Pre-iOS 13 -->
  <rect x="50" y="20" width="220" height="180" rx="10" ry="10" fill="#E0E0E0" stroke="#CCCCCC" stroke-width="1"/>
  <text x="160" y="45" font-family="Arial, sans-serif" font-size="16" font-weight="bold" text-anchor="middle" fill="#333">Pre-iOS 13</text>
  <rect x="80" y="60" width="160" height="40" rx="5" ry="5" fill="#2A8367" stroke="#1F5C48" stroke-width="1"/>
  <text x="160" y="85" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="white">AppDelegate</text>
  <path d="M160,100 L160,120" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <rect x="80" y="120" width="160" height="40" rx="5" ry="5" fill="#1565c0" stroke="#0F4C92" stroke-width="1"/>
  <text x="160" y="145" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="white">UIWindow</text>
  <path d="M160,160 L160,180" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <rect x="80" y="180" width="160" height="20" rx="5" ry="5" fill="#F04B3E" stroke="#B0372E" stroke-width="1"/>
  <text x="160" y="195" font-family="Arial, sans-serif" font-size="12" text-anchor="middle" fill="white">Root ViewController</text>

  <!-- Post-iOS 13 -->
  <rect x="330" y="20" width="220" height="180" rx="10" ry="10" fill="#E0E0E0" stroke="#CCCCCC" stroke-width="1"/>
  <text x="440" y="45" font-family="Arial, sans-serif" font-size="16" font-weight="bold" text-anchor="middle" fill="#333">Post-iOS 13</text>
  <rect x="360" y="60" width="160" height="30" rx="5" ry="5" fill="#2A8367" stroke="#1F5C48" stroke-width="1"/>
  <text x="440" y="80" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="white">AppDelegate</text>
  <path d="M440,90 L440,105" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <rect x="360" y="105" width="160" height="30" rx="5" ry="5" fill="#1565c0" stroke="#0F4C92" stroke-width="1"/>
  <text x="440" y="125" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="white">SceneDelegate</text>
  <path d="M440,135 L440,150" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <rect x="360" y="150" width="160" height="20" rx="5" ry="5" fill="#1565c0" stroke="#0F4C92" stroke-width="1"/>
  <text x="440" y="165" font-family="Arial, sans-serif" font-size="12" text-anchor="middle" fill="white">UIWindow</text>
  <path d="M440,170 L440,180" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <rect x="360" y="180" width="160" height="20" rx="5" ry="5" fill="#F04B3E" stroke="#B0372E" stroke-width="1"/>
  <text x="440" y="195" font-family="Arial, sans-serif" font-size="12" text-anchor="middle" fill="white">Root ViewController</text>

  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
    </marker>
  </defs>
</svg>
</div>

## The `AppDelegate`: The Original App Lifecycle Manager

Before iOS 13, the `AppDelegate` class was the single point of entry for all major application-level events. It conformed to the `UIApplicationDelegate` protocol and was responsible for:

*   **App Launch and Termination**: Knowing when the app started and ended.
*   **State Transitions**: Responding to the app moving to and from the background, becoming active, or resigning active status.
*   **Core Services Setup**: Initializing frameworks like Core Data, setting up push notifications, handling URL schemes, and managing background tasks.
*   **UIWindow Management**: Creating the `UIWindow` object and setting its `rootViewController`.

Here's a look at some common `AppDelegate` methods you might remember or still encounter in older projects:

```swift
import UIKit
import CoreData // Example for app-wide service

@main
class AppDelegate: UIResponder, UIApplicationDelegate {

    // Pre-iOS 13, this was used to create the window and set its root view controller.
    // For iOS 13+, this property is typically nil if using SceneDelegate.
    var window: UIWindow?

    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        // Perform app-wide initialization here
        print("App did finish launching.")
        // Example: Setup Core Data stack, configure analytics, etc.
        setupCoreDataStack()
        return true
    }

    func applicationWillResignActive(_ application: UIApplication) {
        // Sent when the application is about to move from active to inactive state.
        // This can occur for certain types of temporary interruptions (such as an incoming phone call or SMS message)
        // or when the user quits the application and it begins the transition to the background state.
        print("App will resign active.")
    }

    func applicationDidEnterBackground(_ application: UIApplication) {
        // Use this method to release shared resources, save user data, invalidate timers,
        // and store enough application state information to restore your application to its current state in case it is terminated later.
        print("App did enter background.")
    }

    func applicationWillEnterForeground(_ application: UIApplication) {
        // Called as part of the transition from the background to the active state;
        // here you can undo many of the changes made on entering the background.
        print("App will enter foreground.")
    }

    func applicationDidBecomeActive(_ application: UIApplication) {
        // Restart any tasks that were paused (or not yet started) while the application was inactive.
        // If the application was previously in the background, optionally refresh the user interface.
        print("App did become active.")
    }

    func applicationWillTerminate(_ application: UIApplication) {
        // Called when the application is about to terminate. Save data if appropriate.
        print("App will terminate.")
    }

    // Example of an app-wide service setup
    private func setupCoreDataStack() {
        // Core Data setup logic here...
        print("Core Data stack initialized.")
    }

    // MARK: - UISceneSession lifecycle (for iOS 13+ only)
    // These methods are crucial for AppDelegate's role in managing scenes.
    func application(_ application: UIApplication, configurationForConnecting connectingSceneSession: UISceneSession, options: UIScene.ConnectionOptions) -> UISceneConfiguration {
        // Called when a new scene session is being created.
        // Use this method to select a configuration to create the new scene with.
        print("AppDelegate: Requesting configuration for new scene session.")
        return UISceneConfiguration(name: "Default Configuration", sessionRole: connectingSceneSession.role)
    }

    func application(_ application: UIApplication, didDiscardSceneSessions sceneSessions: Set<UISceneSession>) {
        // Called when the user discards a scene session.
        // If any sessions were discarded while the application was not running, this will be called shortly after application:didFinishLaunchingWithOptions.
        // Use this method to release any resources that were specific to the discarded scenes, as they will not return.
        print("AppDelegate: Did discard scene sessions: \(sceneSessions.count)")
    }
}
```

## The Rise of `SceneDelegate` (iOS 13+): Multi-Window Support

With iOS 13, Apple introduced the concept of "scenes" to support multi-window experiences on iPadOS (and later Mac Catalyst). A scene represents a single instance of your app's user interface, which can be running independently. For example, on an iPad, a user might have two instances of the same app open side-by-side, each with its own `UIWindow` and view hierarchy. Each of these instances is managed by its own `SceneDelegate`.

The `SceneDelegate` conforms to the `UIWindowSceneDelegate` protocol and is responsible for:

*   **Managing a Single UI Window**: It holds a reference to the `UIWindow` object for its specific scene.
*   **Setting the Root View Controller**: It's where you typically instantiate and assign the `rootViewController` for that scene's window.
*   **Scene-Specific Lifecycle Events**: Responding to events related to its particular UI instance, such as when a scene becomes active, enters the background, or is disconnected.
*   **State Restoration**: Handling the saving and restoring of UI state for its specific scene.
*   **Deep Links**: Processing URL schemes or user activities that are specific to that scene.

Here's what a typical `SceneDelegate` looks like:

```swift
import UIKit

class SceneDelegate: UIResponder, UIWindowSceneDelegate {

    var window: UIWindow? // This window is specific to *this scene*

    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options connectionOptions: UIScene.ConnectionOptions) {
        // Use this method to optionally configure and attach the UIWindow `window` to the provided UIWindowScene `scene`.
        // If using a storyboard, the `window` property will automatically be initialized and attached to the scene.
        // This delegate does not imply the connecting scene is the default or only scene for your application.
        guard let windowScene = (scene as? UIWindowScene) else { return }

        print("SceneDelegate: Scene will connect to session.")

        // Create a new UIWindow for this scene
        window = UIWindow(windowScene: windowScene)

        // Instantiate your root view controller
        let rootViewController = ViewController() // Replace with your actual root VC
        window?.rootViewController = rootViewController

        // Make this window the key window and visible
        window?.makeKeyAndVisible()

        // Handle deep links or user activities specific to this scene
        if let userActivity = connectionOptions.userActivities.first ?? session.stateRestorationActivity {
            // Process user activity here
            print("SceneDelegate: Handled user activity: \(userActivity.activityType)")
        }
        if let urlContext = connectionOptions.urlContexts.first {
            // Process URL here
            print("SceneDelegate: Handled URL: \(urlContext.url)")
        }
    }

    func sceneDidDisconnect(_ scene: UIScene) {
        // Called as the scene is being released by the system.
        // This occurs shortly after the scene enters the background, or when its session is discarded.
        // Release any resources associated with this scene that can be re-created the next time the scene connects.
        // The scene may re-connect later, as its session was not necessarily discarded.
        print("SceneDelegate: Scene did disconnect.")
    }

    func sceneDidBecomeActive(_ scene: UIScene) {
        // Called when the scene has moved from an inactive state to an active state.
        // Use this method to restart any tasks that were paused (or not yet started) when the scene was inactive.
        print("SceneDelegate: Scene did become active.")
    }

    func sceneWillResignActive(_ scene: UIScene) {
        // Called when the scene will move from an active state to an inactive state.
        // This may occur due to temporary interruptions (ex. an incoming phone call).
        print("SceneDelegate: Scene will resign active.")
    }

    func sceneWillEnterForeground(_ scene: UIScene) {
        // Called as the scene transitions from the background to the foreground.
        // Use this method to undo the changes made on entering the background.
        print("SceneDelegate: Scene will enter foreground.")
    }

    func sceneDidEnterBackground(_ scene: UISene) {
        // Called as the scene transitions from the foreground to the background.
        // Use this method to save data, release shared resources, and store enough scene-specific state information
        // to restore the scene back to its current state.
        print("SceneDelegate: Scene did enter background.")
    }
}
```

## The Relationship: `AppDelegate` and `SceneDelegate` Together

The introduction of `SceneDelegate` didn't make `AppDelegate` obsolete; rather, it redefined its role. Now, `AppDelegate` is primarily concerned with *app-wide* lifecycle events and managing *scenes*, not the UI itself.

Here's how they interact:

```
┌──────────────────┐
│   App Launch     │
└──────────────────┘
        │
        ▼
┌──────────────────┐
│   AppDelegate    │
│ (App-level life  │
│  & Scene Mgmt)   │
└──────────────────┘
        │
        ▼  (Request for Scene)
┌──────────────────┐
│ UISceneSession   │
│ (One or more)    │
└──────────────────┘
        │
        ▼  (Connect to Session)
┌──────────────────┐
│   SceneDelegate  │
│  (UI-level life  │
│   & Window Mgmt) │
└──────────────────┘
        │
        ▼
┌──────────────────┐
│    UIWindow      │
└──────────────────┘
        │
        ▼
┌──────────────────┐
│ Root ViewController │
└──────────────────┘
```

**`AppDelegate`'s Remaining Responsibilities (App-wide):**

*   **App Process Lifecycle**: `application(_:didFinishLaunchingWithOptions:)`, `applicationWillTerminate(_:)`. These are truly global for the entire application process.
*   **Scene Management**: The `AppDelegate` is responsible for providing `UISceneConfiguration` objects when the system requests a new scene (`application(_:configurationForConnectingSceneSession:options:)`). It also handles `didDiscardSceneSessions`, notifying when a scene is removed.
*   **Push Notifications Setup**: Registering for push notifications and handling device tokens.
*   **Core Data Stack**: If your app uses Core Data, the persistent container setup often remains in `AppDelegate` as it's an app-wide resource.
*   **App-wide Services**: Initializing third-party SDKs that are truly global and not tied to a specific UI instance (e.g., analytics, crash reporting).
*   **URL Handling (Fallback/Global)**: While `SceneDelegate` is preferred for scene-specific deep links, `AppDelegate` can still handle global URL schemes or as a fallback.

**`SceneDelegate`'s Responsibilities (Scene-specific):**

*   **UI Window Management**: Creating and managing the `UIWindow` for its specific scene.
*   **Root View Controller Setup**: Setting the `rootViewController` for that scene's window.
*   **Scene State Transitions**: `sceneDidBecomeActive(_:)`, `sceneWillResignActive(_:)`, `sceneDidEnterBackground(_:)`, `sceneWillEnterForeground(_:)`, `sceneDidDisconnect(_:)`. These methods relate to the visibility and activity of that particular UI instance.
*   **Scene-Specific Deep Links/User Activities**: Handling `scene(_:openURLContexts:)` or `scene(_:continue:)` for URLs or user activities directed at that specific UI.
*   **State Restoration**: Saving and restoring the UI state of a particular scene.

## Practical Scenarios

Let's look at how this split of responsibilities manifests in common development tasks.

### Initializing the UI

In an iOS 13+ app, the `AppDelegate` is no longer directly responsible for creating the `UIWindow` or setting the `rootViewController`. That's `SceneDelegate`'s job.

**`AppDelegate.swift` (Minimal for UI setup):**

```swift
import UIKit

@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    func application(_ application: UIApplication, configurationForConnecting connectingSceneSession: UISceneSession, options: UIScene.ConnectionOptions) -> UISceneConfiguration {
        // Provide the configuration for a new scene.
        return UISceneConfiguration(name: "Default Configuration", sessionRole: connectingSceneSession.role)
    }

    // Other app-wide lifecycle methods here...
}
```

**`SceneDelegate.swift` (UI setup):**

```swift
import UIKit

class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    var window: UIWindow?

    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options connectionOptions: UIScene.ConnectionOptions) {
        guard let windowScene = (scene as? UIWindowScene) else { return }

        window = UIWindow(windowScene: windowScene)
        window?.rootViewController = MainTabBarController() // Your app's main UI entry point
        window?.makeKeyAndVisible()
    }

    // Other scene-specific lifecycle methods here...
}
```
This separation allows each scene to manage its own UI independently, crucial for multi-window iPad experiences where different windows might display different parts of your app or even the same part with different data.

### Handling Deep Links

Deep links (custom URL schemes, universal links, `NSUserActivity`) can technically be handled in either delegate, but the best practice for iOS 13+ is to handle them in the `SceneDelegate` if they are meant to navigate or update the UI of a specific scene.

**`SceneDelegate.swift` (Handling a deep link for its scene):**

```swift
// ... inside SceneDelegate class ...

func scene(_ scene: UIScene, openURLContexts URLContexts: Set<UIOpenURLContext>) {
    guard let urlContext = URLContexts.first else { return }
    let url = urlContext.url

    print("SceneDelegate: Received URL: \(url.absoluteString)")

    // Example: Parse the URL and navigate within this scene's UI
    if url.host == "products" && url.pathComponents.count > 1 {
        let productID = url.pathComponents[1]
        // Assuming your rootViewController can handle this navigation
        (window?.rootViewController as? MainTabBarController)?.navigateToProduct(with: productID)
    }
}
```
If a deep link needs to affect *all* scenes, or if it's a global action not tied to a specific UI, the `AppDelegate` might still be used, but this is less common with modern scene-based apps.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 250" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="AppDelegate vs SceneDelegate Responsibilities">
  <title>AppDelegate vs SceneDelegate Responsibilities</title>

  <!-- Box for AppDelegate -->
  <rect x="30" y="30" width="260" height="190" rx="10" ry="10" fill="#E8F5E9" stroke="#2A8367" stroke-width="2"/>
  <text x="160" y="55" font-family="Arial, sans-serif" font-size="18" font-weight="bold" text-anchor="middle" fill="#2A8367">AppDelegate</text>
  <text x="160" y="75" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">(App-wide Scope)</text>
  <line x1="40" y1="90" x2="280" y2="90" stroke="#2A8367" stroke-dasharray="3,3"/>
  <text x="50" y="110" font-family="Arial, sans-serif" font-size="13" fill="#333">• App Process Lifecycle</text>
  <text x="50" y="130" font-family="Arial, sans-serif" font-size="13" fill="#333">• Scene Management (Creation/Discard)</text>
  <text x="50" y="150" font-family="Arial, sans-serif" font-size="13" fill="#333">• Push Notifications Setup</text>
  <text x="50" y="170" font-family="Arial, sans-serif" font-size="13" fill="#333">• Core Data Stack / App-wide Services</text>
  <text x="50" y="190" font-family="Arial, sans-serif" font-size="13" fill="#333">• Global URL Handling (Fallback)</text>
  <text x="50" y="210" font-family="Arial, sans-serif" font-size="13" fill="#333">• `application(_:didFinishLaunchingWithOptions:)`</text>


  <!-- Box for SceneDelegate -->
  <rect x="310" y="30" width="260" height="190" rx="10" ry="10" fill="#E3F2FD" stroke="#1565c0" stroke-width="2"/>
  <text x="440" y="55" font-family="Arial, sans-serif" font-size="18" font-weight="bold" text-anchor="middle" fill="#1565c0">SceneDelegate</text>
  <text x="440" y="75" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">(Scene-specific Scope)</text>
  <line x1="320" y1="90" x2="560" y2="90" stroke="#1565c0" stroke-dasharray="3,3"/>
  <text x="330" y="110" font-family="Arial, sans-serif" font-size="13" fill="#333">• `UIWindow` Management</text>
  <text x="330" y="130" font-family="Arial, sans-serif" font-size="13" fill="#333">• Root View Controller Setup</text>
  <text x="330" y="150" font-family="Arial, sans-serif" font-size="13" fill="#333">• Scene State Transitions (Active, Background)</text>
  <text x="330" y="170" font-family="Arial, sans-serif" font-size="13" fill="#333">• Scene-specific Deep Links / User Activities</text>
  <text x="330" y="190" font-family="Arial, sans-serif" font-size="13" fill="#333">• Scene State Restoration</text>
  <text x="330" y="210" font-family="Arial, sans-serif" font-size="13" fill="#333">• `scene(_:willConnectTo:options:)`</text>

</svg>
</div>

## Summary

The transition from a single `AppDelegate` to a combined `AppDelegate` and `SceneDelegate` model in iOS 13+ marks a significant evolution in how iOS apps manage their lifecycle and UI. While the `AppDelegate` retains its role as the gatekeeper for the entire application process and scene management, the `SceneDelegate` has become the dedicated manager for individual UI instances (scenes).

For modern iOS development, especially when targeting iOS 13 and later, remember this crucial distinction:
*   **`AppDelegate`**: Handles application-wide events, manages the creation and destruction of scenes, and sets up global services (e.g., push notifications, Core Data stack).
*   **`SceneDelegate`**: Manages the lifecycle of a single `UIWindowScene`, including its `UIWindow`, `rootViewController`, and scene-specific events like foreground/background transitions and deep links that affect only that scene.

By understanding and leveraging this separation of concerns, you can build more robust, modular, and multi-window capable iOS applications.

Happy Swifting!
