---
title: App Store Connect Submission Checklist for iOS
date: 2026-08-10 10:10
description: A comprehensive checklist to streamline your iOS app submission to App Store Connect, covering Xcode setup, metadata, and review best practices.
tags: App Store, iOS, Development
---

# App Store Connect Submission Checklist for iOS

The moment of truth for any iOS developer is the App Store submission. After countless hours of coding, testing, and refining, the final hurdle is getting your app approved and published on the App Store. While it can feel daunting, a well-organized checklist can transform this complex process into a manageable series of steps.

This article provides a comprehensive, step-by-step checklist to guide you through preparing and submitting your iOS app to App Store Connect. We'll cover everything from Xcode configurations to metadata, ensuring you're ready for a smooth review process and a successful launch.

Let's dive in!

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="High-level iOS App Submission Flow">
  <title>High-level iOS App Submission Flow</title>
  <style>
    .box { fill: #1565c0; stroke: #0d47a1; stroke-width: 2; rx: 8; ry: 8; }
    .arrow { stroke: #333; stroke-width: 2; marker-end: url(#arrowhead); }
    .text { font-family: sans-serif; font-size: 16px; fill: white; text-anchor: middle; dominant-baseline: central; }
    .label-text { font-family: sans-serif; font-size: 14px; fill: #333; text-anchor: middle; dominant-baseline: central; }
  </style>
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
    </marker>
  </defs>

  <!-- Boxes -->
  <rect class="box" x="20" y="70" width="100" height="60" />
  <text class="text" x="70" y="100">Develop</text>

  <rect class="box" x="140" y="70" width="100" height="60" />
  <text class="text" x="190" y="100">Test</text>

  <rect class="box" x="260" y="70" width="100" height="60" />
  <text class="text" x="310" y="100">Configure</text>

  <rect class="box" x="380" y="70" width="100" height="60" />
  <text class="text" x="430" y="100">Submit</text>

  <rect class="box" x="500" y="70" width="100" height="60" />
  <text class="text" x="550" y="100">Review</text>

  <!-- Arrows -->
  <line class="arrow" x1="120" y1="100" x2="140" y2="100" />
  <line class="arrow" x1="240" y1="100" x2="260" y2="100" />
  <line class="arrow" x1="360" y1="100" x2="380" y2="100" />
  <line class="arrow" x1="480" y1="100" x2="500" y2="100" />

  <!-- Labels -->
  <text class="label-text" x="70" y="40">Build Features</text>
  <text class="label-text" x="190" y="40">Internal & TestFlight</text>
  <text class="label-text" x="310" y="40">App Store Connect</text>
  <text class="label-text" x="430" y="40">Upload Build</text>
  <text class="label-text" x="550" y="40">Apple's Approval</text>
</svg>
</div>

## Pre-Submission Checklist: Inside Xcode

Before you even think about App Store Connect, your Xcode project needs to be in tip-top shape.

### 1. App Icons & Launch Screen

*   **App Icons:** Ensure all required icon sizes are present in your Asset Catalog (`AppIcon`). Missing sizes or using a placeholder icon will lead to rejection. Pay attention to both iOS and potentially iPadOS/watchOS/macOS icons if your app supports multiple platforms.
*   **Launch Screen:** Your app must include a launch screen (either a Storyboard or `LaunchScreen.storyboard` file). Avoid using a static image for the launch screen as it doesn't scale well across devices. Ensure it reflects your app's branding and doesn't display any interactive elements or text that changes.

### 2. Bundle Identifier & Versioning

*   **Bundle Identifier:** This must be unique across the App Store and match the one registered in App Store Connect. It's usually in the format `com.yourcompany.yourappname`. You configure this in your project's `Info.plist` or target's General settings.
*   **Version Number (`CFBundleShortVersionString`):** This is your marketing version number (e.g., "1.0", "1.0.1"). Users see this.
*   **Build Number (`CFBundleVersion`):** This is an internal version number (e.g., "1", "2", "3"). It must be incremented with every new build you upload to App Store Connect, even if the marketing version hasn't changed.

### 3. Provisioning Profiles & Certificates

*   **Distribution Profile:** For App Store submissions, you need an "App Store" distribution provisioning profile.
*   **Automatic vs. Manual Signing:** For most developers, Xcode's "Automatically manage signing" option works best. Ensure you've selected the correct development team. If you're managing profiles manually, double-check that your "Release" build configuration uses the correct App Store Distribution profile and certificate.

### 4. Code Signing Entitlements

*   **Capabilities:** If your app uses specific Apple services (e.g., Push Notifications, iCloud, App Groups, Sign In with Apple, Wallet, HealthKit, SiriKit), ensure these capabilities are correctly enabled in Xcode (under your target's "Signing & Capabilities" tab) and match the services configured for your App ID in the Apple Developer Portal. Mismatches will cause build submission failures or runtime issues.

### 5. Privacy Manifests (iOS 17+)

*   **Required Declaration:** For apps targeting iOS 17 and later, you must include a `PrivacyInfo.xcprivacy` file in your project. This file declares the types of data your app collects and reasons for API usage that impacts privacy (e.g., `UserDefaults`, `FileManager`, `SystemBootTime`). Failing to include this or providing inaccurate information can lead to rejection.

### 6. Target Device Support & Orientation

*   **Device Compatibility:** In your project's General settings (under "Deployment Info"), specify whether your app supports iPhone, iPad, or both ("Universal").
*   **Supported Orientations:** Define the allowed device orientations (Portrait, Landscape Left/Right). Ensure your UI adapts correctly to all supported orientations.

### 7. App Thinning & Bitcode

*   **App Thinning:** Xcode automatically optimizes your app's size for different devices. Ensure your Asset Catalogs are set up correctly for this.
*   **Bitcode:** While historically important, Bitcode is no longer required for iOS, tvOS, or watchOS apps. You can generally leave "Enable Bitcode" set to "No" in your build settings for modern iOS projects.

## Pre-Submission Checklist: Outside Xcode (Content & Legal)

With your Xcode project polished, it's time to prepare the assets and information for your App Store product page. This content is crucial for attracting users and passing review.

### 1. App Store Product Page Assets

*   **Screenshots:**
    *   Minimum of 1, maximum of 10 per localization.
    *   Capture screenshots for all supported device families (iPhone, iPad, potentially Apple Watch, Mac).
    *   For iPhone, you need screenshots for the largest display (e.g., 6.7-inch iPhone) and 5.5-inch iPhone.
    *   For iPad, you need screenshots for the 12.9-inch iPad Pro (2nd Gen) and 12.9-inch iPad Pro (3rd Gen).
    *   Make them compelling, showcasing your app's best features.
*   **App Previews (Optional but Recommended):** Short videos (15-30 seconds) demonstrating your app's features. These can significantly boost downloads.
*   **App Icon (1024x1024):** A high-resolution version of your app icon. This is distinct from the icons in your Xcode Asset Catalog.

### 2. App Store Metadata

This information is what users see on your App Store listing.

*   **App Name:** Up to 30 characters. Make it unique, memorable, and descriptive.
*   **Subtitle:** Up to 30 characters. A brief phrase that expands on your app’s value.
*   **Promotional Text:** Up to 170 characters. Appears above your description and can be updated anytime without a new app version. Use it for announcements or sales.
*   **Keywords:** Up to 100 characters, comma-separated. Use relevant terms users might search for. Avoid competitor names or irrelevant words.
*   **Description:** Up to 4000 characters. A compelling, clear, and concise explanation of what your app does and why users need it. Highlight key features and benefits.
*   **Support URL:** A link to a webpage where users can get support for your app.
*   **Marketing URL (Optional):** A link to your app's marketing website.
*   **Privacy Policy URL:** A **mandatory** link to your app's privacy policy. This must be a live, accessible URL.

### 3. Pricing & Availability

*   **Price Tier:** Choose your app's price from a predefined list of tiers.
*   **Geographical Availability:** Select the countries/regions where your app will be available.

### 4. App Information

*   **Category:** Choose a primary category and an optional secondary category that best describes your app.
*   **Content Rating:** Complete the content rating questionnaire accurately. This determines the age rating for your app. Misrepresenting content can lead to rejection.
*   **Copyright:** Enter the name of the person or entity that owns the exclusive rights to your app, preceded by the year the rights were acquired (e.g., "2024 YourCompany, Inc.").

### 5. App Privacy Details

This section in App Store Connect requires you to declare your app's data collection practices. Be transparent and accurate.

*   **Data Collection:** Declare what data your app and its third-party partners collect (e.g., location, contact info, identifiers, usage data).
*   **Data Usage:** Explain how this data is used (e.g., app functionality, analytics, personalization).

### 6. Export Compliance (if applicable)

If your app uses encryption (other than standard HTTPS connections), you might need to answer export compliance questions. Be prepared to provide details if required.

```
┌────────────────────────────────┐
│       App Store Connect        │
└───────────────┬────────────────┘
                │
                ▼
┌───────────────────────────────┐
│           My Apps             │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│        App Information        │
│        Pricing & Availability │
│        App Privacy            │
│        TestFlight             │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│      App Version Details      │
│      (e.g., 1.0)              │
│      - Build                  │
│      - Screenshots            │
│      - Metadata               │
│      - Review Information     │
└───────────────────────────────┘
```

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 700 250" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Common App Store Review Rejection Reasons">
  <title>Common App Store Review Rejection Reasons</title>
  <style>
    .node { fill: #1565c0; stroke: #0d47a1; stroke-width: 2; rx: 8; ry: 8; }
    .decision { fill: #F04B3E; stroke: #c62828; stroke-width: 2; rx: 8; ry: 8; }
    .success { fill: #2A8367; stroke: #1b5e20; stroke-width: 2; rx: 8; ry: 8; }
    .text { font-family: sans-serif; font-size: 14px; fill: white; text-anchor: middle; dominant-baseline: central; }
    .label-text { font-family: sans-serif; font-size: 12px; fill: #333; text-anchor: middle; dominant-baseline: central; }
    .arrow { stroke: #333; stroke-width: 1; marker-end: url(#arrowhead); }
  </style>
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
    </marker>
  </defs>

  <!-- Start Node -->
  <rect class="node" x="250" y="20" width="200" height="40" />
  <text class="text" x="350" y="40">App Submitted for Review</text>

  <!-- Decision Point -->
  <rect class="decision" x="250" y="90" width="200" height="40" />
  <text class="text" x="350" y="110">Passes Initial Checks?</text>

  <!-- Paths -->
  <line class="arrow" x1="350" y1="60" x2="350" y2="90" />

  <!-- Rejection Reasons -->
  <rect class="node" x="20" y="180" width="150" height="40" />
  <text class="text" x="95" y="200">Metadata Issues</text>
  <line class="arrow" x1="260" y1="130" x2="160" y2="180" />
  <text class="label-text" x="210" y="155">No (A)</text>

  <rect class="node" x="180" y="180" width="150" height="40" />
  <text class="text" x="255" y="200">Broken Functionality</text>
  <line class="arrow" x1="350" y1="130" x2="280" y2="180" />
  <text class="label-text" x="310" y="155">No (B)</text>

  <rect class="node" x="340" y="180" width="150" height="40" />
  <text class="text" x="415" y="200">Privacy Non-Compliance</text>
  <line class="arrow" x1="440" y1="130" x2="415" y2="180" />
  <text class="label-text" x="435" y="155">No (C)</text>

  <rect class="node" x="500" y="180" width="150" height="40" />
  <text class="text" x="575" y="200">Poor User Experience</text>
  <line class="arrow" x1="440" y1="130" x2="510" y2="180" />
  <text class="label-text" x="470" y="155">No (D)</text>

  <!-- Approval Path -->
  <rect class="success" x="550" y="90" width="100" height="40" />
  <text class="text" x="600" y="110">Approved!</text>
  <line class="arrow" x1="450" y1="110" x2="550" y2="110" />
  <text class="label-text" x="500" y="85">Yes</text>
</svg>
</div>

## Submitting the Build

Once all your preparations are complete, it's time to get your app into App Store Connect.

### 1. Archiving the App

In Xcode:
1.  Select your app's scheme.
2.  Ensure your target device is set to "Any iOS Device (arm64)" or a specific physical device, **not** a simulator.
3.  Go to `Product > Archive`. Xcode will build your app and open the Organizer window.

### 2. Uploading to App Store Connect

From the Organizer window:
1.  Select your archived build.
2.  Click "Distribute App".
3.  Choose "App Store Connect" as the method.
4.  Select "App Store Distribution" for the destination.
5.  Follow the prompts to sign and upload your app. Xcode will perform various validations before uploading. Alternatively, you can use the standalone [Transporter app](https://apps.apple.com/us/app/transporter/id1450874784) for uploading.

After uploading, your build will appear in App Store Connect under the "TestFlight" tab, usually within 15-30 minutes, sometimes longer. It will show as "Processing".

### 3. Testing with TestFlight

**Crucial Step:** Before submitting for review, always test your uploaded build using TestFlight.

*   **Internal Testing:** Add developers and testers from your App Store Connect team to internal groups. They can immediately download and test the build.
*   **External Testing:** For broader testing, you can invite external testers. These builds require a beta app review by Apple before they become available.
*   **Why TestFlight?** It ensures your distribution build functions as expected, helps catch last-minute bugs specific to the App Store environment, and provides valuable feedback.

You can check if your app is running via TestFlight using the `appStoreReceiptURL` property:

```swift
import Foundation

func isRunningInTestFlight() -> Bool {
    guard let url = Bundle.main.appStoreReceiptURL else {
        return false
    }

    // Check if the URL contains "sandboxReceipt"
    // This indicates it's a test receipt, common in TestFlight builds
    let isSandboxReceipt = url.lastPathComponent == "sandboxReceipt"

    // Further check for the presence of the embedded.mobileprovision file
    // TestFlight builds often contain this, while App Store builds typically do not
    let hasEmbeddedProvision = Bundle.main.path(forResource: "embedded", ofType: "mobileprovision") != nil

    return isSandboxReceipt || hasEmbeddedProvision
}

// Example usage:
if isRunningInTestFlight() {
    print("App is running in TestFlight or Sandbox environment.")
    // Adjust behavior for testing, e.g., disable analytics or show debug info
} else {
    print("App is running in production or development environment.")
}
```
*Note: This check is a heuristic and might not cover all edge cases, but it's a common and generally reliable way to detect the TestFlight environment.*

## Final Review & Submission

Finally, navigate to your app's version in App Store Connect.

1.  **Select the Build:** Under the "Build" section, click the "+" button and select the build you just uploaded.
2.  **Review All Information:** Go through every section (App Information, Pricing, App Privacy, Version Information, etc.) one last time. Double-check your screenshots, description, keywords, and privacy declarations.
3.  **Contact Information:** Provide accurate contact details for the App Review team.
4.  **Notes for App Review (Crucial!):**
    *   **Login Credentials:** If your app requires a login, provide a working demo account (username and password) for the reviewers.
    *   **Specific Instructions:** Explain any non-obvious features, complex workflows, or areas that might require special attention during testing.
    *   **Hardware Requirements:** If your app needs specific hardware or accessories, mention it.
    *   **Language:** If your app is not fully localized into English, specify the primary language.
5.  **Release Options:** Choose how your app will be released:
    *   **Manually release this version:** You manually click "Release" after approval.
    *   **Automatically release this version:** The app goes live immediately upon approval.
    *   **Release this version after your first Mac app version is approved:** For universal purchases.
6.  **Submit for Review:** Click the "Submit for Review" button.

### After Submission

*   **Patience:** App review times vary, but Apple usually provides an estimated timeframe. You can check the status in App Store Connect.
*   **Handling Rejections:** If your app is rejected, don't panic. Read the rejection message carefully. Apple usually provides specific reasons and guidelines. Fix the issues, update your app, and resubmit. Use the Resolution Center in App Store Connect to communicate with the review team if you need clarification.

### Summary

Submitting an iOS app to the App Store is a meticulous process, but with a thorough checklist, it becomes much more manageable. By meticulously preparing your Xcode project, crafting compelling App Store metadata, understanding privacy requirements, and thoroughly testing with TestFlight, you significantly increase your chances of a smooth approval and a successful launch. Remember, attention to detail and adherence to Apple's guidelines are key.

Happy Swifting!
