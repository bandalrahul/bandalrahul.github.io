---
title: Face ID and Touch ID Authentication in iOS
date: 2026-08-19 09:25
description: Learn how to integrate Face ID and Touch ID into your iOS apps using the LocalAuthentication framework for enhanced security and user experience.
tags: Security, iOS, Development
---

# Face ID and Touch ID Authentication in iOS

In today's mobile-first world, security and convenience go hand-in-hand. For iOS applications, Apple provides robust biometric authentication mechanisms: Face ID and Touch ID. These technologies allow users to quickly and securely verify their identity using their face or fingerprint, significantly enhancing the user experience while protecting sensitive data.

As intermediate iOS developers, understanding how to properly integrate these features is crucial for building secure and user-friendly applications. This article will guide you through the `LocalAuthentication` framework, covering how to check for biometric availability, perform authentication, and handle various scenarios and errors gracefully.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="High-level LocalAuthentication Flow">
  <title>High-level LocalAuthentication Flow</title>
  <!-- App Box -->
  <rect x="50" y="80" width="100" height="60" rx="8" fill="#1565c0" stroke="#0C4A93" stroke-width="2"/>
  <text x="100" y="115" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">Your App</text>

  <!-- Arrow to LAContext -->
  <line x1="150" y1="110" x2="200" y2="110" stroke="black" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="175" y="100" font-family="Arial, sans-serif" font-size="12" fill="black" text-anchor="middle">Request</text>

  <!-- LAContext Box -->
  <rect x="200" y="80" width="120" height="60" rx="8" fill="#2A8367" stroke="#1C5E4A" stroke-width="2"/>
  <text x="260" y="105" font-family="Arial, sans-serif" font-size="14" fill="white" text-anchor="middle">LAContext</text>
  <text x="260" y="125" font-family="Arial, sans-serif" font-size="12" fill="white" text-anchor="middle">evaluatePolicy</text>

  <!-- Arrow to System Prompt -->
  <line x1="320" y1="110" x2="370" y2="110" stroke="black" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="345" y="100" font-family="Arial, sans-serif" font-size="12" fill="black" text-anchor="middle">System UI</text>

  <!-- Biometric Prompt Box -->
  <rect x="370" y="80" width="120" height="60" rx="8" fill="#F04B3E" stroke="#B83930" stroke-width="2"/>
  <text x="430" y="105" font-family="Arial, sans-serif" font-size="14" fill="white" text-anchor="middle">Biometric /</text>
  <text x="430" y="125" font-family="Arial, sans-serif" font-size="14" fill="white" text-anchor="middle">Passcode Prompt</text>

  <!-- Arrow back to App (Success) -->
  <line x1="430" y1="140" x2="430" y2="180" stroke="black" stroke-width="2" marker-end="url(#arrowhead)"/>
  <line x1="430" y1="180" x2="100" y2="180" stroke="black" stroke-width="2"/>
  <line x1="100" y1="180" x2="100" y2="140" stroke="black" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="300" y="195" font-family="Arial, sans-serif" font-size="12" fill="#2A8367" text-anchor="middle">Success</text>

  <!-- Arrow back to App (Failure) -->
  <line x1="490" y1="110" x2="540" y2="110" stroke="black" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="515" y="100" font-family="Arial, sans-serif" font-size="12" fill="#F04B3E" text-anchor="middle">Failure</text>
  <text x="540" y="125" font-family="Arial, sans-serif" font-size="12" fill="#F04B3E" text-anchor="start">Handle Error</text>

  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="black" />
    </marker>
  </defs>
</svg>
</div>

## The `LocalAuthentication` Framework

All biometric authentication in iOS is handled by the `LocalAuthentication` framework. Its core class is `LAContext`, which manages the authentication process. You'll primarily interact with two methods:

1.  `canEvaluatePolicy(_:error:)`: Checks if the device supports the specified authentication policy and if the necessary biometrics (or passcode) are enrolled.
2.  `evaluatePolicy(_:localizedReason:reply:)`: Initiates the authentication process, presenting the user with the Face ID, Touch ID, or passcode prompt.

