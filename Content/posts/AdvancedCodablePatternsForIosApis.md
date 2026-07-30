---
title: Advanced Codable Patterns for iOS APIs
date: 2026-07-30 11:00
description: Explore advanced Codable patterns for iOS APIs
tags: Swift, Networking, iOS
---

# Advanced Codable Patterns for iOS APIs

As iOS developers, we often work with external APIs to fetch data for our apps. The `Codable` protocol in Swift provides an easy way to encode and decode data to and from JSON. However, when dealing with complex APIs, we may need to use more advanced patterns to handle the data. In this article, we will explore some of these patterns and learn how to use them effectively.

## Introduction to Codable

The `Codable` protocol is a combination of the `Encodable` and `Decodable` protocols. It allows us to encode and decode data to and from external formats like JSON. To use `Codable`, we need to conform our data structures to the protocol and provide a way to encode and decode the data.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Codable Protocol">
  <title>Codable Protocol</title>
  <rect x="50" y="50" width="100" height="50" fill="#2A8367" rx="10"/>
  <text x="100" y="90" text-anchor="middle" fill="#ffffff" font-size="18">Codable</text>
  <line x1="150" y1="90" x2="250" y2="90" stroke="#000000" stroke-width="2"/>
  <rect x="250" y="50" width="100" height="50" fill="#F04B3E" rx="10"/>
  <text x="300" y="90" text-anchor="middle" fill="#ffffff" font-size="18">Encodable</text>
  <line x1="350" y1="90" x2="450" y2="90" stroke="#000000" stroke-width="2"/>
  <rect x="450" y="50" width="100" height="50" fill="#1565c0" rx="10"/>
  <text x="500" y="90" text-anchor="middle" fill="#ffffff" font-size="18">Decodable</text>
</svg>
</div>

## Nested Codable Structures

When dealing with complex APIs, we often encounter nested data structures. To handle these structures, we can use nested `Codable` conformances. For example, let's say we have an API that returns a list of users, and each user has a nested address object.

```swift
struct User: Codable {
    let id: Int
    let name: String
    let address: Address
}

struct Address: Codable {
    let street: String
    let city: String
    let state: String
    let zip: String
}
```

In this example, the `User` struct has a nested `Address` struct. Both structs conform to the `Codable` protocol, which allows us to encode and decode the data easily.

## Custom Codable Keys

Sometimes, the API may use different key names than our Swift structs. To handle this, we can use custom `Codable` keys. For example, let's say the API uses the key "first_name" instead of "firstName".

```swift
struct User: Codable {
    let id: Int
    let firstName: String
    let lastName: String
    
    enum CodingKeys: String, CodingKey {
        case id
        case firstName = "first_name"
        case lastName
    }
}
```

In this example, we define a custom `CodingKeys` enum that maps the Swift property names to the API key names.

## Advanced Codable Patterns

There are many other advanced `Codable` patterns that we can use to handle complex APIs. For example, we can use `Codable` arrays, dictionaries, and sets to handle collections of data.

```swift
struct User: Codable {
    let id: Int
    let name: String
    let friends: [User]
}

struct Group: Codable {
    let id: Int
    let name: String
    let users: [String: User]
}
```

In this example, the `User` struct has an array of `User` objects, and the `Group` struct has a dictionary of `User` objects.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Advanced Codable Patterns">
  <title>Advanced Codable Patterns</title>
  <rect x="50" y="50" width="100" height="50" fill="#2A8367" rx="10"/>
  <text x="100" y="90" text-anchor="middle" fill="#ffffff" font-size="18">Arrays</text>
  <line x1="150" y1="90" x2="250" y2="90" stroke="#000000" stroke-width="2"/>
  <rect x="250" y="50" width="100" height="50" fill="#F04B3E" rx="10"/>
  <text x="300" y="90" text-anchor="middle" fill="#ffffff" font-size="18">Dictionaries</text>
  <line x1="350" y1="90" x2="450" y2="90" stroke="#000000" stroke-width="2"/>
  <rect x="450" y="50" width="100" height="50" fill="#1565c0" rx="10"/>
  <text x="500" y="90" text-anchor="middle" fill="#ffffff" font-size="18">Sets</text>
</svg>
</div>

## Real-World Example

Let's say we have an API that returns a list of posts, and each post has a nested user object and a list of comments.

```swift
struct Post: Codable {
    let id: Int
    let title: String
    let user: User
    let comments: [Comment]
}

struct User: Codable {
    let id: Int
    let name: String
}

struct Comment: Codable {
    let id: Int
    let text: String
    let user: User
}
```

In this example, the `Post` struct has a nested `User` object and a list of `Comment` objects. The `Comment` struct also has a nested `User` object.

```
┌─────────────┐     ┌─────────────┐
│   Post     │ ──► │  User      │
└─────────────┘     └─────────────┘
       │               │
       │               │
       │               │
       │               │
       │               │
       └───────┬───────┘
               │
               │
               │
               │
               │
               │
               v
       ┌─────────────┐
       │  Comments  │
       └─────────────┘
               │
               │
               │
               │
               │
               │
               v
       ┌─────────────┐
       │  Comment   │
       └─────────────┘
               │
               │
               │
               │
               │
               │
               v
       ┌─────────────┐
       │  User      │
       └─────────────┘
```

## Summary

In this article, we explored advanced `Codable` patterns for iOS APIs. We learned how to use nested `Codable` structures, custom `Codable` keys, and advanced `Codable` patterns like arrays, dictionaries, and sets. We also saw a real-world example of using `Codable` to handle complex API data.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Codable Patterns Comparison">
  <title>Codable Patterns Comparison</title>
  <rect x="50" y="50" width="100" height="50" fill="#2A8367" rx="10"/>
  <text x="100" y="90" text-anchor="middle" fill="#ffffff" font-size="18">Nested</text>
  <line x1="150" y1="90" x2="250" y2="90" stroke="#000000" stroke-width="2"/>
  <rect x="250" y="50" width="100" height="50" fill="#F04B3E" rx="10"/>
  <text x="300" y="90" text-anchor="middle" fill="#ffffff" font-size="18">Custom Keys</text>
  <line x1="350" y1="90" x2="450" y2="90" stroke="#000000" stroke-width="2"/>
  <rect x="450" y="50" width="100" height="50" fill="#1565c0" rx="10"/>
  <text x="500" y="90" text-anchor="middle" fill="#ffffff" font-size="18">Advanced</text>
</svg>
</div>

Happy Swifting!
