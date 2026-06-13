---
title: Access Specifiers in Swift: A Complete Guide
date: 2025-06-13 10:00
description: Learn how Swift access control works — private, fileprivate, internal, public, and open — with practical examples, inheritance rules, and best practices for building maintainable iOS and macOS apps.
tags: Swift, iOS, Access Control, Development, Programming
---

# Access Specifiers in Swift: A Complete Guide

Every Swift project eventually grows beyond a single file. As your codebase expands, you need a way to decide **what code is visible where** — within a type, within a file, within a module, or to the outside world. That is exactly what **access control** (also called **access specifiers** or **access modifiers**) gives you.

Swift provides five access levels. Understanding them helps you write safer APIs, hide implementation details, and design modules that are easy to use and hard to misuse.

## Table of Contents

1. [Why Access Control Matters](#why-access-control-matters)
2. [The Five Access Levels](#the-five-access-levels)
3. [What You Can Apply Access Control To](#what-you-can-apply-access-control-to)
4. [Access Levels in Detail](#access-levels-in-detail)
5. [Inheritance and Overriding Rules](#inheritance-and-overriding-rules)
6. [Access Control in Extensions](#access-control-in-extensions)
7. [Asymmetric Getter and Setter Access](#asymmetric-getter-and-setter-access)
8. [Testing with `@testable import`](#testing-with-testable-import)
9. [Common Patterns and Best Practices](#common-patterns-and-best-practices)
10. [Quick Reference](#quick-reference)

## Why Access Control Matters

Without access control, every type, property, and method you write is potentially reachable from anywhere in your app. That leads to:

- **Tight coupling** — other parts of your code depend on details that should stay hidden
- **Harder refactoring** — changing an internal helper breaks code you did not expect to touch
- **Leaky APIs** — framework consumers use implementation types you never meant to expose

Access specifiers let you draw boundaries. You expose only what callers need and keep the rest private to your implementation.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 720 200" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Without vs with access control">
  <title>Without vs with access control</title>
  <rect x="10" y="20" width="330" height="160" rx="8" fill="#fff5f5" stroke="#e57373" stroke-width="2"/>
  <text x="175" y="48" text-anchor="middle" font-family="Futura, sans-serif" font-size="14" font-weight="bold" fill="#c62828">Without Access Control</text>
  <circle cx="80" cy="100" r="28" fill="#ef5350" opacity="0.9"/>
  <text x="80" y="105" text-anchor="middle" font-size="11" fill="#fff">View</text>
  <circle cx="175" cy="100" r="28" fill="#ef5350" opacity="0.9"/>
  <text x="175" y="105" text-anchor="middle" font-size="11" fill="#fff">VM</text>
  <circle cx="270" cy="100" r="28" fill="#ef5350" opacity="0.9"/>
  <text x="270" y="105" text-anchor="middle" font-size="11" fill="#fff">API</text>
  <line x1="108" y1="100" x2="147" y2="100" stroke="#c62828" stroke-width="2" marker-end="url(#arrowRed)"/>
  <line x1="203" y1="100" x2="242" y2="100" stroke="#c62828" stroke-width="2" marker-end="url(#arrowRed)"/>
  <text x="175" y="155" text-anchor="middle" font-size="11" fill="#666">Everything can reach everything</text>

  <rect x="380" y="20" width="330" height="160" rx="8" fill="#f1f8e9" stroke="#81c784" stroke-width="2"/>
  <text x="545" y="48" text-anchor="middle" font-family="Futura, sans-serif" font-size="14" font-weight="bold" fill="#2e7d32">With Access Control</text>
  <rect x="410" y="72" width="90" height="56" rx="6" fill="#66bb6a"/>
  <text x="455" y="105" text-anchor="middle" font-size="11" fill="#fff">View</text>
  <rect x="520" y="72" width="90" height="56" rx="6" fill="#43a047"/>
  <text x="565" y="105" text-anchor="middle" font-size="11" fill="#fff">VM</text>
  <rect x="630" y="72" width="60" height="56" rx="6" fill="#2e7d32"/>
  <text x="660" y="98" text-anchor="middle" font-size="10" fill="#fff">API</text>
  <text x="660" y="112" text-anchor="middle" font-size="9" fill="#fff">private</text>
  <line x1="500" y1="100" x2="520" y2="100" stroke="#2e7d32" stroke-width="2" marker-end="url(#arrowGreen)"/>
  <line x1="610" y1="100" x2="630" y2="100" stroke="#aaa" stroke-width="2" stroke-dasharray="5,4"/>
  <text x="545" y="155" text-anchor="middle" font-size="11" fill="#666">Only public API is exposed</text>

  <defs>
    <marker id="arrowRed" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 Z" fill="#c62828"/>
    </marker>
    <marker id="arrowGreen" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 Z" fill="#2e7d32"/>
    </marker>
  </defs>
</svg>
</div>

## The Five Access Levels

From **most restrictive** to **least restrictive**:

| Access Level   | Scope                                      | Typical Use |
|----------------|--------------------------------------------|-------------|
| `private`      | Enclosing declaration only                 | Implementation details inside a type |
| `fileprivate`  | Same source file                           | Helpers shared across types in one file |
| `internal`     | Same module (target) — **default**         | App-internal APIs |
| `public`       | Any module that imports yours              | Framework APIs (read-only outside module) |
| `open`         | Any module; allows subclassing/overriding  | Framework base classes meant to be extended |

Think of access levels as **concentric circles**. `private` is the smallest circle; `open` is the largest.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 520 520" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Concentric access level scopes">
  <title>Access level scopes from private to open</title>
  <circle cx="260" cy="260" r="240" fill="#e3f2fd" stroke="#1565c0" stroke-width="2"/>
  <text x="260" y="42" text-anchor="middle" font-family="Futura, sans-serif" font-size="15" font-weight="bold" fill="#1565c0">open</text>
  <text x="260" y="58" text-anchor="middle" font-size="11" fill="#555">Any module + subclass / override</text>

  <circle cx="260" cy="270" r="190" fill="#bbdefb" stroke="#1976d2" stroke-width="2"/>
  <text x="260" y="108" text-anchor="middle" font-family="Futura, sans-serif" font-size="15" font-weight="bold" fill="#1565c0">public</text>
  <text x="260" y="124" text-anchor="middle" font-size="11" fill="#555">Any module that imports yours</text>

  <circle cx="260" cy="280" r="140" fill="#90caf9" stroke="#1e88e5" stroke-width="2"/>
  <text x="260" y="168" text-anchor="middle" font-family="Futura, sans-serif" font-size="15" font-weight="bold" fill="#0d47a1">internal (default)</text>
  <text x="260" y="184" text-anchor="middle" font-size="11" fill="#333">Same module / target</text>

  <circle cx="260" cy="290" r="90" fill="#64b5f6" stroke="#2196f3" stroke-width="2"/>
  <text x="260" y="228" text-anchor="middle" font-family="Futura, sans-serif" font-size="14" font-weight="bold" fill="#fff">fileprivate</text>
  <text x="260" y="244" text-anchor="middle" font-size="10" fill="#fff">Same source file</text>

  <circle cx="260" cy="300" r="42" fill="#1565c0" stroke="#0d47a1" stroke-width="2"/>
  <text x="260" y="298" text-anchor="middle" font-family="Futura, sans-serif" font-size="13" font-weight="bold" fill="#fff">private</text>
  <text x="260" y="314" text-anchor="middle" font-size="9" fill="#e3f2fd">Enclosing type</text>

  <text x="260" y="500" text-anchor="middle" font-size="12" fill="#666">Each outer ring can see everything inside it</text>
</svg>
</div>

### Visibility Across Modules

When you split code into an **App target** and a **Framework**, access levels decide who can see what:

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 760 320" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Module visibility diagram">
  <title>What each module can access</title>

  <!-- Framework module -->
  <rect x="20" y="40" width="220" height="240" rx="10" fill="#fff3e0" stroke="#ef6c00" stroke-width="2"/>
  <text x="130" y="68" text-anchor="middle" font-family="Futura, sans-serif" font-size="14" font-weight="bold" fill="#e65100">MyFramework Module</text>
  <rect x="40" y="88" width="180" height="36" rx="4" fill="#ffb74d"/>
  <text x="130" y="111" text-anchor="middle" font-size="11" fill="#333">internal API</text>
  <rect x="40" y="134" width="180" height="36" rx="4" fill="#ff9800"/>
  <text x="130" y="157" text-anchor="middle" font-size="11" fill="#fff">public API</text>
  <rect x="40" y="180" width="180" height="36" rx="4" fill="#f57c00"/>
  <text x="130" y="203" text-anchor="middle" font-size="11" fill="#fff">open base class</text>
  <rect x="40" y="226" width="85" height="36" rx="4" fill="#bf360c"/>
  <text x="82" y="249" text-anchor="middle" font-size="10" fill="#fff">private</text>
  <rect x="135" y="226" width="85" height="36" rx="4" fill="#d84315"/>
  <text x="177" y="249" text-anchor="middle" font-size="10" fill="#fff">fileprivate</text>

  <!-- App module -->
  <rect x="270" y="40" width="220" height="240" rx="10" fill="#e8f5e9" stroke="#2e7d32" stroke-width="2"/>
  <text x="380" y="68" text-anchor="middle" font-family="Futura, sans-serif" font-size="14" font-weight="bold" fill="#1b5e20">MyApp Module</text>
  <rect x="290" y="100" width="180" height="36" rx="4" fill="#66bb6a"/>
  <text x="380" y="123" text-anchor="middle" font-size="11" fill="#fff">imports MyFramework</text>
  <text x="380" y="160" text-anchor="middle" font-size="11" fill="#333">✅ Can use public &amp; open</text>
  <text x="380" y="182" text-anchor="middle" font-size="11" fill="#333">❌ Cannot see internal</text>
  <text x="380" y="204" text-anchor="middle" font-size="11" fill="#333">❌ Cannot see private</text>
  <text x="380" y="240" text-anchor="middle" font-size="11" fill="#333">✅ Can subclass open only</text>

  <!-- External module -->
  <rect x="520" y="40" width="220" height="240" rx="10" fill="#fce4ec" stroke="#c2185b" stroke-width="2"/>
  <text x="630" y="68" text-anchor="middle" font-family="Futura, sans-serif" font-size="14" font-weight="bold" fill="#880e4f">Another App Module</text>
  <rect x="540" y="100" width="180" height="36" rx="4" fill="#f48fb1"/>
  <text x="630" y="123" text-anchor="middle" font-size="11" fill="#333">imports MyFramework</text>
  <text x="630" y="160" text-anchor="middle" font-size="11" fill="#333">✅ public types</text>
  <text x="630" y="182" text-anchor="middle" font-size="11" fill="#333">✅ open subclassing</text>
  <text x="630" y="204" text-anchor="middle" font-size="11" fill="#333">❌ MyApp internals</text>
  <text x="630" y="240" text-anchor="middle" font-size="11" fill="#333">❌ Framework internal</text>

  <!-- Arrows -->
  <line x1="240" y1="152" x2="270" y2="152" stroke="#555" stroke-width="2" marker-end="url(#arrowGray)"/>
  <line x1="240" y1="198" x2="270" y2="198" stroke="#555" stroke-width="2" marker-end="url(#arrowGray)"/>
  <line x1="490" y1="152" x2="520" y2="152" stroke="#555" stroke-width="2" marker-end="url(#arrowGray)"/>
  <line x1="490" y1="198" x2="520" y2="198" stroke="#555" stroke-width="2" marker-end="url(#arrowGray)"/>

  <defs>
    <marker id="arrowGray" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 Z" fill="#555"/>
    </marker>
  </defs>
</svg>
</div>

## What You Can Apply Access Control To

Access control applies to:

- Top-level types (`class`, `struct`, `enum`, `protocol`, `typealias`)
- Properties and constants
- Methods and subscripts
- Initializers
- Nested types

You place the keyword **before** the declaration:

```swift
public class NetworkClient {
    private let session: URLSession

    internal func fetchData() { }

    fileprivate var cache: [URL: Data] = [:]
}
```

If you omit an access modifier, Swift uses **`internal`** by default.

## Access Levels in Detail

### `private`

`private` limits visibility to the **enclosing declaration** and any **extensions of that declaration in the same file**.

```swift
class BankAccount {
    private var balance: Double = 0

    func deposit(_ amount: Double) {
        balance += amount
    }

    func withdraw(_ amount: Double) -> Bool {
        guard balance >= amount else { return false }
        balance -= amount
        return true
    }
}

let account = BankAccount()
// account.balance = 1000  // ❌ Error: 'balance' is inaccessible due to 'private' protection level
account.deposit(1000)        // ✅ Works — balance is modified through the type's API
```

Use `private` for:

- Stored properties that should not be mutated from outside
- Helper methods used only inside the type
- Details of an algorithm callers should not depend on

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 560 200" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="private scope within a type">
  <title>private access scope</title>
  <rect x="20" y="30" width="520" height="140" rx="10" fill="#f5f5f5" stroke="#999" stroke-width="2" stroke-dasharray="6,4"/>
  <text x="40" y="55" font-family="Futura, sans-serif" font-size="13" font-weight="bold" fill="#555">BankAccount.swift (same file)</text>

  <rect x="60" y="75" width="440" height="75" rx="8" fill="#1565c0" stroke="#0d47a1" stroke-width="2"/>
  <text x="80" y="98" font-family="Futura, sans-serif" font-size="13" font-weight="bold" fill="#fff">class BankAccount</text>
  <rect x="90" y="110" width="100" height="28" rx="4" fill="#ffcdd2" stroke="#c62828" stroke-width="1.5"/>
  <text x="140" y="129" text-anchor="middle" font-size="11" fill="#b71c1c">private balance</text>
  <rect x="210" y="110" width="80" height="28" rx="4" fill="#c8e6c9" stroke="#2e7d32" stroke-width="1.5"/>
  <text x="250" y="129" text-anchor="middle" font-size="11" fill="#1b5e20">deposit()</text>
  <rect x="310" y="110" width="80" height="28" rx="4" fill="#c8e6c9" stroke="#2e7d32" stroke-width="1.5"/>
  <text x="350" y="129" text-anchor="middle" font-size="11" fill="#1b5e20">withdraw()</text>

  <rect x="420" y="75" width="100" height="75" rx="8" fill="#fff" stroke="#c62828" stroke-width="2"/>
  <text x="470" y="108" text-anchor="middle" font-size="11" fill="#c62828">Outside</text>
  <text x="470" y="126" text-anchor="middle" font-size="11" fill="#c62828">caller</text>
  <text x="470" y="144" text-anchor="middle" font-size="10" fill="#c62828">❌ balance</text>

  <line x1="390" y1="124" x2="420" y2="124" stroke="#2e7d32" stroke-width="2" marker-end="url(#arrowGreen2)"/>
  <text x="405" y="118" font-size="9" fill="#2e7d32">✅ methods</text>

  <defs>
    <marker id="arrowGreen2" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 Z" fill="#2e7d32"/>
    </marker>
  </defs>
</svg>
</div>

### `fileprivate`

`fileprivate` is visible anywhere in the **same Swift source file**, even across different types.

```swift
// UserProfile.swift

struct UserProfile {
    fileprivate var displayName: String
}

struct ProfileFormatter {
    func format(_ profile: UserProfile) -> String {
        return "Hello, \(profile.displayName)"  // ✅ Same file
    }
}
```

Use `fileprivate` when:

- Two or more types in the same file need to share state
- You want tighter scope than `internal` but more flexibility than `private`

**Tip:** Prefer `private` when possible. Reach for `fileprivate` only when multiple types in one file genuinely need access.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 560 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="private vs fileprivate vs internal comparison">
  <title>Comparing private, fileprivate, and internal scope</title>

  <!-- private -->
  <rect x="10" y="20" width="170" height="180" rx="8" fill="#e3f2fd" stroke="#1565c0" stroke-width="2"/>
  <text x="95" y="45" text-anchor="middle" font-size="13" font-weight="bold" fill="#1565c0">private</text>
  <rect x="35" y="65" width="120" height="60" rx="6" fill="#1565c0"/>
  <text x="95" y="90" text-anchor="middle" font-size="11" fill="#fff">Type A</text>
  <text x="95" y="108" text-anchor="middle" font-size="10" fill="#bbdefb">member visible</text>
  <text x="95" y="150" text-anchor="middle" font-size="10" fill="#555">Scope: inside Type A</text>
  <text x="95" y="168" text-anchor="middle" font-size="10" fill="#555">+ same-file extension</text>

  <!-- fileprivate -->
  <rect x="195" y="20" width="170" height="180" rx="8" fill="#fff3e0" stroke="#ef6c00" stroke-width="2"/>
  <text x="280" y="45" text-anchor="middle" font-size="13" font-weight="bold" fill="#e65100">fileprivate</text>
  <rect x="210" y="60" width="140" height="110" rx="6" fill="#ffe0b2" stroke="#ef6c00" stroke-width="1.5" stroke-dasharray="4,3"/>
  <text x="280" y="78" text-anchor="middle" font-size="10" fill="#e65100">UserProfile.swift</text>
  <rect x="220" y="88" width="55" height="35" rx="4" fill="#ff9800"/>
  <text x="247" y="110" text-anchor="middle" font-size="10" fill="#fff">Type A</text>
  <rect x="285" y="88" width="55" height="35" rx="4" fill="#ff9800"/>
  <text x="312" y="110" text-anchor="middle" font-size="10" fill="#fff">Type B</text>
  <line x1="275" y1="105" x2="285" y2="105" stroke="#fff" stroke-width="2"/>
  <text x="280" y="150" text-anchor="middle" font-size="10" fill="#555">Scope: entire file</text>
  <text x="280" y="168" text-anchor="middle" font-size="10" fill="#555">Both types can share</text>

  <!-- internal -->
  <rect x="380" y="20" width="170" height="180" rx="8" fill="#e8f5e9" stroke="#2e7d32" stroke-width="2"/>
  <text x="465" y="45" text-anchor="middle" font-size="13" font-weight="bold" fill="#1b5e20">internal</text>
  <rect x="395" y="60" width="140" height="110" rx="6" fill="#c8e6c9" stroke="#2e7d32" stroke-width="1.5" stroke-dasharray="4,3"/>
  <text x="465" y="78" text-anchor="middle" font-size="10" fill="#1b5e20">MyApp Module</text>
  <rect x="405" y="92" width="40" height="30" rx="3" fill="#43a047"/>
  <text x="425" y="111" text-anchor="middle" font-size="9" fill="#fff">File1</text>
  <rect x="455" y="92" width="40" height="30" rx="3" fill="#43a047"/>
  <text x="475" y="111" text-anchor="middle" font-size="9" fill="#fff">File2</text>
  <rect x="505" y="92" width="40" height="30" rx="3" fill="#43a047"/>
  <text x="525" y="111" text-anchor="middle" font-size="9" fill="#fff">File3</text>
  <text x="465" y="150" text-anchor="middle" font-size="10" fill="#555">Scope: whole module</text>
  <text x="465" y="168" text-anchor="middle" font-size="10" fill="#555">Default access level</text>
</svg>
</div>

### `internal` (Default)

`internal` is visible anywhere in the **same module**. A module is typically an app target, framework, or Swift package.

```swift
// No keyword needed — internal is the default
class SessionManager {
    var currentUser: User?

    func logout() {
        currentUser = nil
    }
}
```

Everything in your app target can use `SessionManager`, but code in another framework cannot unless you mark it `public` or `open`.

Use `internal` for:

- Most app code
- Types and methods that are shared across your app but not meant for external consumers

### `public`

`public` makes a declaration visible to **any module that imports** yours. It is essential for Swift packages and frameworks.

```swift
public struct APIResponse<T: Decodable>: Decodable {
    public let data: T
    public let statusCode: Int

    public init(data: T, statusCode: Int) {
        self.data = data
        self.statusCode = statusCode
    }
}
```

Important rules for `public`:

- A `public` type's **members are still `internal` by default**
- You must explicitly mark members `public` if you want them accessible outside the module

```swift
public class Logger {
    var level: LogLevel = .info       // internal — not visible outside module
    public func log(_ message: String) { }  // visible outside module
}
```

Use `public` for:

- Framework and library APIs
- Types you ship in a Swift package

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 560 240" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="public type with internal members by default">
  <title>public type members default to internal</title>
  <rect x="80" y="30" width="400" height="180" rx="10" fill="#e3f2fd" stroke="#1565c0" stroke-width="2"/>
  <text x="280" y="58" text-anchor="middle" font-family="Futura, sans-serif" font-size="14" font-weight="bold" fill="#1565c0">public class Logger</text>

  <rect x="110" y="80" width="150" height="50" rx="6" fill="#fff9c4" stroke="#f9a825" stroke-width="2"/>
  <text x="185" y="102" text-anchor="middle" font-size="11" fill="#f57f17">var level</text>
  <text x="185" y="118" text-anchor="middle" font-size="10" fill="#666">internal (default)</text>
  <text x="185" y="148" text-anchor="middle" font-size="10" fill="#888">Hidden outside module</text>

  <rect x="300" y="80" width="150" height="50" rx="6" fill="#c8e6c9" stroke="#2e7d32" stroke-width="2"/>
  <text x="375" y="102" text-anchor="middle" font-size="11" fill="#1b5e20">public func log()</text>
  <text x="375" y="118" text-anchor="middle" font-size="10" fill="#666">explicitly public</text>
  <text x="375" y="148" text-anchor="middle" font-size="10" fill="#2e7d32">Visible to importers</text>

  <rect x="30" y="100" width="40" height="60" rx="4" fill="#ffcdd2" stroke="#c62828" stroke-width="1.5"/>
  <text x="50" y="125" text-anchor="middle" font-size="9" fill="#c62828">Other</text>
  <text x="50" y="138" text-anchor="middle" font-size="9" fill="#c62828">module</text>
  <text x="50" y="151" text-anchor="middle" font-size="9" fill="#c62828">❌ level</text>

  <rect x="490" y="100" width="40" height="60" rx="4" fill="#c8e6c9" stroke="#2e7d32" stroke-width="1.5"/>
  <text x="510" y="125" text-anchor="middle" font-size="9" fill="#1b5e20">Other</text>
  <text x="510" y="138" text-anchor="middle" font-size="9" fill="#1b5e20">module</text>
  <text x="510" y="151" text-anchor="middle" font-size="9" fill="#1b5e20">✅ log()</text>

  <line x1="70" y1="130" x2="110" y2="105" stroke="#aaa" stroke-width="1.5" stroke-dasharray="4,3"/>
  <line x1="450" y1="105" x2="490" y2="130" stroke="#2e7d32" stroke-width="2" marker-end="url(#arrowGreen3)"/>

  <defs>
    <marker id="arrowGreen3" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 Z" fill="#2e7d32"/>
    </marker>
  </defs>
</svg>
</div>

### `open`

`open` is like `public`, but it also allows **subclassing and overriding outside your module**.

```swift
open class BaseViewController: UIViewController {
    open func setupUI() {
        // Default layout
    }
}
```

Another module can do:

```swift
import MyUIKitHelpers

class HomeViewController: BaseViewController {
    override func setupUI() {
        super.setupUI()
        // Custom home screen layout
    }
}
```

With `public`, subclassing and overriding **outside the defining module** is **not** allowed.

Use `open` sparingly:

- Base classes in frameworks designed for extension (e.g. custom view controllers, parsers)
- When you explicitly want third-party subclasses

For most framework APIs, **`public` is enough** — it exposes the type without committing to an inheritance contract.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 620 280" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="public vs open inheritance comparison">
  <title>public vs open — subclassing from another module</title>

  <!-- public branch -->
  <rect x="20" y="20" width="280" height="240" rx="10" fill="#ffebee" stroke="#c62828" stroke-width="2"/>
  <text x="160" y="48" text-anchor="middle" font-size="14" font-weight="bold" fill="#c62828">public class BaseVC</text>
  <rect x="50" y="70" width="220" height="40" rx="6" fill="#ffcdd2"/>
  <text x="160" y="95" text-anchor="middle" font-size="11" fill="#b71c1c">public func setupUI()</text>
  <rect x="80" y="130" width="160" height="50" rx="6" fill="#fff" stroke="#c62828" stroke-width="2"/>
  <text x="160" y="152" text-anchor="middle" font-size="11" fill="#c62828">External Module</text>
  <text x="160" y="170" text-anchor="middle" font-size="10" fill="#c62828">❌ Cannot subclass</text>
  <text x="160" y="220" text-anchor="middle" font-size="10" fill="#666">Use when inheritance</text>
  <text x="160" y="236" text-anchor="middle" font-size="10" fill="#666">is not part of your API</text>

  <!-- open branch -->
  <rect x="320" y="20" width="280" height="240" rx="10" fill="#e8f5e9" stroke="#2e7d32" stroke-width="2"/>
  <text x="460" y="48" text-anchor="middle" font-size="14" font-weight="bold" fill="#1b5e20">open class BaseVC</text>
  <rect x="350" y="70" width="220" height="40" rx="6" fill="#c8e6c9"/>
  <text x="460" y="95" text-anchor="middle" font-size="11" fill="#1b5e20">open func setupUI()</text>
  <rect x="380" y="130" width="160" height="50" rx="6" fill="#fff" stroke="#2e7d32" stroke-width="2"/>
  <text x="460" y="152" text-anchor="middle" font-size="11" fill="#1b5e20">External Module</text>
  <text x="460" y="170" text-anchor="middle" font-size="10" fill="#2e7d32">✅ Can subclass &amp; override</text>
  <text x="460" y="220" text-anchor="middle" font-size="10" fill="#666">Use for framework</text>
  <text x="460" y="236" text-anchor="middle" font-size="10" fill="#666">extension points</text>
</svg>
</div>

## Inheritance and Overriding Rules

Access control interacts with inheritance in predictable ways:

1. **You cannot override with a more restrictive access level**
2. **`open` > `public` > `internal` > `fileprivate` > `private`** in terms of visibility
3. A subclass can override a method and make it **more accessible**, not less

```swift
class Animal {
    internal func makeSound() { print("...") }
}

class Dog: Animal {
    public override func makeSound() { print("Woof!") }  // ✅ More accessible
}
```

For framework design:

| Goal | Use |
|------|-----|
| Expose a type, no external subclassing | `public class` |
| Allow external subclassing and overriding | `open class` |
| Hide a type entirely outside the module | `internal` or lower |

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 520 200" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Override access level rules">
  <title>Override access must be equal or more permissive</title>
  <rect x="30" y="50" width="180" height="60" rx="8" fill="#90caf9" stroke="#1565c0" stroke-width="2"/>
  <text x="120" y="75" text-anchor="middle" font-size="12" font-weight="bold" fill="#0d47a1">Superclass</text>
  <text x="120" y="95" text-anchor="middle" font-size="11" fill="#333">internal func makeSound()</text>

  <line x1="210" y1="80" x2="260" y2="80" stroke="#555" stroke-width="2" marker-end="url(#arrowGray2)"/>
  <text x="235" y="72" text-anchor="middle" font-size="10" fill="#2e7d32">override ✅</text>

  <rect x="270" y="50" width="220" height="60" rx="8" fill="#c8e6c9" stroke="#2e7d32" stroke-width="2"/>
  <text x="380" y="75" text-anchor="middle" font-size="12" font-weight="bold" fill="#1b5e20">Subclass</text>
  <text x="380" y="95" text-anchor="middle" font-size="11" fill="#333">public override func makeSound()</text>

  <text x="260" y="145" text-anchor="middle" font-size="12" fill="#666">Rule: override access ≥ superclass access</text>
  <text x="260" y="165" text-anchor="middle" font-size="11" fill="#c62828">❌ Cannot override with private if superclass is internal</text>

  <defs>
    <marker id="arrowGray2" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 Z" fill="#555"/>
    </marker>
  </defs>
</svg>
</div>

## Access Control in Extensions

Extensions follow the same rules, with a few nuances:

- An extension can **lower** the effective access of members only within its own scope
- You can add `private` helpers in an extension in the same file as the type

```swift
class OrderService {
    func placeOrder(for product: Product) {
        validate(product)
        submit(product)
    }
}

private extension OrderService {
    func validate(_ product: Product) { /* ... */ }
    func submit(_ product: Product) { /* ... */ }
}
```

`private extension` is a popular pattern for grouping implementation details cleanly.

```
┌─────────────────────────────────────────────────────┐
│  OrderService.swift                                 │
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │  class OrderService                           │  │
│  │                                               │  │
│  │  placeOrder()  ──►  public API surface        │  │
│  └───────────────────────────────────────────────┘  │
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │  private extension OrderService               │  │
│  │                                               │  │
│  │  validate()  ──►  hidden implementation       │  │
│  │  submit()    ──►  hidden implementation       │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## Asymmetric Getter and Setter Access

Swift lets you give a property **different access levels** for reading and writing:

```swift
struct Temperature {
    private(set) var celsius: Double

    init(celsius: Double) {
        self.celsius = celsius
    }

    mutating func setCelsius(_ value: Double) {
        celsius = value
    }
}

let temp = Temperature(celsius: 25)
print(temp.celsius)   // ✅ Readable
// temp.celsius = 30  // ❌ Cannot assign — setter is private
```

Common combinations:

```swift
public private(set) var items: [Item] = []   // Public read, private write
internal private(set) var cache: Data?       // Module read, private write
```

This pattern is ideal for **read-only public APIs** backed by mutable internal state.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 560 200" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Asymmetric getter and setter access">
  <title>private(set) — different read and write access</title>
  <rect x="180" y="60" width="200" height="70" rx="8" fill="#1565c0" stroke="#0d47a1" stroke-width="2"/>
  <text x="280" y="88" text-anchor="middle" font-size="13" font-weight="bold" fill="#fff">var celsius</text>
  <text x="280" y="108" text-anchor="middle" font-size="11" fill="#bbdefb">private(set)</text>

  <rect x="40" y="50" width="120" height="90" rx="8" fill="#c8e6c9" stroke="#2e7d32" stroke-width="2"/>
  <text x="100" y="78" text-anchor="middle" font-size="12" font-weight="bold" fill="#1b5e20">Getter</text>
  <text x="100" y="98" text-anchor="middle" font-size="11" fill="#333">internal / public</text>
  <text x="100" y="118" text-anchor="middle" font-size="11" fill="#2e7d32">✅ Anyone can read</text>

  <rect x="400" y="50" width="120" height="90" rx="8" fill="#ffcdd2" stroke="#c62828" stroke-width="2"/>
  <text x="460" y="78" text-anchor="middle" font-size="12" font-weight="bold" fill="#c62828">Setter</text>
  <text x="460" y="98" text-anchor="middle" font-size="11" fill="#333">private</text>
  <text x="460" y="118" text-anchor="middle" font-size="11" fill="#c62828">❌ External write</text>

  <line x1="160" y1="95" x2="180" y2="95" stroke="#2e7d32" stroke-width="2" marker-end="url(#arrowGreen4)"/>
  <line x1="380" y1="95" x2="400" y2="95" stroke="#c62828" stroke-width="2" stroke-dasharray="5,4" marker-end="url(#arrowRed2)"/>
  <text x="280" y="165" text-anchor="middle" font-size="12" fill="#666">Controlled mutation — only the type itself can assign</text>

  <defs>
    <marker id="arrowGreen4" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 Z" fill="#2e7d32"/>
    </marker>
    <marker id="arrowRed2" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 Z" fill="#c62828"/>
    </marker>
  </defs>
</svg>
</div>

## Testing with `@testable import`

Unit tests live in a separate module (test target). By default, `internal` members are invisible to tests. Use `@testable import`:

```swift
@testable import MyApp

final class OrderServiceTests: XCTestCase {
    func testPlaceOrder() {
        let service = OrderService()
        // Can access internal members of MyApp
    }
}
```

Notes:

- `@testable import` exposes **`internal`** members only
- It does **not** expose `private` or `fileprivate` members
- Design testable code by keeping test-critical logic at `internal` or by injecting dependencies

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 620 260" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="What testable import exposes">
  <title>@testable import visibility</title>

  <rect x="30" y="40" width="260" height="200" rx="10" fill="#e3f2fd" stroke="#1565c0" stroke-width="2"/>
  <text x="160" y="68" text-anchor="middle" font-size="14" font-weight="bold" fill="#1565c0">MyApp Target</text>
  <rect x="50" y="88" width="100" height="32" rx="4" fill="#ffcdd2"/>
  <text x="100" y="108" text-anchor="middle" font-size="10" fill="#b71c1c">private</text>
  <rect x="170" y="88" width="100" height="32" rx="4" fill="#ffe0b2"/>
  <text x="220" y="108" text-anchor="middle" font-size="10" fill="#e65100">fileprivate</text>
  <rect x="50" y="132" width="220" height="32" rx="4" fill="#fff9c4"/>
  <text x="160" y="152" text-anchor="middle" font-size="10" fill="#f57f17">internal  ← exposed to tests</text>
  <rect x="50" y="176" width="220" height="32" rx="4" fill="#c8e6c9"/>
  <text x="160" y="196" text-anchor="middle" font-size="10" fill="#1b5e20">public / open</text>

  <line x1="290" y1="140" x2="330" y2="140" stroke="#555" stroke-width="2" marker-end="url(#arrowGray3)"/>
  <text x="310" y="130" text-anchor="middle" font-size="9" fill="#555">@testable</text>
  <text x="310" y="158" text-anchor="middle" font-size="9" fill="#555">import</text>

  <rect x="340" y="40" width="250" height="200" rx="10" fill="#f3e5f5" stroke="#7b1fa2" stroke-width="2"/>
  <text x="465" y="68" text-anchor="middle" font-size="14" font-weight="bold" fill="#6a1b9a">MyAppTests Target</text>
  <text x="465" y="110" text-anchor="middle" font-size="11" fill="#c62828">❌ private — blocked</text>
  <text x="465" y="134" text-anchor="middle" font-size="11" fill="#c62828">❌ fileprivate — blocked</text>
  <text x="465" y="158" text-anchor="middle" font-size="11" fill="#2e7d32">✅ internal — accessible</text>
  <text x="465" y="182" text-anchor="middle" font-size="11" fill="#2e7d32">✅ public — accessible</text>
  <text x="465" y="215" text-anchor="middle" font-size="10" fill="#666">Separate module, special import</text>

  <defs>
    <marker id="arrowGray3" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 Z" fill="#555"/>
    </marker>
  </defs>
</svg>
</div>

## Common Patterns and Best Practices

### 1. Start Restrictive, Loosen When Needed

Default to `private`, then widen access only when another type genuinely needs it. It is easier to expose an API later than to hide one callers already depend on.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 560 120" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Decision flow for choosing access level">
  <title>Which access level should I use?</title>
  <rect x="10" y="40" width="100" height="40" rx="20" fill="#1565c0"/>
  <text x="60" y="65" text-anchor="middle" font-size="11" fill="#fff">Start</text>
  <line x1="110" y1="60" x2="140" y2="60" stroke="#555" stroke-width="2" marker-end="url(#arrowGray4)"/>

  <rect x="140" y="30" width="120" height="60" rx="6" fill="#e3f2fd" stroke="#1565c0" stroke-width="1.5"/>
  <text x="200" y="55" text-anchor="middle" font-size="10" fill="#333">Only this type</text>
  <text x="200" y="72" text-anchor="middle" font-size="10" font-weight="bold" fill="#1565c0">→ private</text>

  <line x1="260" y1="60" x2="290" y2="60" stroke="#555" stroke-width="2" marker-end="url(#arrowGray4)"/>
  <rect x="290" y="30" width="120" height="60" rx="6" fill="#fff3e0" stroke="#ef6c00" stroke-width="1.5"/>
  <text x="350" y="55" text-anchor="middle" font-size="10" fill="#333">Same file only</text>
  <text x="350" y="72" text-anchor="middle" font-size="10" font-weight="bold" fill="#e65100">→ fileprivate</text>

  <line x1="410" y1="60" x2="440" y2="60" stroke="#555" stroke-width="2" marker-end="url(#arrowGray4)"/>
  <rect x="440" y="22" width="110" height="76" rx="6" fill="#e8f5e9" stroke="#2e7d32" stroke-width="1.5"/>
  <text x="495" y="48" text-anchor="middle" font-size="10" fill="#333">App / module</text>
  <text x="495" y="65" text-anchor="middle" font-size="10" font-weight="bold" fill="#1b5e20">→ internal</text>
  <text x="495" y="82" text-anchor="middle" font-size="9" fill="#333">Framework API</text>
  <text x="495" y="94" text-anchor="middle" font-size="9" font-weight="bold" fill="#1565c0">→ public / open</text>

  <defs>
    <marker id="arrowGray4" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 Z" fill="#555"/>
    </marker>
  </defs>
</svg>
</div>

### 2. Use `private(set)` for Controlled State

```swift
class ViewModel {
    private(set) var isLoading = false

    func loadData() async {
        isLoading = true
        defer { isLoading = false }
        // fetch...
    }
}
```

### 3. Mark Framework Surface Area Explicitly

In a Swift package, be deliberate:

```swift
public protocol NetworkServiceProtocol {
    func request<T: Decodable>(_ endpoint: Endpoint) async throws -> T
}

public final class NetworkService: NetworkServiceProtocol {
    public init(session: URLSession = .shared) { /* ... */ }
    public func request<T: Decodable>(_ endpoint: Endpoint) async throws -> T { /* ... */ }
}
```

### 4. Avoid `open` Unless You Mean It

`open` is a long-term contract. Subclasses outside your module can override behavior you may change in future releases. Prefer `public` plus composition or protocols when possible.

### 5. Keep Files Focused to Reduce `fileprivate` Sprawl

If you find yourself using `fileprivate` heavily, consider whether types belong in the same file or whether a clearer API boundary would help.

## Quick Reference

```swift
// Most common app code — default internal
class UserRepository { }

// Hide implementation
private func normalizeEmail(_ email: String) -> String { }

// Share within one file
fileprivate struct InternalDTO { }

// Framework API
public struct Config {
    public let baseURL: URL
    public init(baseURL: URL) { self.baseURL = baseURL }
}

// Framework base class for subclassing
open class Plugin {
    open func execute() { }
}

// Read-only outside, writable inside
public private(set) var version: String = "1.0.0"
```

## Summary

Swift access specifiers help you control visibility at five levels:

- **`private`** — inside the type (and same-file extensions)
- **`fileprivate`** — inside the source file
- **`internal`** — inside the module (default)
- **`public`** — visible to importers; no external subclassing
- **`open`** — visible to importers; allows external subclassing and overriding

Used well, access control keeps your code modular, your APIs clean, and your refactoring safe. When in doubt, start with `private` or `internal`, expose only what is necessary, and use `public` / `open` deliberately in frameworks and packages.

Happy Swifting!