### Understanding Authentication Policies

The `LocalAuthentication` framework defines several policies that dictate how authentication should occur:

-   `LAPolicy.deviceOwnerAuthenticationWithBiometrics`: This policy attempts to authenticate using biometrics (Face ID or Touch ID). If biometrics are not enrolled or available, it will fail. It does *not* offer a passcode fallback automatically.
-   `LAPolicy.deviceOwnerAuthentication`: This is generally the preferred policy. It attempts to authenticate using biometrics first. If biometrics are not available, not enrolled, or fail, it *automatically offers a system passcode fallback*. This provides a better user experience as it gives users an alternative if their biometrics aren't working or they prefer to use their passcode.

Unless you have a very specific reason to restrict authentication solely to biometrics, `deviceOwnerAuthentication` is usually the way to go.

## Checking for Biometric Availability

Before attempting to authenticate, it's crucial to check if the device supports the desired authentication method and if the user has it set up. This prevents presenting an authentication prompt that's guaranteed to fail and allows you to provide a better fallback experience.

```swift
import LocalAuthentication

class BiometricAuthenticator {

    let context = LAContext()

    func canAuthenticate() -> Bool {
        var error: NSError?
        // Check if the device owner can authenticate using biometrics or passcode
        let canEvaluate = context.canEvaluatePolicy(.deviceOwnerAuthentication, error: &error)

        if let error = error {
            print("Biometric/Passcode availability error: \(error.localizedDescription)")
            switch error.code {
            case LAError.Code.biometryNotAvailable.rawValue:
                print("Biometry is not available on this device.")
            case LAError.Code.biometryNotEnrolled.rawValue:
                print("Biometry is available but no faces/fingers are enrolled.")
            case LAError.Code.passcodeNotSet.rawValue:
                print("A passcode is not set on the device.")
            case LAError.Code.biometryLockout.rawValue:
                print("Biometry is locked out due to too many failed attempts.")
            default:
                print("Other LAError: \(error.localizedDescription)")
            }
            return false
        }

        // If no error, it means the policy can be evaluated.
        // We can also check biometryType for more specific info.
        if canEvaluate {
            switch context.biometryType {
            case .faceID:
                print("Device supports Face ID.")
            case .touchID:
                print("Device supports Touch ID.")
            case .none:
                print("Device supports passcode only.")
            @unknown default:
                print("Unknown biometry type.")
            }
        }
        
        return canEvaluate
    }
}
```

In the `canAuthenticate()` method, we pass `nil` for the error parameter initially and then check if an `NSError` was populated. The `LAError` enumeration provides specific error codes that help you understand why authentication might not be possible.

### `biometryType` Property

The `LAContext.biometryType` property, available from iOS 11.0, allows you to determine the specific biometric type available on the device (`.faceID`, `.touchID`, or `.none`). This is useful for customizing your UI, for example, by showing a "Use Face ID" or "Use Touch ID" button.

## Performing Authentication

Once you've confirmed that authentication is possible, you can initiate the process using `evaluatePolicy(_:localizedReason:reply:)`. This method takes a `localizedReason` string, which is crucial for good user experience. This string is displayed to the user in the biometric prompt, explaining *why* your app needs authentication.

```swift
extension BiometricAuthenticator {

    func authenticate(localizedReason: String, completion: @escaping (Result<Bool, LAError>) -> Void) {
        // Ensure authentication is possible before proceeding
        guard canAuthenticate() else {
            // Handle cases where authentication is not possible (e.g., no biometrics, no passcode)
            // For simplicity, we'll just return a generic error here.
            // In a real app, you might want to provide a more specific error based on canAuthenticate() checks.
            completion(.failure(LAError(.biometryNotAvailable)))
            return
        }

        context.evaluatePolicy(.deviceOwnerAuthentication, localizedReason: localizedReason) { success, error in
            DispatchQueue.main.async {
                if success {
                    completion(.success(true))
                } else {
                    if let error = error as? LAError {
                        completion(.failure(error))
                    } else {
                        // Handle unexpected error types
                        completion(.failure(LAError(.appCancel))) // Or a more appropriate generic error
                    }
                }
            }
        }
    }
}
```

