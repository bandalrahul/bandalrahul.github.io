---
title: Custom View Controller Transitions in UIKit
date: 2026-07-22 11:00
description: Learn how to create stunning custom view controller transitions in UIKit using UIViewControllerTransitioningDelegate and UIViewControllerAnimatedTransitioning.
tags: UIKit, iOS, Development
---

# Custom View Controller Transitions in UIKit

UIKit provides a robust set of default transitions for presenting and dismissing view controllers, like the familiar slide-up modal or the push/pop navigation animations. While these work well for most standard interactions, sometimes you need to go beyond the defaults to create a truly unique and engaging user experience. This is where custom view controller transitions come in.

Custom transitions allow you to define precisely how one view controller animates on or off the screen, offering endless possibilities for creative UI. Whether you want a dramatic zoom, a subtle fade, or a bespoke card-stacking effect, UIKit's powerful transition APIs give you the control you need.

In this article, we'll dive deep into the core protocols and steps required to build your own custom view controller transitions. We'll walk through a practical example of creating a "zoom-in" presentation and "zoom-out" dismissal animation.

## The Core Protocols of Custom Transitions

At the heart of UIKit's custom transition system are three key players:

1.  **`UIViewControllerTransitioningDelegate`**: This protocol acts as the coordinator for your custom transition. When a view controller is presented with `modalPresentationStyle = .custom` and its `transitioningDelegate` property is set, UIKit will ask this delegate for the appropriate animator objects for both presentation and dismissal.

2.  **`UIViewControllerAnimatedTransitioning`**: This is where the actual animation logic lives. An object conforming to this protocol is responsible for defining the duration of the transition and, most importantly, performing the visual animations that move views from their "before" state to their "after" state. You'll implement the `animateTransition(using:)` method here.

3.  **`UIViewControllerContextTransitioning`**: This protocol provides the animator with all the necessary information about the transition. It gives you access to the container view where all animations should take place, the "from" view controller and view, the "to" view controller and view, and other crucial details. Think of it as the animation's canvas and toolbox.

Here's a simplified flow of how these components interact:

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Flow of custom view controller transition initiation">
  <title>Custom Transition Initiation Flow</title>

  <!-- Presenting VC -->
  <rect x="50" y="20" width="150" height="60" rx="10" ry="10" fill="#1565c0" stroke="#0e4b8f" stroke-width="2"/>
  <text x="125" y="55" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">Presenting VC</text>

  <!-- calls present() -->
  <path d="M200 50 L250 50" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="225" y="40" font-family="Arial, sans-serif" font-size="12" fill="#333" text-anchor="middle">present()</text>

  <!-- Transitioning Delegate -->
  <rect x="250" y="20" width="180" height="60" rx="10" ry="10" fill="#2A8367" stroke="#1c5a47" stroke-width="2"/>
  <text x="340" y="55" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">Transitioning Delegate</text>

  <!-- returns Animator -->
  <path d="M340 80 L340 120" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="340" y="100" font-family="Arial, sans-serif" font-size="12" fill="#333" text-anchor="middle">returns animator</text>

  <!-- Custom Animator -->
  <rect x="250" y="120" width="180" height="60" rx="10" ry="10" fill="#F04B3E" stroke="#b3382f" stroke-width="2"/>
  <text x="340" y="155" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">Custom Animator</text>

  <!-- performs animation -->
  <path d="M340 180 L340 200 L500 200 L500 150" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="420" y="190" font-family="Arial, sans-serif" font-size="12" fill="#333" text-anchor="middle">performs animation</text>

  <!-- Presented VC -->
  <rect x="450" y="120" width="100" height="60" rx="10" ry="10" fill="#1565c0" stroke="#0e4b8f" stroke-width="2"/>
  <text x="500" y="155" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">Presented VC</text>

  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
    </marker>
  </defs>
</svg>
</div>

## Step-by-Step: Building a Zoom Transition

Let's create a custom transition where a presented view controller zooms in from a small point and fades in, and then zooms out and fades out upon dismissal.

