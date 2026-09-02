---
title: StoreKit 2 and In-App Purchases on iOS
date: 2026-09-02 13:07
description: Master StoreKit 2 for iOS in-app purchases. Learn product fetching, transaction processing, and subscription management with practical Swift code examples.
tags: StoreKit, iOS, Development
---

# StoreKit 2 and In-App Purchases on iOS

StoreKit 2, introduced at WWDC 2021, revolutionized how developers integrate in-app purchases (IAPs) into their iOS apps. Building upon the foundation of the original StoreKit framework, StoreKit 2 offers a modern, async/await-based API that simplifies many complex aspects of IAP implementation, from fetching product information to processing transactions and handling subscription statuses. It brings improved reliability, better error handling, and a more streamlined development experience, leveraging Swift's concurrency features.

If you've struggled with the delegate-based patterns and manual receipt validation of StoreKit 1, you'll find StoreKit 2 a breath of fresh air. This article will guide you through the essentials of integrating StoreKit 2, covering product fetching, making purchases, processing transactions, and managing entitlements, all with practical Swift code examples.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Comparison of StoreKit 1 vs StoreKit 2 complexity">
  <title>StoreKit 1 vs StoreKit 2 Complexity</title>

  <!-- StoreKit 1 Box -->
  <rect x="50" y="30" width="220" height="150" fill="#F04B3E" rx="10" ry="10"/>
  <text x="160" y="60" font-family="Arial" font-size="20" fill="white" text-anchor="middle" font-weight="bold">StoreKit 1</text>
  <text x="160" y="90" font-family="Arial" font-size="14" fill="white" text-anchor="middle">Delegate-based APIs</text>
  <text x="160" y="110" font-family="Arial" font-size="14" fill="white" text-anchor="middle">Manual receipt validation</text>
  <text x="160" y="130" font-family="Arial" font-size="14" fill="white" text-anchor="middle">Complex state management</text>
  <text x="160" y="150" font-family="Arial" font-size="14" fill="white" text-anchor="middle">Less reliable transaction updates</text>

  <!-- StoreKit 2 Box -->
  <rect x="330" y="30" width="220" height="150" fill="#2A8367" rx="10" ry="10"/>
  <text x="440" y="60" font-family="Arial" font-size="20" fill="white" text-anchor="middle" font-weight="bold">StoreKit 2</text>
  <text x="440" y="90" font-family="Arial" font-size="14" fill="white" text-anchor="middle">Async/await APIs</text>
  <text x="440" y="110" font-family="Arial" font-size="14" fill="white" text-anchor="middle">Built-in transaction verification</text>
  <text x="440" y="130" font-family="Arial" font-size="14" fill="white" text-anchor="middle">Streamlined transaction flow</text>
  <text x="440" y="150" font-family="Arial" font-size="14" fill="white" text-anchor="middle">Reliable transaction updates (Combine/async stream)</text>

  <!-- Arrow/Label -->
  <line x1="275" y1="105" x2="325" y2="105" stroke="#1565c0" stroke-width="3" marker-end="url(#arrowhead)"/>
  <text x="300" y="95" font-family="Arial" font-size="14" fill="#1565c0" text-anchor="middle">Simplified</text>
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#1565c0" />
    </marker>
  </defs>
</svg>
</div>

## Setting Up Your Project

Before diving into code, you'll need to configure your app for in-app purchases:

1.  **App Store Connect:** Create your IAPs (Consumable, Non-Consumable, Auto-Renewable Subscription, Non-Renewing Subscription) in App Store Connect. Make sure to note their **Product IDs**. These IDs are crucial for fetching products in your app.
2.  **Xcode Capabilities:** In your Xcode project, select your target, go to the "Signing & Capabilities" tab, and add the "In-App Purchase" capability. This links your app to the StoreKit framework.

## Understanding StoreKit 2 Fundamentals

StoreKit 2 introduces several key types that form the backbone of your IAP implementation:

*   **`Product`**: Represents an item available for purchase in your app. It contains details like product ID, display name, description, and price. When you fetch products, you'll receive an array of `Product` objects.
*   **`Transaction`**: Encapsulates a completed purchase. It includes vital information such as the product purchased, the purchase date, and most importantly, the **verification status**. StoreKit 2 automatically verifies transactions on-device, providing a `VerificationResult` enum (either `.verified` or `.unverified`).
*   **`Storefront`**: Provides information about the user's current App Store storefront, including its ID and country code. Useful for displaying localized pricing.
*   **`AppStore`**: The central entry point for StoreKit 2 operations. It provides static methods for fetching products, initiating purchases, and observing transaction updates.
*   **`Transaction.updates`**: An `AsyncSequence` that delivers a continuous stream of `Transaction` objects as they are created, updated, or restored. This is the primary way to observe and process all transactions in your app.

