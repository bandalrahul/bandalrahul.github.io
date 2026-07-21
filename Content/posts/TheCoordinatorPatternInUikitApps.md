---
title: The Coordinator Pattern in UIKit Apps
date: 2026-07-21 10:59
description: Learn how the Coordinator pattern decouples navigation logic from UIViewControllers, making your UIKit apps more modular, testable, and maintainable.
tags: UIKit, iOS, Architecture
---

# The Coordinator Pattern in UIKit Apps

UIKit applications, especially those with complex navigation flows, often face a common challenge: massive view controllers. While Model-View-Controller (MVC) is the default architectural pattern for UIKit, it frequently leads to view controllers becoming overloaded with responsibilities, including managing navigation logic. This can make code harder to read, test, and maintain.

Enter the **Coordinator Pattern**. This powerful architectural approach helps to extract navigation and flow logic out of your `UIViewController` subclasses, leading to cleaner, more modular, and more testable codebases. If you've ever found yourself with `UIViewController` files spanning thousands of lines, riddled with `present`, `push`, and `dismiss` calls, then the Coordinator pattern might be exactly what your project needs.

In this article, we'll dive deep into the Coordinator pattern, understand its core components, walk through a practical implementation, and discuss its benefits and trade-offs.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Traditional MVC Navigation Problem">
  <title>Traditional MVC Navigation Problem: View Controllers tightly coupled</title>

  <!-- Boxes for View Controllers -->
  <rect x="50" y="50" width="150" height="50" fill="#1565c0" rx="5" ry="5" stroke="#0d47a1" stroke-width="2"/>
  <text x="125" y="77" font-family="Arial" font-size="16" fill="white" text-anchor="middle">VC A</text>

  <rect x="250" y="50" width="150" height="50" fill="#1565c0" rx="5" ry="5" stroke="#0d47a1" stroke-width="2"/>
  <text x="325" y="77" font-family="Arial" font-size="16" fill="white" text-anchor="middle">VC B</text>

  <rect x="450" y="50" width="150" height="50" fill="#1565c0" rx="5" ry="5" stroke="#0d47a1" stroke-width="2"/>
  <text x="525" y="77" font-family="Arial" font-size="16" fill="white" text-anchor="middle">VC C</text>

  <!-- Arrows for navigation -->
  <line x1="200" y1="75" x2="240" y2="75" stroke="#F04B3E" stroke-width="3" marker-end="url(#arrowhead)"/>
  <text x="220" y="65" font-family="Arial" font-size="14" fill="#F04B3E" text-anchor="middle">presents/pushes</text>

  <line x1="400" y1="75" x2="440" y2="75" stroke="#F04B3E" stroke-width="3" marker-end="url(#arrowhead)"/>
  <text x="420" y="65" font-family="Arial" font-size="14" fill="#F04B3E" text-anchor="middle">presents/pushes</text>

  <!-- Problem description -->
  <text x="325" y="150" font-family="Arial" font-size="18" fill="#F04B3E" text-anchor="middle">Problem: View Controllers are tightly coupled and manage navigation.</text>
  <text x="325" y="175" font-family="Arial" font-size="16" fill="#F04B3E" text-anchor="middle">Hard to reuse, test, and maintain.</text>

  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#F04B3E" />
    </marker>
  </defs>
</svg>
</div>

## Why Coordinators? The Problem with Massive View Controllers

In a typical UIKit MVC application, `UIViewController` instances are often responsible for:
*   Displaying UI elements.
*   Handling user interactions.
*   Fetching and presenting data (sometimes via a ViewModel).
*   **Deciding *what* to present next and *how* to present it.**

It's this last point that causes the most trouble. When `ViewControllerA` directly instantiates and presents `ViewControllerB`, a tight coupling is formed. `ViewControllerA` now knows too much about `ViewControllerB`'s existence, its dependencies, and how to configure it.

Consider a user flow: `LoginViewController` -> `HomeViewController` -> `ProfileViewController`. If `LoginViewController` directly pushes `HomeViewController`, and `HomeViewController` directly pushes `ProfileViewController`, what happens if the `LoginViewController` needs to navigate to a different screen after a successful login in a different context (e.g., onboarding)? Or what if `ProfileViewController` can be reached from multiple places and needs different setup based on its origin?

