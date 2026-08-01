---
title: App Transport Security Best Practices on iOS
date: 2026-08-01 10:28
description: Learn about App Transport Security (ATS) on iOS, why it's crucial for app security, and how to implement best practices for secure network communication, including configuring Info.plist exceptions.
tags: Security, iOS, Development
---

# App Transport Security Best Practices on iOS

In the world of mobile app development, security is paramount. Users trust our apps with their data, and it's our responsibility to protect it. A critical component of this security on Apple platforms is App Transport Security (ATS). Introduced in iOS 9, ATS significantly enhances user privacy and data integrity by enforcing secure network connections by default.

But what exactly is ATS, and how does it impact your app? More importantly, what are the best practices for working with it, especially when dealing with legacy systems that might not yet meet modern security standards? This article will dive deep into ATS, providing you with the knowledge and practical steps to ensure your app's network communications are secure and compliant.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="App Transport Security (ATS) Flow">
  <title>App Transport Security (ATS) Flow</title>
  <!-- Background -->
  <rect x="0" y="0" width="600" height="220" fill="#ffffff"/>

  <!-- App Box -->
  <rect x="50" y="80" width="100" height="60" rx="10" ry="10" fill="#1565c0" stroke="#000" stroke-width="2"/>
  <text x="100" y="115" font-family="Arial" font-size="20" fill="#fff" text-anchor="middle">Your App</text>

  <!-- ATS Gate -->
  <rect x="250" y="60" width="100" height="100" rx="10" ry="10" fill="#2A8367" stroke="#000" stroke-width="2"/>
  <text x="300" y="85" font-family="Arial" font-size="20" fill="#fff" text-anchor="middle">ATS</text>
  <text x="300" y="110" font-family="Arial" font-size="14" fill="#fff" text-anchor="middle">(Security</text>
  <text x="300" y="128" font-family="Arial" font-size="14" fill="#fff" text-anchor="middle">Gate)</text>

  <!-- Server Box (Secure) -->
  <rect x="450" y="50" width="100" height="60" rx="10" ry="10" fill="#2A8367" stroke="#000" stroke-width="2"/>
  <text x="500" y="85" font-family="Arial" font-size="18" fill="#fff" text-anchor="middle">Secure</text>
  <text x="500" y="105" font-family="Arial" font-size="18" fill="#fff" text-anchor="middle">Server</text>

  <!-- Server Box (Insecure) -->
  <rect x="450" y="130" width="100" height="60" rx="10" ry="10" fill="#F04B3E" stroke="#000" stroke-width="2"/>
  <text x="500" y="165" font-family="Arial" font-size="18" fill="#fff" text-anchor="middle">Insecure</text>
  <text x="500" y="185" font-family="Arial" font-size="18" fill="#fff" text-anchor="middle">Server</text>

  <!-- Arrow App to ATS -->
  <line x1="150" y1="110" x2="250" y2="110" stroke="#000" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="200" y="100" font-family="Arial" font-size="14" fill="#000" text-anchor="middle">Network Request</text>

  <!-- Arrow ATS to Secure Server -->
  <line x1="350" y1="90" x2="450" y2="90" stroke="#2A8367" stroke-width="2" marker-end="url(#arrowheadGreen)"/>
  <text x="400" y="80" font-family="Arial" font-size="14" fill="#2A8367" text-anchor="middle">Allowed</text>

  <!-- Arrow ATS to Insecure Server (Blocked) -->
  <line x1="350" y1="140" x2="450" y2="140" stroke="#F04B3E" stroke-width="2" marker-end="url(#arrowheadRed)"/>
  <text x="400" y="130" font-family="Arial" font-size="14" fill="#F04B3E" text-anchor="middle">Blocked</text>

  <!-- Arrowhead definitions -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#000" />
    </marker>
    <marker id="arrowheadGreen" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#2A8367" />
    </marker>
    <marker id="arrowheadRed" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#F04B3E" />
    </marker>
  </defs>
</svg>
</div>

## Understanding App Transport Security (ATS)

At its core, ATS is a set of policies that dictate how your app can connect to web services. Since iOS 9, watchOS 2, tvOS 9, and macOS 10.11, ATS has been enabled by default for all new apps. This means that all HTTP connections made by your app must conform to specific security requirements.