## Fetching Products

The first step is to fetch the product information from the App Store. You'll need the `Product IDs` you configured in App Store Connect.

```swift
import StoreKit

class StoreManager: ObservableObject {
    @Published var products: [Product] = []
    // Replace with your actual product IDs from App Store Connect
    private let productIDs = ["com.yourapp.premium_feature", "com.yourapp.monthly_subscription"] 

    func requestProducts() async {
        do {
            // Request products from the App Store
            let storeProducts = try await Product.products(for: productIDs)

            // Update on the main actor since @Published vars need main thread access
            await MainActor.run {
                // Sort them for consistent display
                self.products = storeProducts.sorted { $0.id < $1.id }
                print("Fetched \(self.products.count) products.")
                for product in self.products {
                    print("Product: \(product.displayName) - \(product.displayPrice)")
                }
            }
        } catch {
            print("Failed to fetch products: \(error)")
        }
    }
}
```

You can call `requestProducts()` when your app launches or when your IAP store view appears. It's an `async` function, so remember to call it within a `Task` or an `async` context.

## Making a Purchase

Once you have your `Product` objects, initiating a purchase is straightforward. The `Product.purchase()` method handles the entire purchase flow, including presenting the App Store purchase sheet.

```swift
extension StoreManager {
    func purchase(_ product: Product) async throws -> Transaction? {
        // Begin a purchase transaction.
        let result = try await product.purchase()

        switch result {
        case .success(let verificationResult):
            // The purchase was successful. Verify and process the transaction.
            let transaction = try checkVerified(verificationResult)
            print("Purchase successful for product: \(transaction.productID)")
            return transaction
        case .userCancelled:
            print("Purchase cancelled by user.")
            return nil
        case .pending:
            print("Purchase is pending, awaiting external action.")
            return nil
        @unknown default:
            // Handle new cases that may be introduced in future StoreKit versions.
            print("Unknown purchase result.")
            return nil
        }
    }

    // Helper to check the verification result and return the verified transaction.
    private func checkVerified<T>(_ result: VerificationResult<T>) throws -> T {
        switch result {
        case .unverified(let unverifiedTransaction, let error):
            // Handle unverified transactions.
            // This could be due to a server issue, a tampered receipt, etc.
            // For production apps, you might want to log this and potentially
            // fall back to server-side receipt validation if necessary.
            print("Unverified transaction: \(unverifiedTransaction), error: \(error)")
            throw StoreError.failedVerification
        case .verified(let verifiedTransaction):
            return verifiedTransaction
        }
    }
}

enum StoreError: Error {
    case failedVerification
}
```

The `Product.purchase()` method returns a `PurchaseResult`. The most important case is `.success`, which contains a `VerificationResult<Transaction>`. StoreKit 2 automatically performs on-device receipt validation. Your `checkVerified` helper function unwraps this, ensuring you only proceed with verified transactions.

Here's a simplified flow for a purchase:

```
┌─────────────────┐     ┌─────────────────────┐     ┌─────────────────┐
│ User Taps Buy   │────►│  Product.purchase() │────►│ App Store Sheet │
└─────────────────┘     └─────────────────────┘     └─────────────────┘
         │                                               │
         ▼                                               │
┌─────────────────┐                                      │
│ PurchaseResult  │◄─────────────────────────────────────┘
│  (.success,     │
│   .userCancelled,│
│   .pending)     │
└─────────────────┘
```

## Processing Transactions and Handling Purchases

While `product.purchase()` gives you the result of a *single* purchase attempt, StoreKit 2 also provides a continuous stream of *all* transactions (new purchases, restores, refunds, subscription renewals) through `Transaction.updates`. You should always listen to this stream to ensure your app correctly grants entitlements and handles state changes, even if the app was not running when a transaction occurred.

This listener should ideally be set up early in your app's lifecycle, for example, in your `App` struct's `init()` or `onAppear` for a dedicated Store Manager.