This approach leads to:
1.  **Tight Coupling**: View controllers become highly dependent on each other, making changes ripple through the codebase.
2.  **Poor Reusability**: A `LoginViewController` that always navigates to `HomeViewController` is less reusable than one that simply signals "login successful" and lets something else handle the navigation.
3.  **Difficult Testing**: Testing navigation paths becomes cumbersome as you need to instantiate and mock entire view controller hierarchies.
4.  **Massive View Controllers**: All the navigation logic, often with conditional branching, accumulates within the view controller, making it bloated and hard to understand.

## What is the Coordinator Pattern?

The Coordinator pattern, sometimes referred to as Flow Controller, aims to solve these problems by delegating the responsibility of navigation to separate objects called "Coordinators."

A Coordinator is an object whose primary responsibility is to encapsulate navigation logic. Instead of a view controller knowing *where* to go next, it simply informs its coordinator *what happened*. The coordinator then decides *where* to go and *how* to get there.

Key responsibilities of a Coordinator include:
*   **Starting a flow**: A coordinator typically has a `start()` method that sets up the initial view controller(s) and presents them.
*   **Handling navigation**: When a view controller needs to navigate, it delegates this responsibility to its coordinator. The coordinator then pushes, presents, or dismisses other view controllers.
*   **Managing child coordinators**: Complex applications often have nested flows. A parent coordinator can start and manage child coordinators for specific sub-flows, like an authentication flow or an onboarding flow.
*   **Communicating flow completion**: When a child flow completes, its coordinator typically notifies its parent coordinator, which can then dismiss the child and continue the main flow.

## Core Components of the Coordinator Pattern

Let's break down the essential pieces you'll need to implement the Coordinator pattern.

### 1. The `Coordinator` Protocol

This protocol defines the basic interface for any coordinator. It ensures all coordinators can be started and can manage child coordinators.

```swift
import UIKit

protocol Coordinator: AnyObject {
    var navigationController: UINavigationController { get set }
    var childCoordinators: [Coordinator] { get set }

    func start()
    func finish() // Optional: To signal completion of a flow
}

extension Coordinator {
    func finish() {
        // Default implementation, can be overridden if specific cleanup is needed
        childCoordinators.removeAll()
    }
}
```

*   `navigationController`: The `UINavigationController` instance that this coordinator will use to push/pop view controllers. While not strictly required for *all* coordinators (some might use `present` directly on a root view controller), it's very common.
*   `childCoordinators`: An array to hold strong references to any child coordinators. This is crucial to prevent child coordinators from being deallocated prematurely.
*   `start()`: The entry point for the coordinator, typically where it sets up and presents its initial view controller.
*   `finish()`: An optional method to signal that the coordinator's flow is complete and perform any necessary cleanup.

### 2. The `AppCoordinator` (Root Coordinator)

Every application needs a starting point. The `AppCoordinator` is the main coordinator that lives for the lifetime of the application. It's responsible for setting up the initial window and deciding which main flow (e.g., authentication, main app content) to start.

```swift
class AppCoordinator: Coordinator {
    var navigationController: UINavigationController
    var childCoordinators = [Coordinator]()
    private let window: UIWindow

    init(window: UIWindow) {
        self.window = window
        self.navigationController = UINavigationController()
    }

    func start() {
        window.rootViewController = navigationController
        window.makeKeyAndVisible()
        
        // Decide which flow to start initially (e.g., based on login status)
        startAuthFlow()
    }
    
    private func startAuthFlow() {
        let authCoordinator = AuthCoordinator(navigationController: navigationController)
        authCoordinator.parentCoordinator = self // Set parent for delegation
        childCoordinators.append(authCoordinator)
        authCoordinator.start()
    }
    
    // ... other methods to handle flow completion from child coordinators
}
```

### 3. Child Coordinators

For specific, self-contained flows (like authentication, user profile, product detail), you create child coordinators. These coordinators manage their own set of view controllers and navigation within that specific flow.

### 4. Delegation for Flow Completion