Specifically, ATS requires:

1.  **HTTPS (TLS 1.2 or higher)**: All connections must use HTTPS. This encrypts data in transit, preventing eavesdropping and tampering.
2.  **Forward Secrecy**: The server must support Forward Secrecy, which ensures that even if a server's long-term private key is compromised, past communications remain secure.
3.  **Strong Cipher Suites**: Only modern, strong cryptographic cipher suites are allowed.
4.  **Trusted Certificates**: Server certificates must be signed by a trusted Certificate Authority (CA) and meet specific size requirements (e.g., RSA 2048-bit or greater, ECDSA 256-bit or greater).

If your app attempts to connect to a server that doesn't meet these criteria, the connection will fail, resulting in an error similar to `App Transport Security has blocked a cleartext HTTP (http://) resource load because it is insecure.`. This aggressive stance by Apple is a clear signal: secure your network communications.

## The Default ATS Behavior

By default, any network request originating from your app using `URLSession` (or other higher-level APIs like `WebKit`) will be subject to ATS scrutiny. If the destination server does not adhere to the strict ATS requirements, the connection will be blocked. This is a good thing for security, as it protects users from potential Man-in-the-Middle (MitM) attacks, data interception, and other vulnerabilities associated with insecure HTTP connections.

For most modern applications that communicate with well-maintained APIs, ATS should not be an issue. However, challenges arise when integrating with older, third-party services, legacy internal APIs, or content delivery networks (CDNs) that might not yet have fully adopted modern security standards.

## When and How to Bypass ATS (Carefully!)

While Apple strongly discourages disabling ATS, they provide mechanisms to create exceptions when absolutely necessary. These exceptions are configured in your app's `Info.plist` file, under the `NSAppTransportSecurity` dictionary. It's crucial to understand that bypassing ATS should be a last resort and done with extreme caution, always aiming to secure the backend service itself rather than weakening your app's security posture.

Here are the primary ways to configure ATS exceptions, from least to most recommended:

### 1. `NSAllowsArbitraryLoads` (The "Nuclear Option")

This boolean key, when set to `YES`, completely disables ATS for *all* domains. This is highly discouraged by Apple and should **never** be used in production apps. It opens up your app and users to significant security risks, allowing connections over insecure HTTP and to servers with weak TLS configurations.

```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/> <!-- AVOID THIS IN PRODUCTION! -->
</dict>
```

If you ever find this key set to `true` in your `Info.plist`, you should make it a top priority to remove it and adopt more granular exceptions or, ideally, migrate your backend to secure HTTPS.

### 2. `NSAllowsArbitraryLoadsForMedia`

This key is a slightly less dangerous version of `NSAllowsArbitraryLoads`, allowing arbitrary loads specifically for media content (e.g., video and audio streams). It's intended for scenarios where you need to play media from various sources, some of which might be insecure, but your core data communications remain protected by ATS.

```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoadsForMedia</key>
    <true/>
</dict>
```
While better than a full arbitrary load, still use this with caution and only for media content.

### 3. `NSExceptionDomains` (The Recommended Approach)

This is the preferred and most secure way to bypass ATS for specific domains. `NSExceptionDomains` is a dictionary where each key is a domain name (e.g., `api.legacy.com`), and its value is another dictionary containing specific exception rules for that domain. This allows you to apply exceptions only where they are strictly necessary, keeping the rest of your app's connections secure.

Here are the common keys you can use within an `NSExceptionDomains` entry:

*   **`NSExceptionAllowsInsecureHTTPLoads`** (Boolean): Set to `true` if the domain serves content over plain HTTP. This is often the primary reason for needing an exception.
*   **`NSExceptionMinimumTLSVersion`** (String): Specifies the minimum TLS version required for this domain (e.g., `TLSv1.0`, `TLSv1.1`, `TLSv1.2`). Use this if a server cannot meet TLS 1.2.
*   **`NSExceptionRequiresForwardSecrecy`** (Boolean): Set to `false` if the domain does not support Forward Secrecy. By default, even exceptions require Forward Secrecy.
*   **`NSIncludesSubdomains`** (Boolean): Set to `true` if the exception should also apply to all subdomains of the specified domain (e.g., `sub.api.legacy.com`).

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="ATS Exception Strategies Comparison">
  <title>ATS Exception Strategies Comparison</title>
  <!-- Background -->
  <rect x="0" y="0" width="600" height="220" fill="#ffffff"/>

  <!-- Arbitrary Loads Section -->
  <rect x="50" y="30" width="250" height="160" rx="10" ry="10" fill="#F04B3E" stroke="#000" stroke-width="2"/>
  <text x="175" y="60" font-family="Arial" font-size="20" fill="#fff" text-anchor="middle" font-weight="bold">NSAllowsArbitraryLoads</text>
  <text x="175" y="90" font-family="Arial" font-size="16" fill="#fff" text-anchor="middle">"The Nuclear Option"</text>
  <text x="175" y="120" font-family="Arial" font-size="14" fill="#fff" text-anchor="middle">Disables ATS for ALL domains.</text>
  <text x="175" y="140" font-family="Arial" font-size="14" fill="#fff" text-anchor="middle">High security risk.</text>
  <text x="175" y="160" font-family="Arial" font-size="14" fill="#fff" text-anchor="middle">Avoid in production.</text>

  <!-- Exception Domains Section -->
  <rect x="300" y="30" width="250" height="160" rx="10" ry="10" fill="#1565c0" stroke="#000" stroke-width="2"/>
  <text x="425" y="60" font-family="Arial" font-size="20" fill="#fff" text-anchor="middle" font-weight="bold">NSExceptionDomains</text>
  <text x="425" y="90" font-family="Arial" font-size="16" fill="#fff" text-anchor="middle">"Granular Control"</text>
  <text x="425" y="120" font-family="Arial" font-size="14" fill="#fff" text-anchor="middle">Disables ATS for SPECIFIC domains.</text>
  <text x="425" y="140" font-family="Arial" font-size="14" fill="#fff" text-anchor="middle">Lower, controlled risk.</text>
  <text x="425" y="160" font-family="Arial" font-size="14" fill="#fff" text-anchor="middle">Recommended for exceptions.</text>
</svg>
</div>

### Practical Example: Configuring `NSExceptionDomains`

Let's say your app needs to connect to `http://legacy.api.example.com` which only supports HTTP and an older TLS version (e.g., TLS 1.0) without Forward Secrecy, and also `https://another.api.example.com` which is HTTPS but also lacks Forward Secrecy.

Your `Info.plist` would look something like this:

```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSExceptionDomains</key>
    <dict>
        <key>legacy.api.example.com</key>
        <dict>
            <key>NSExceptionAllowsInsecureHTTPLoads</key>
            <true/>
            <key>NSExceptionMinimumTLSVersion</key>
            <string>TLSv1.0</string>
            <key>NSExceptionRequiresForwardSecrecy</key>
            <false/>
        </dict>
        <key>another.api.example.com</key>
        <dict>
            <key>NSExceptionRequiresForwardSecrecy</key>
            <false/>
            <key>NSIncludesSubdomains</key>
            <true/> <!-- Applies to any.another.api.example.com too -->
        </dict>
    </dict>
</dict>
```

With this configuration, only `legacy.api.example.com` and `another.api.example.com` (and its subdomains) will have relaxed ATS rules, while all other network connections in your app will still enforce the strict default ATS requirements.

### Swift Code Example for Network Request

Here's a simple `URLSession` example that demonstrates how ATS might affect your requests. If you try to access an `http://` URL without proper `NSExceptionDomains` setup, it will fail.