```swift
extension StoreManager {
    func listenForTransactions() {
        Task(priority: .background) {
            for await result in Transaction.updates {
                do {
                    let transaction = try checkVerified(result)
                    await self.updateCustomerProductStatus(transaction: transaction)
                    await transaction.finish() // Mark transaction as consumed
                } catch {
                    print("Transaction failed verification or processing: \(error)")
                }
            }
        }
    }

    // This method would update your app's internal state,
    // grant content, save to UserDefaults, Core Data, etc.
    @MainActor
    private func updateCustomerProductStatus(transaction: Transaction) async {
        // Example: Granting access to a premium feature
        if transaction.productID == "com.yourapp.premium_feature" {
            // Update UI, save state, unlock content.
            // You might have a @Published var `isPremium` that you set to true.
            print("User now has premium feature access.")
        } else if transaction.productID == "com.yourapp.monthly_subscription" {
            // Handle subscription entitlements.
            // For subscriptions, you'd typically check `transaction.expirationDate`
            // and potentially fetch the full subscription status using `Product.SubscriptionInfo.status`.
            print("User has an active monthly subscription.")
        }

        // Always ensure that only *purchased* and *not revoked* transactions grant entitlements.
        // For production, you might want more sophisticated logic, especially for subscriptions.
    }
}
```

The `listenForTransactions()` function creates a `Task` that continuously awaits new transactions from `Transaction.updates`. For each transaction, we verify it using our `checkVerified` helper, update the customer's entitlements, and then **finish** the transaction using `await transaction.finish()`. Finishing a transaction tells the App Store that your app has successfully processed it and it won't be delivered again.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 250" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="StoreKit 2 Transaction Processing Flow">
  <title>StoreKit 2 Transaction Processing Flow</title>

  <!-- Start Node -->
  <circle cx="100" cy="50" r="20" fill="#1565c0"/>
  <text x="100" y="55" font-family="Arial" font-size="12" fill="white" text-anchor="middle">Start</text>

  <!-- Transaction.updates loop -->
  <rect x="180" y="30" width="180" height="40" fill="#2A8367" rx="5" ry="5"/>
  <text x="270" y="55" font-family="Arial" font-size="14" fill="white" text-anchor="middle">Transaction.updates AsyncSequence</text>
  <line x1="120" y1="50" x2="180" y2="50" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowhead)"/>

  <!-- Process Transaction -->
  <rect x="200" y="100" width="140" height="40" fill="#2A8367" rx="5" ry="5"/>
  <text x="270" y="125" font-family="Arial" font-size="14" fill="white" text-anchor="middle">Process Transaction</text>
  <line x1="270" y1="70" x2="270" y2="100" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowhead)"/>

  <!-- Verify Transaction -->
  <rect x="200" y="160" width="140" height="40" fill="#1565c0" rx="5" ry="5"/>
  <text x="270" y="185" font-family="Arial" font-size="14" fill="white" text-anchor="middle">Verify Transaction (checkVerified)</text>
  <line x1="270" y1="140" x2="270" y2="160" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowhead)"/>

  <!-- Decision: Verified? -->
  <rect x="230" y="210" width="80" height="40" fill="#F04B3E" rx="5" ry="5"/>
  <text x="270" y="235" font-family="Arial" font-size="12" fill="white" text-anchor="middle" dominant-baseline="middle">Verified?</text>
  <line x1="270" y1="200" x2="270" y2="210" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowhead)"/>

  <!-- If Verified -->
  <rect x="400" y="160" width="150" height="40" fill="#2A8367" rx="5" ry="5"/>
  <text x="475" y="185" font-family="Arial" font-size="14" fill="white" text-anchor="middle">Grant Entitlement</text>
  <line x1="310" y1="230" x2="400" y2="180" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="360" y="200" font-family="Arial" font-size="12" fill="#1565c0" text-anchor="middle">Yes</text>

  <!-- If Not Verified -->
  <rect x="400" y="210" width="150" height="40" fill="#F04B3E" rx="5" ry="5"/>
  <text x="475" y="235" font-family="Arial" font-size="14" fill="white" text-anchor="middle">Handle Error/Log</text>
  <line x1="270" y1="250" x2="400" y2="230" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="335" y="240" font-family="Arial" font-size="12" fill="#1565c0" text-anchor="middle">No</text>

  <!-- Finish Transaction -->
  <rect x="400" y="80" width="150" height="40" fill="#1565c0" rx="5" ry="5"/>
  <text x="475" y="105" font-family="Arial" font-size="14" fill="white" text-anchor="middle">Finish Transaction</text>
  <line x1="475" y1="160" x2="475" y2="120" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowhead)"/>
  <line x1="475" y1="210" x2="475" y2="120" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowhead)"/>

  <!-- Loop back to Transaction.updates -->
  <line x1="550" y1="100" x2="570" y2="100" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowhead)"/>
  <line x1="570" y1="100" x2="570" y1="50" stroke="#1565c0" stroke-width="2"/>
  <line x1="570" y1="50" x2="360" y2="50" stroke="#1565c0" stroke-width="2" marker-end="url(#arrowhead)"/>

  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#1565c0" />
    </marker>
  </defs>