It's important to note that the `reply` closure is executed on a background thread. Any UI updates should be dispatched back to the main thread.

## Handling Authentication Errors Gracefully

Authentication can fail for various reasons, from user cancellation to biometric lockout. Providing clear feedback and alternative options to the user is key. Here's a breakdown of common `LAError` codes and how to handle them:

```
┌──────────────────┐
│   LAError        │
│   (error.code)   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  switch error.code │
└────────┬─────────┘
         │
         ├─── LAError.userCancel ───────► User tapped 'Cancel'
         │                                (Dismiss prompt, do nothing)
         │
         ├─── LAError.userFallback ─────► User tapped 'Enter Passcode'
         │                                (Offer custom passcode UI or alternative)
         │
         ├─── LAError.systemCancel ─────► System cancelled (e.g., app moved to background)
         │                                (Dismiss prompt, retry if appropriate)
         │
         ├─── LAError.biometryLockout ──► Too many failed attempts
         │                                (Prompt for device passcode or wait)
         │
         ├─── LAError.biometryNotEnrolled ► No biometrics set up
         │                                (Guide user to Settings)
         │
         ├─── LAError.passcodeNotSet ───► Device passcode not set
         │                                (Guide user to Settings)
         │
         ├─── LAError.biometryNotAvailable ► Device lacks biometry hardware
         │                                (Hide biometry option, use alternative)
         │
         └─── default ───────────────────► Other unexpected errors
                                         (Log error, show generic message)
```

Here's an example of how you might handle these errors within your `completion` block:

```swift
func handleAuthenticationResult(result: Result<Bool, LAError>) {
    switch result {
    case .success(true):
        print("Authentication successful!")
        // Proceed with sensitive operation
    case .failure(let error):
        print("Authentication failed: \(error.localizedDescription)")
        switch error.code {
        case .userCancel:
            print("User cancelled the authentication.")
            // Do nothing, or simply dismiss the UI
        case .userFallback:
            print("User chose to enter passcode.")
            // You might present your own passcode entry UI here,
            // or let the system handle the passcode fallback if using .deviceOwnerAuthentication
        case .systemCancel:
            print("System cancelled the authentication (e.g., app went to background).")
            // Can retry authentication if appropriate when app returns to foreground
        case .biometryLockout:
            print("Biometry is locked out. User must enter device passcode or wait.")
            // Inform user and potentially offer a device passcode prompt (if .deviceOwnerAuthentication wasn't used)
        case .biometryNotEnrolled, .passcodeNotSet:
            print("Biometry/Passcode not set up. Please go to Settings.")
            // Guide user to iOS Settings
        case .biometryNotAvailable:
            print("Biometry not available on this device.")
            // Fallback to username/password or other method
        case .appCancel:
            print("Authentication cancelled by app.")
        case .invalidContext:
            print("LAContext invalid (e.g., used after invalidate()).")
        @unknown default:
            print("An unknown LAError occurred: \(error.localizedDescription)")
        }
        // Present an alert to the user or take other recovery steps
    }
}
```

## Best Practices and User Experience