### 1. The Custom Transitioning Delegate

First, we need a class that conforms to `UIViewControllerTransitioningDelegate`. This class will be responsible for providing the animator objects. It's crucial to keep a strong reference to this delegate instance, as UIKit does not retain it automatically. A common pattern is to make it a property of the presenting view controller.

```swift
class ZoomTransitioningDelegate: NSObject, UIViewControllerTransitioningDelegate {
    func animationController(forPresented presented: UIViewController, presenting: UIViewController, source: UIViewController) -> UIViewControllerAnimatedTransitioning? {
        return ZoomAnimator(isPresenting: true)
    }

    func animationController(forDismissed dismissed: UIViewController) -> UIViewControllerAnimatedTransitioning? {
        return ZoomAnimator(isPresenting: false)
    }
}
```

As you can see, this delegate has two methods: one for presentation and one for dismissal. Both return an instance of our `ZoomAnimator` (which we'll define next), initialized with a flag to indicate whether it's handling a presentation or a dismissal.

### 2. The Custom Animator Object

This is where the actual animation code resides. Our `ZoomAnimator` class will conform to `UIViewControllerAnimatedTransitioning`.

```swift
class ZoomAnimator: NSObject, UIViewControllerAnimatedTransitioning {
    let isPresenting: Bool

    init(isPresenting: Bool) {
        self.isPresenting = isPresenting
        super.init()
    }

    // MARK: - UIViewControllerAnimatedTransitioning

    func transitionDuration(using transitionContext: UIViewControllerContextTransitioning?) -> TimeInterval {
        // Define the duration of the animation
        return 0.6
    }

    func animateTransition(using transitionContext: UIViewControllerContextTransitioning) {
        // Get the container view where all transition animations happen
        let containerView = transitionContext.containerView

        // Get the 'from' and 'to' views
        guard let fromView = transitionContext.view(forKey: .from) else {
            transitionContext.completeTransition(false)
            return
        }
        
        let toView = transitionContext.view(forKey: .to)! // The 'to' view is always available for presentation

        if isPresenting {
            // For presentation:
            // 1. Add the 'to' view to the container view
            containerView.addSubview(toView)

            // 2. Set the 'to' view's initial state (small and transparent)
            toView.transform = CGAffineTransform(scaleX: 0.1, y: 0.1)
            toView.alpha = 0.0

            // 3. Animate to its final state (full size and opaque)
            UIView.animate(withDuration: transitionDuration(using: transitionContext), delay: 0, usingSpringWithDamping: 0.7, initialSpringVelocity: 0.5, options: .curveEaseInOut) {
                toView.transform = .identity // Default, full-size state
                toView.alpha = 1.0
            } completion: { finished in
                // 4. Crucially, inform the context that the transition is complete
                transitionContext.completeTransition(finished)
            }
        } else {
            // For dismissal:
            // 1. Animate the 'from' view (the one being dismissed) to its final state (small and transparent)
            UIView.animate(withDuration: transitionDuration(using: transitionContext), animations: {
                fromView.transform = CGAffineTransform(scaleX: 0.1, y: 0.1)
                fromView.alpha = 0.0
            }) { finished in
                // 2. Remove the 'from' view from the superview
                fromView.removeFromSuperview()
                // 3. Inform the context that the transition is complete
                transitionContext.completeTransition(finished)
            }
        }
    }
}
```

Let's break down `animateTransition(using:)`:

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="UIViewControllerContextTransitioning components">
  <title>UIViewControllerContextTransitioning Components</title>

  <!-- Container View -->
  <rect x="50" y="20" width="500" height="180" rx="10" ry="10" fill="#EEEEEE" stroke="#333" stroke-width="2"/>
  <text x="300" y="45" font-family="Arial, sans-serif" font-size="16" fill="#333" text-anchor="middle">containerView (UIViewControllerContextTransitioning)</text>

  <!-- fromView -->
  <rect x="70" y="70" width="200" height="100" rx="8" ry="8" fill="#F04B3E" opacity="0.7" stroke="#b3382f" stroke-width="1"/>
  <text x="170" y="125" font-family="Arial, sans-serif" font-size="14" fill="white" text-anchor="middle">fromView</text>
  <text x="170" y="145" font-family="Arial, sans-serif" font-size="12" fill="white" text-anchor="middle">(fromVC.view)</text>

  <!-- toView -->
  <rect x="330" y="70" width="200" height="100" rx="8" ry="8" fill="#2A8367" opacity="0.7" stroke="#1c5a47" stroke-width="1"/>
  <text x="430" y="125" font-family="Arial, sans-serif" font-size="14" fill="white" text-anchor="middle">toView</text>
  <text x="430" y="145" font-family="Arial, sans-serif" font-size="12" fill="white" text-anchor="middle">(toVC.view)</text>

  <!-- Label for animation -->
  <text x="300" y="190" font-family="Arial, sans-serif" font-size="14" fill="#333" text-anchor="middle">Animator manipulates fromView and toView within containerView</text>
</svg>
</div>

*   **`containerView`**: This is the temporary view that houses all the views participating in the transition. Your animations should always occur within this view.
*   **`fromView` and `toView`**: These are the views of the `from` and `to` view controllers. For presentation, `toView` is the view of the view controller being presented. For dismissal, `fromView` is the view of the view controller being dismissed.
*   **Adding `toView`**: During presentation, it's *your* responsibility to add `toView` to the `containerView`. UIKit does not do this automatically for custom transitions. For dismissal, `fromView` is already in the `containerView`.
*   **Animation**: Use `UIView.animate` to perform your desired visual effects. You manipulate properties like `transform`, `alpha`, `frame`, etc.
*   **`completeTransition(finished)`**: This is the **most critical step**. You *must* call `transitionContext.completeTransition(true)` when your animations are finished. If you forget this, UIKit will be left in an inconsistent state, and your app might become unresponsive or behave unexpectedly. Pass `false` if the transition was cancelled (e.g., in an interactive transition).
*   **Removing `fromView`**: For dismissal, after the animation, it's good practice to remove the `fromView` from its superview using `removeFromSuperview()`.

### 3. Presenting the View Controller with Custom Transition

Now, let's wire everything up in our view controllers. We'll need a `PresentingViewController` and a `PresentedViewController`.

```swift
// MARK: - PresentedViewController

class PresentedViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemRed.withAlphaComponent(0.8)
        view.layer.cornerRadius = 15
        view.clipsToBounds = true

        let dismissButton = UIButton(type: .system)
        dismissButton.setTitle("Dismiss", for: .normal)
        dismissButton.setTitleColor(.white, for: .normal)
        dismissButton.backgroundColor = .systemRed
        dismissButton.layer.cornerRadius = 8
        dismissButton.addTarget(self, action: #selector(dismissVC), for: .touchUpInside)
        dismissButton.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(dismissButton)

        NSLayoutConstraint.activate([
            dismissButton.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            dismissButton.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -20),
            dismissButton.widthAnchor.constraint(equalToConstant: 120),
            dismissButton.heightAnchor.constraint(equalToConstant: 44)
        ])
    }

    @objc func dismissVC() {
        dismiss(animated: true, completion: nil)
    }
}

// MARK: - PresentingViewController

class PresentingViewController: UIViewController {
    // IMPORTANT: Keep a strong reference to your transitioning delegate!
    // UIKit does not retain it, so if it's a local variable, it will be deallocated.
    let customTransitionDelegate = ZoomTransitioningDelegate()

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemBlue

        let presentButton = UIButton(type: .system)
        presentButton.setTitle("Present Custom VC", for: .normal)
        presentButton.setTitleColor(.white, for: .normal)
        presentButton.backgroundColor = .systemGreen
        presentButton.layer.cornerRadius = 8
        presentButton.addTarget(self, action: #selector(presentCustomVC), for: .touchUpInside)
        presentButton.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(presentButton)

        NSLayoutConstraint.activate([
            presentButton.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            presentButton.centerYAnchor.constraint(equalTo: view.centerYAnchor),
            presentButton.widthAnchor.constraint(equalToConstant: 200),
            presentButton.heightAnchor.constraint(equalToConstant: 50)
        ])
    }

    @objc func presentCustomVC() {
        let presentedVC = PresentedViewController()
        
        // 1. Set the modal presentation style to .custom
        presentedVC.modalPresentationStyle = .custom
        
        // 2. Assign our custom transitioning delegate
        presentedVC.transitioningDelegate = customTransitionDelegate
        
        // 3. Present the view controller
        present(presentedVC, animated: true, completion: nil)
    }
}
```

In the `PresentingViewController`, notice these crucial lines:

*   `let customTransitionDelegate = ZoomTransitioningDelegate()`: We instantiate our delegate and keep a strong reference.
*   `presentedVC.modalPresentationStyle = .custom`: This tells UIKit that we want to provide a custom presentation style, which then triggers the `transitioningDelegate` methods.
*   `presentedVC.transitioningDelegate = customTransitionDelegate`: We assign our custom delegate to the view controller being presented.

When `present(presentedVC, animated: true, completion: nil)` is called, UIKit will consult `customTransitionDelegate` to get the `ZoomAnimator`, and then the `ZoomAnimator` takes over to perform the animation.

## Beyond Basic Animations: Interactive Transitions

While this article focuses on non-interactive custom transitions, it's worth noting that you can also create *interactive* transitions. This means the user can control the progress of the transition, for example, by dragging their finger across the screen to dismiss a view controller.

This involves implementing a `UIPercentDrivenInteractiveTransition` object, which works in conjunction with your `UIViewControllerAnimatedTransitioning` to update the animation's progress based on user gestures. The `UIViewControllerTransitioningDelegate` would then also implement `interactionControllerForPresentation(using:)` and `interactionControllerForDismissal(using:)` to return your interactive transition object.

```
┌──────────────────────────┐     ┌───────────────────────────────────┐
│                          │     │                                   │
│  Presenting Controller   │────►│  `modalPresentationStyle = .custom`   │
│                          │     │                                   │
└──────────────────────────┘     └───────────────────────────────────┘
             │                                   │
             │  `transitioningDelegate`          │
             V                                   V
┌───────────────────────────────────┐     ┌───────────────────────────────────┐
│                                   │     │                                   │
│  `UIViewControllerTransitioningDelegate`  │────►│  `UIViewControllerAnimatedTransitioning`  │
│                                   │     │                                   │
└───────────────────────────────────┘     └───────────────────────────────────┘
             │                                   │         │
             │  Returns animator                 │         │  Performs Animations
             V                                   V         V
┌───────────────────────────────────┐     ┌───────────────────────────────────┐
│                                   │     │                                   │
│  `animationController(forPresented:)`   │────►│  `animateTransition(using:)`    │
│                                   │     │                                   │
└───────────────────────────────────┘     └───────────────────────────────────┘
                                                       │
                                                       │  Manipulates views in `containerView`
                                                       V
                                          ┌───────────────────────────────┐
                                          │                               │
                                          │ `transitionContext.completeTransition(true)` │
                                          │                               │
                                          └───────────────────────────────┘
```

This diagram illustrates the lifecycle from initiating a custom presentation to completing the animation.

## Summary

Custom view controller transitions in UIKit are a powerful tool for crafting unique and engaging user interfaces. By understanding and implementing the `UIViewControllerTransitioningDelegate` and `UIViewControllerAnimatedTransitioning` protocols, you gain granular control over the presentation and dismissal animations of your view controllers. Remember these key takeaways:

*   Set `modalPresentationStyle = .custom` on the view controller being presented.
*   Assign a strong reference to your `UIViewControllerTransitioningDelegate` instance.
*   In your `UIViewControllerAnimatedTransitioning` object, add the `toView` to the `containerView` for presentations.
*   Always call `transitionContext.completeTransition(true)` when your animations are done.

With these techniques, you're well-equipped to elevate your app's user experience beyond standard UIKit animations.

Happy Swifting!