View controllers need a way to tell their coordinator that an action has occurred that requires navigation. This is typically done through a delegate protocol. Child coordinators also need a way to tell their parent coordinator when their flow is complete.

```swift
// Example: LoginViewController's delegate protocol
protocol LoginCoordinatorDelegate: AnyObject {
    func loginCoordinatorDidFinishLogin(_ coordinator: AuthCoordinator)
}
```

## Implementing a Simple Flow with Coordinators

Let's walk through an example of an authentication flow: `LoginViewController` -> `HomeViewController`.

First, define our view controllers (simplified):

```swift
// LoginViewController.swift
import UIKit

protocol LoginViewControllerDelegate: AnyObject {
    func loginViewControllerDidTapLogin(_ viewController: LoginViewController)
}

class LoginViewController: UIViewController {
    weak var delegate: LoginViewControllerDelegate?

    private lazy var loginButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("Log In", for: .normal)
        button.addTarget(self, action: #selector(didTapLogin), for: .touchUpInside)
        button.translatesAutoresizingMaskIntoConstraints = false
        return button
    }()

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemBackground
        title = "Login"
        
        view.addSubview(loginButton)
        NSLayoutConstraint.activate([
            loginButton.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            loginButton.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }

    @objc private func didTapLogin() {
        delegate?.loginViewControllerDidTapLogin(self)
    }
}

// HomeViewController.swift
import UIKit

class HomeViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemGreen.withAlphaComponent(0.2)
        title = "Home"
    }
}
```

Now, let's create our `AuthCoordinator`.

```swift
// AuthCoordinator.swift
import UIKit

protocol AuthCoordinatorDelegate: AnyObject {
    func authCoordinatorDidFinish(_ coordinator: AuthCoordinator)
}

class AuthCoordinator: Coordinator {
    var navigationController: UINavigationController
    var childCoordinators = [Coordinator]()
    weak var parentCoordinator: AuthCoordinatorDelegate? // Delegate to parent

    init(navigationController: UINavigationController) {
        self.navigationController = navigationController
    }

    func start() {
        showLogin()
    }

    private func showLogin() {
        let loginVC = LoginViewController()
        loginVC.delegate = self // LoginVC delegates navigation events to AuthCoordinator
        navigationController.pushViewController(loginVC, animated: true)
    }
    
    private func showHome() {
        let homeVC = HomeViewController()
        // No delegate needed here if Home is the end of this flow before returning to parent
        navigationController.setViewControllers([homeVC], animated: true) // Replace navigation stack
        parentCoordinator?.authCoordinatorDidFinish(self) // Notify parent that auth flow is complete
    }
}

// Extend AuthCoordinator to conform to LoginViewControllerDelegate
extension AuthCoordinator: LoginViewControllerDelegate {
    func loginViewControllerDidTapLogin(_ viewController: LoginViewController) {
        // User tapped login, now AuthCoordinator decides what happens next
        print("Login successful, navigating to Home...")
        showHome()
    }
}
```

Finally, let's update our `AppCoordinator` and `SceneDelegate` (or `AppDelegate` for older projects) to kick things off.

```swift
// Updated AppCoordinator.swift
extension AppCoordinator: AuthCoordinatorDelegate {
    func authCoordinatorDidFinish(_ coordinator: AuthCoordinator) {
        // Remove the finished auth coordinator from children
        childCoordinators = childCoordinators.filter { $0 !== coordinator }
        print("Auth flow finished. Ready for main app content.")
        // Here you would typically start a new "MainAppCoordinator"
        // For this example, AuthCoordinator already transitioned to HomeVC.
    }
}

// SceneDelegate.swift (or AppDelegate for non-SceneDelegate apps)
class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    var window: UIWindow?
    var appCoordinator: AppCoordinator? // Keep a strong reference

    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options connectionOptions: UIScene.ConnectionOptions) {
        guard let windowScene = (scene as? UIWindowScene) else { return }
        window = UIWindow(windowScene: windowScene)
        
        appCoordinator = AppCoordinator(window: window!)
        appCoordinator?.start()
    }
    // ... other SceneDelegate methods
}
```