1.  **Clear `localizedReason`**: Always provide a descriptive and user-friendly `localizedReason` string. It should clearly explain *why* your app needs to authenticate the user. E.g., "Unlock app access," "Confirm purchase," "Access protected data."
2.  **Use `deviceOwnerAuthentication`**: As discussed, this policy generally provides the best user experience by offering a system passcode fallback if biometrics are unavailable or fail.
3.  **Don't rely solely on biometrics**: Biometrics are for convenience and local device security. For highly sensitive operations (e.g., transferring money), consider requiring additional authentication steps like a server-verified password.
4.  **Provide alternatives**: If biometrics are not available or fail persistently, ensure your app offers a secure fallback mechanism, such as a username/password login or a custom passcode screen.
5.  **Respect user privacy**: Never collect or store biometric data. `LocalAuthentication` only tells you if the *device owner* has authenticated; it doesn't provide any biometric information to your app.
6.  **Handle `LAContext` lifecycle**: Create a new `LAContext` instance for each authentication attempt or ensure your existing context is valid. Reusing a context that has become invalid can lead to `LAError.invalidContext`.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Detailed Biometric Authentication Flowchart">
  <title>Detailed Biometric Authentication Flowchart</title>
  <!-- Start -->
  <circle cx="50" cy="50" r="20" fill="#1565c0"/>
  <text x="50" y="55" font-family="Arial, sans-serif" font-size="12" fill="white" text-anchor="middle">Start</text>

  <!-- Check Availability -->
  <rect x="100" y="30" width="120" height="40" rx="5" fill="#2A8367"/>
  <text x="160" y="55" font-family="Arial, sans-serif" font-size="12" fill="white" text-anchor="middle">Can Authenticate?</text>

  <!-- Diamond for Can Authenticate -->
  <polygon points="250,50 270,70 250,90 230,70" fill="#F04B3E" stroke="#B83930" stroke-width="1"/>
  <text x="250" y="70" font-family="Arial, sans-serif" font-size="12" fill="white" text-anchor="middle">Yes?</text>

  <!-- No Path from Can Authenticate -->
  <line x1="270" y1="70" x2="330" y2="70" stroke="black" stroke-width="1" marker-end="url(#arrowhead-black)"/>
  <text x="300" y="60" font-family="Arial, sans-serif" font-size="10" fill="black" text-anchor="middle">No</text>
  <rect x="330" y="50" width="100" height="40" rx="5" fill="#F04B3E"/>
  <text x="380" y="75" font-family="Arial, sans-serif" font-size="10" fill="white" text-anchor="middle">Show Error / Fallback</text>
  <line x1="380" y1="90" x2="380" y2="190" stroke="black" stroke-width="1" marker-end="url(#arrowhead-black)"/>
  <text x="380" y="175" font-family="Arial, sans-serif" font-size="10" fill="black" text-anchor="middle">End</text>

  <!-- Yes Path from Can Authenticate -->
  <line x1="250" y1="90" x2="250" y2="120" stroke="black" stroke-width="1" marker-end="url(#arrowhead-black)"/>
  <text x="260" y="105" font-family="Arial, sans-serif" font-size="10" fill="black" text-anchor="start">Yes</text>

  <!-- Evaluate Policy -->
  <rect x="190" y="120" width="120" height="40" rx="5" fill="#2A8367"/>
  <text x="250" y="145" font-family="Arial, sans-serif" font-size="12" fill="white" text-anchor="middle">Evaluate Policy</text>

  <!-- Diamond for Success -->
  <polygon points="250,160 270,180 250,200 230,180" fill="#1565c0" stroke="#0C4A93" stroke-width="1"/>
  <text x="250" y="180" font-family="Arial, sans-serif" font-size="12" fill="white" text-anchor="middle">Success?</text>

  <!-- Success Path -->
  <line x1="250" y1="200" x2="250" y2="210" stroke="black" stroke-width="1" marker-end="url(#arrowhead-black)"/>
  <rect x="190" y="210" width="120" height="40" rx="5" fill="#2A8367"/>
  <text x="250" y="235" font-family="Arial, sans-serif" font-size="12" fill="white" text-anchor="middle">Access Data</text>
  <line x1="250" y1="250" x2="250" y2="260" stroke="black" stroke-width="1" marker-end="url(#arrowhead-black)"/>
  <text x="250" y="275" font-family="Arial, sans-serif" font-size="12" fill="black" text-anchor="middle">End</text>

  <!-- Failure Path -->
  <line x1="270" y1="180" x2="330" y2="180" stroke="black" stroke-width="1" marker-end="url(#arrowhead-black)"/>
  <text x="300" y="170" font-family="Arial, sans-serif" font-size="10" fill="black" text-anchor="middle">No</text>
  <rect x="330" y="160" width="100" height="40" rx="5" fill="#F04B3E"/>
  <text x="380" y="185" font-family="Arial, sans-serif" font-size="10" fill="white" text-anchor="middle">Handle LAError</text>
  <line x1="380" y1="200" x2="380" y2="210" stroke="black" stroke-width="1" marker-end="url(#arrowhead-black)"/>
  <text x="380" y="225" font-family="Arial, sans-serif" font-size="10" fill="black" text-anchor="middle">End</text>

  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowhead-black" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="black" />
    </marker>
  </defs>