</svg>
</div>

## Restoring Purchases

For non-consumable products and subscriptions, users expect to be able to restore their purchases if they reinstall the app or get a new device. StoreKit 2 simplifies this significantly. Instead of a separate "Restore Purchases" button that triggers a specific delegate method, you primarily rely on `AppStore.sync()` and iterating through `Transaction.currentEntitlements`.

`AppStore.sync()` ensures that your app's local receipt is up-to-date with the latest information from the App Store. Then, you can simply iterate through `Transaction.currentEntitlements` to get all valid, non-expired transactions associated with the user's Apple ID.

```swift
extension StoreManager {
    func restorePurchases() async {
        do {
            // This syncs the local receipt with the App Store.
            // It's good practice to call this periodically or when a user explicitly requests restore.
            try await AppStore.sync()

            // Iterate through all current entitlements for the user.
            for await result in Transaction.currentEntitlements {
                do {
                    let transaction = try checkVerified(result)
                    await updateCustomerProductStatus(transaction: transaction)
                    // No need to call transaction.finish() here, as these are already finished transactions
                    // being delivered for entitlement checks.
                } catch {
                    print("Failed to restore an entitlement: \(error)")
                }
            }
            print("Purchases restored successfully.")
        } catch {
            print("Failed to sync or restore purchases: \(error)")
        }
    }
}
```
You can call `restorePurchases()` from a UI button or when your app first launches to ensure all entitlements are correctly applied.

## Subscription Management

StoreKit 2 provides robust tools for managing subscriptions. Each `Product` has a `subscription` property (`Product.SubscriptionInfo?`) that provides details like subscription group ID, renewal period, and introductory offers.

When processing a `Transaction` for a subscription, you can access `transaction.expirationDate` to determine when the subscription will expire. For more detailed status, especially for auto-renewable subscriptions, you can fetch `Product.SubscriptionInfo.status` which gives you the current status (e.g., active, expired, grace period) and renewal information.

For users to manage their subscriptions (e.g., change plan, cancel), Apple provides built-in StoreKit views:

```swift
import SwiftUI
import StoreKit

struct SubscriptionManagementView: View {
    @State private var showManageSubscriptions = false

    var body: some View {
        Button("Manage Subscriptions") {
            showManageSubscriptions = true
        }
        .manageSubscriptionsSheet(isPresented: $showManageSubscriptions)
    }
}
```
Using `.manageSubscriptionsSheet` is the recommended way to let users manage their subscriptions without leaving your app, providing a consistent and secure experience.

## Testing In-App Purchases

Testing IAPs is crucial and StoreKit 2 significantly improves the developer experience:

*   **StoreKit Testing in Xcode:** You can create a `.storekit` file in your Xcode project to define your products locally. This allows for rapid testing without needing to configure products in App Store Connect or use a sandbox tester account initially. You can simulate various scenarios like successful purchases, failed purchases, refunds, and subscription renewals.
*   **Sandbox Environment:** For testing with actual App Store Connect configurations and sandbox user accounts, you'll still use the sandbox environment. Ensure your device is signed in with a sandbox tester Apple ID.

## Error Handling

StoreKit operations can fail for various reasons (network issues, user cancellation, payment problems). Always wrap your StoreKit 2 calls in `do-catch` blocks or handle `throws` appropriately. Common errors you might encounter include `Product.PurchaseError`, `StoreKitError` (for general StoreKit issues), and custom errors you define (like `StoreError.failedVerification`). Providing clear feedback to the user when an error occurs is important for a good user experience.

## Summary

StoreKit 2 offers a powerful and streamlined approach to integrating in-app purchases into your iOS applications. By leveraging Swift's async/await, it simplifies product fetching, transaction processing, and entitlement management, significantly reducing the boilerplate and complexity inherent in its predecessor. Key takeaways include:

*   Using `Product.products(for:)` to fetch IAP details.
*   Initiating purchases with `product.purchase()` and handling `PurchaseResult`.
*   Setting up a continuous listener for `Transaction.updates` to reliably process all transactions, including restores and renewals.
*   Verifying transactions on-device using `VerificationResult`.
*   Simplifying subscription management and restoration with `Product.SubscriptionInfo` and `AppStore.sync()`.
*   Utilizing StoreKit Testing in Xcode for efficient development.

Embracing StoreKit 2 not only makes your IAP implementation more robust and easier to maintain but also aligns your app with Apple's modern concurrency best practices.

Happy Swifting!