```swift
import Foundation

func makeNetworkRequest(to urlString: String) async {
    guard let url = URL(string: urlString) else {
        print("Invalid URL: \(urlString)")
        return
    }

    print("Attempting to connect to: \(urlString)")

    do {
        let (data, response) = try await URLSession.shared.data(from: url)
        guard let httpResponse = response as? HTTPURLResponse else {
            print("Not an HTTP response for \(urlString).")
            return
        }

        if (200...299).contains(httpResponse.statusCode) {
            print("✅ Successfully fetched data from \(urlString). Status Code: \(httpResponse.statusCode)")
            // Optionally print data:
            // print("Data: \(String(data: data, encoding: .utf8) ?? "N/A")")
        } else {
            print("❌ Request failed for \(urlString). Status Code: \(httpResponse.statusCode)")
            print("Response headers: \(httpResponse.allHeaderFields)")
        }
    } catch {
        print("❌ Network request failed for \(urlString) with error: \(error.localizedDescription)")
        if let urlError = error as? URLError, urlError.code == .appTransportSecurityRequiresSecureConnection {
            print("💡 This error is likely due to App Transport Security (ATS) blocking an insecure connection.")
            print("   Consider updating your server to HTTPS or configuring ATS exceptions carefully in Info.plist.")
        }
    }
}

// To run this, you'd typically call it within a Task in an async context,
// for example, from a button action or in an `onAppear` modifier in SwiftUI.
// For demonstration, let's simulate calls:

/*
// Example Usage:
Task {
    // This will likely succeed if the domain is secure and ATS compliant
    await makeNetworkRequest(to: "https://api.github.com/zen")

    // This will likely fail due to ATS if 'insecure.example.com' is HTTP
    // and not configured in NSExceptionDomains
    await makeNetworkRequest(to: "http://insecure.example.com/data")

    // If 'legacy.api.example.com' is configured in NSExceptionDomains
    // as shown above, this might succeed even if it's HTTP.
    await makeNetworkRequest(to: "http://legacy.api.example.com/status")
}
*/
```

## Checking ATS Compliance with `nscurl`

Before even writing a single line of Swift code, you can test a URL's ATS compliance using the `nscurl` command-line tool. This tool simulates a `URLSession` request and reports any ATS violations.

Open your Terminal and run:

```bash
nscurl --ats-diagnostics https://api.example.com
```

Replace `https://api.example.com` with the actual URL you want to test. The output will detail which ATS requirements are met or failed for the given URL. Look for lines like `ATS Dictionary: (null)` (meaning no exceptions needed for that URL) or specific failures (`Result : FAIL`). This is an invaluable tool for debugging ATS issues.

## Best Practices and Recommendations

1.  **Prioritize Securing Your Backend**: The absolute best practice is to ensure all your backend services and third-party APIs use HTTPS with TLS 1.2+, strong cipher suites, and Forward Secrecy. This eliminates the need for any ATS exceptions in your app.
2.  **Avoid `NSAllowsArbitraryLoads`**: Seriously, do not use this in production. It defeats the entire purpose of ATS and exposes your users to unnecessary risks.
3.  **Use `NSExceptionDomains` Sparingly**: If you must make an exception, use `NSExceptionDomains` to target only the specific, non-compliant domains. Be as granular as possible.
4.  **Regularly Review `Info.plist`**: Periodically audit your `Info.plist` for any ATS exceptions. As backend services are updated, you might be able to remove old exceptions, further strengthening your app's security.
5.  **Educate Your Team**: Ensure all developers working on your project understand the importance of ATS and the implications of bypassing it.
6.  **Test Thoroughly**: Always test network connections on real devices and simulators with various configurations (including and excluding your ATS exceptions) to catch any unexpected behavior.

```
Info.plist
└─ NSAppTransportSecurity (Dictionary)
   ├─ NSAllowsArbitraryLoads (Boolean, NO by default, AVOID!)
   └─ NSExceptionDomains (Dictionary)
      └─ my.legacy.api.com (Dictionary)
         ├─ NSExceptionAllowsInsecureHTTPLoads (Boolean, YES if HTTP needed)
         ├─ NSExceptionMinimumTLSVersion (String, e.g., TLSv1.0)
         ├─ NSExceptionRequiresForwardSecrecy (Boolean, NO if not supported)
         └─ NSIncludesSubdomains (Boolean, YES for subdomains)
```

## Future of ATS

Apple's commitment to security is unwavering. While they haven't completely locked down ATS, their consistent encouragement to adopt secure connections suggests that future iOS versions might make it even harder to bypass ATS, possibly deprecating some of the exception keys. Staying ahead by securing your backend services is the most future-proof strategy.

## Summary

App Transport Security is a fundamental security feature on Apple platforms that protects user data by enforcing secure network connections. While it can sometimes pose challenges when integrating with older services, understanding its mechanisms and adhering to best practices—primarily using `NSExceptionDomains` sparingly and striving for secure backends—will ensure your app remains robust and trustworthy. Prioritize security, and your users will thank you.

Happy Swifting!