</svg>
</div>

## Complete Example: Integrating into a SwiftUI View

Here's how you might integrate our `BiometricAuthenticator` into a SwiftUI view. Remember to add `NSFaceIDUsageDescription` to your `Info.plist` file, explaining why your app needs Face ID. If you only use Touch ID, this is not strictly necessary, but it's good practice to provide a clear reason for any biometric access.

```xml
<key>NSFaceIDUsageDescription</key>
<string>Your face will be used to unlock access to your secure data.</string>
```

```swift
import SwiftUI
import LocalAuthentication // Make sure to import this!

struct ContentView: View {
    @State private var isAuthenticated = false
    @State private var authenticationError: LAError?
    @State private var showingAlert = false
    @State private var alertMessage = ""

    private let authenticator = BiometricAuthenticator()

    var body: some View {
        VStack {
            if isAuthenticated {
                Text("Welcome, authenticated user!")
                    .font(.title)
                    .padding()
                Button("Logout (Reset State)") {
                    isAuthenticated = false
                }
            } else {
                Text("Please authenticate to proceed.")
                    .font(.title2)
                    .padding()

                Button("Authenticate with Biometrics") {
                    authenticateUser()
                }
                .padding()
                .background(Color.blue)
                .foregroundColor(.white)
                .cornerRadius(10)
            }
        }
        .alert("Authentication Failed", isPresented: $showingAlert) {
            Button("OK") { }
        } message: {
            Text(alertMessage)
        }
    }

    private func authenticateUser() {
        guard authenticator.canAuthenticate() else {
            alertMessage = "Biometric or passcode authentication is not available or set up on this device."
            showingAlert = true
            return
        }

        let reason = "To access your secure content."

        authenticator.authenticate(localizedReason: reason) { result in
            switch result {
            case .success(true):
                self.isAuthenticated = true
                self.authenticationError = nil
            case .failure(let error):
                self.isAuthenticated = false
                self.authenticationError = error
                self.alertMessage = self.errorMessage(for: error)
                self.showingAlert = true
            }
        }
    }

    private func errorMessage(for error: LAError) -> String {
        switch error.code {
        case .userCancel:
            return "Authentication cancelled by user."
        case .userFallback:
            return "User chose to enter passcode. Please use device passcode."
        case .systemCancel:
            return "Authentication cancelled by system."
        case .biometryLockout:
            return "Too many failed attempts. Biometrics locked out. Please use device passcode or try again later."
        case .biometryNotEnrolled:
            return "Biometrics not set up. Please enable Face ID or Touch ID in device settings."
        case .passcodeNotSet:
            return "Device passcode not set. Please set a passcode in device settings."
        case .biometryNotAvailable:
            return "Biometrics not available on this device."
        case .appCancel:
            return "Authentication cancelled by the application."
        case .invalidContext:
            return "The authentication context is invalid."
        @unknown default:
            return "An unknown authentication error occurred."
        }
    }
}
```

This `ContentView` provides a basic example of how to trigger authentication and handle its outcomes, displaying different UI states based on authentication success or failure.

## Summary

Integrating Face ID and Touch ID into your iOS applications significantly boosts both security and user convenience. By leveraging the `LocalAuthentication` framework, you can check for biometric availability, initiate authentication, and handle various success and error scenarios. Always prioritize clear communication with the user through the `localizedReason` and provide graceful fallbacks for when biometrics are not available or fail. Remember to add the `NSFaceIDUsageDescription` to your `Info.plist` if your app uses Face ID.

Happy Swifting!