In this setup:
*   `LoginViewController` knows nothing about `HomeViewController` or how to get there. It simply reports `didTapLogin` to its `delegate`.
*   `AuthCoordinator` is the one that knows the flow: after login, present `HomeViewController`. It also tells `AppCoordinator` when its job is done.
*   `AppCoordinator` is aware of the `AuthCoordinator` but not the individual view controllers within it.

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────────┐
│  AppCoordinator │       │  AuthCoordinator│       │ LoginViewController │
└─────────────────┘       └─────────────────┘       └─────────────────────┘
         │                       ▲      │                     ▲
         │                       │      │                     │
         │ startAuthFlow()       │      │ delegate?.didTapLogin()
         ▼                       │      │                     │
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────────┐
│  AppCoordinator │◄──────│  AuthCoordinator│◄──────│ LoginViewController │
│                 │       │    (manages)    │       │   (notifies)        │
│  (manages)      │       │                 │       │                     │
└─────────────────┘       └─────────────────┘       └─────────────────────┘
         │                                   │
         │ authCoordinatorDidFinish()        │ showHome()
         ▼                                   ▼
┌─────────────────┐                       ┌─────────────────┐
│  AppCoordinator │                       │ HomeViewController │
│ (starts MainFlow)│                       │                 │
└─────────────────┘                       └─────────────────┘
```

## Benefits of the Coordinator Pattern

1.  **Decoupling**: View controllers become independent of specific navigation paths. They simply perform their UI tasks and report events, making them highly reusable.
2.  **Improved Testability**: Since navigation logic is centralized in coordinators, it's easier to write unit tests for flows without needing to instantiate and interact with `UIViewController` hierarchies.
3.  **Clearer Separation of Concerns**: View controllers focus solely on presenting UI and handling user input. Coordinators focus exclusively on navigation and flow management.
4.  **Modular Flows**: Complex flows can be broken down into smaller, manageable child coordinators.
5.  **Easier Onboarding/Deep Linking**: With navigation logic centralized, it becomes simpler to handle deep links or start specific flows from different entry points.

## Trade-offs and Considerations

While powerful, the Coordinator pattern isn't a silver bullet:

*   **Increased Boilerplate**: You'll have more files and protocols (for coordinators and delegates), which can feel like overhead for very simple applications.
*   **Learning Curve**: It requires a shift in mindset from traditional `UIViewController`-driven navigation.
*   **Complexity for Simple Apps**: For apps with only a few screens and linear navigation, the benefits might not outweigh the added complexity.
*   **Reference Cycles**: Careful management of `weak` references (e.g., `weak var parentCoordinator`) is essential to prevent retain cycles, especially when child coordinators hold strong references to parent coordinators.

The Coordinator pattern shines in medium to large-sized applications with non-trivial navigation requirements, multiple entry points, or flows that might change over time.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 700 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Coordinator Pattern Flow Diagram">
  <title>Coordinator Pattern Flow: Decoupled Navigation</title>

  <!-- Coordinator Boxes -->
  <rect x="50" y="30" width="150" height="50" fill="#2A8367" rx="5" ry="5" stroke="#1c5f4b" stroke-width="2"/>
  <text x="125" y="57" font-family="Arial" font-size="16" fill="white" text-anchor="middle">AppCoordinator</text>

  <rect x="250" y="30" width="150" height="50" fill="#2A8367" rx="5" ry="5" stroke="#1c5f4b" stroke-width="2"/>
  <text x="325" y="57" font-family="Arial" font-size="16" fill="white" text-anchor="middle">AuthCoordinator</text>

  <rect x="450" y="30" width="150" height="50" fill="#2A8367" rx="5" ry="5" stroke="#1c5f4b" stroke-width="2"/>
  <text x="525" y="57" font-family="Arial" font-size="16" fill="white" text-anchor="middle">MainCoordinator</text>

  <!-- View Controller Boxes -->
  <rect x="50" y="180" width="150" height="50" fill="#1565c0" rx="5" ry="5" stroke="#0d47a1" stroke-width="2"/>
  <text x="125" y="207" font-family="Arial" font-size="16" fill="white" text-anchor="middle">LoginVC</text>

  <rect x="250" y="180" width="150" height="50" fill="#1565c0" rx="5" ry="5" stroke="#0d47a1" stroke-width="2"/>
  <text x="325" y="207" font-family="Arial" font-size="16" fill="white" text-anchor="middle">RegisterVC</text>

  <rect x="450" y="180" width="150" height="50" fill="#1565c0" rx="5" ry="5" stroke="#0d47a1" stroke-width="2"/>
  <text x="525" y="207" font-family="Arial" font-size="16" fill="white" text-anchor="middle">HomeVC</text>

  <!-- Arrows from Coordinator to VC (presents/pushes) -->
  <line x1="325" y1="80" x2="125" y2="170" stroke="black" stroke-width="2" marker-end="url(#arrowheadBlack)"/>
  <text x="225" y="125" font-family="Arial" font-size="12" fill="black" text-anchor="middle">presents/pushes</text>

  <line x1="325" y1="80" x2="325" y2="170" stroke="black" stroke-width="2" marker-end="url(#arrowheadBlack)"/>
  <text x="325" y="125" font-family="Arial" font-size="12" fill="black" text-anchor="middle">presents/pushes</text>

  <line x1="525" y1="80" x2="525" y2="170" stroke="black" stroke-width="2" marker-end="url(#arrowheadBlack)"/>
  <text x="525" y="125" font-family="Arial" font-size="12" fill="black" text-anchor="middle">presents/pushes</text>


  <!-- Arrows from VC to Coordinator (delegates events) -->
  <line x1="125" y1="230" x2="325" y2="90" stroke="#F04B3E" stroke-width="2" marker-end="url(#arrowheadRed)"/>
  <text x="225" y="250" font-family="Arial" font-size="12" fill="#F04B3E" text-anchor="middle">delegates event</text>

  <line x1="325" y1="230" x2="325" y2="90" stroke="#F04B3E" stroke-width="2" marker-end="url(#arrowheadRed)"/>
  <text x="380" y="205" font-family="Arial" font-size="12" fill="#F04B3E" text-anchor="middle">delegates event</text>


  <!-- Arrows between Coordinators (child/parent) -->
  <line x1="125" y1="80" x2="325" y2="80" stroke="#2A8367" stroke-width="2" marker-end="url(#arrowheadGreen)"/>
  <text x="225" y="90" font-family="Arial" font-size="12" fill="#2A8367" text-anchor="middle">manages child</text>

  <line x1="325" y1="80" x2="125" y1="80" stroke="#2A8367" stroke-width="2" marker-end="url(#arrowheadGreen)"/>
  <text x="225" y="70" font-family="Arial" font-size="12" fill="#2A8367" text-anchor="middle">notifies parent</text>
  
  <line x1="125" y1="80" x2="525" y2="80" stroke="#2A8367" stroke-width="2" marker-end="url(#arrowheadGreen)"/>
  <text x="325" y="90" font-family="Arial" font-size="12" fill="#2A8367" text-anchor="middle">manages child</text>

  <!-- Labels for responsibilities -->
  <text x="350" y="270" font-family="Arial" font-size="16" fill="black" text-anchor="middle">Coordinators: Manage navigation logic (who, where, how)</text>
  <text x="350" y="290" font-family="Arial" font-size="16" fill="black" text-anchor="middle">View Controllers: Display UI, handle user input (what happened)</text>


  <!-- Arrowhead definitions -->
  <defs>
    <marker id="arrowheadBlack" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="black" />
    </marker>
    <marker id="arrowheadRed" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#F04B3E" />
    </marker>
    <marker id="arrowheadGreen" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#2A8367" />
    </marker>
  </defs>
</svg>
</div>

## Summary

The Coordinator pattern is a powerful architectural tool for UIKit developers looking to bring order to their app's navigation and flow logic. By extracting these responsibilities from `UIViewController`s into dedicated `Coordinator` objects, you achieve a cleaner, more modular, and more testable codebase. While it introduces some initial boilerplate, the long-term benefits in terms of maintainability and flexibility for complex applications are significant. Consider adopting the Coordinator pattern if your view controllers are becoming bloated with navigation logic or if you find yourself struggling with reusing view controllers across different user flows.

Happy Swifting!
