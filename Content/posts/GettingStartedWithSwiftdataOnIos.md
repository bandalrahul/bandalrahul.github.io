---
title: Getting Started with SwiftData on iOS
date: 2026-07-27 12:14
description: Learn how to integrate SwiftData into your iOS applications, from defining models to fetching and persisting data efficiently.
tags: SwiftData, iOS, Development
---

# Getting Started with SwiftData on iOS

Data persistence is a cornerstone of almost every non-trivial iOS application. For years, Core Data has been Apple's robust framework for managing object graphs and persisting them to disk. While powerful, Core Data has historically carried a reputation for a steep learning curve, especially for developers new to its intricacies.

Enter SwiftData. Introduced at WWDC23, SwiftData is a modern, Swift-native persistence framework built on top of Core Data, but designed to be significantly easier and more intuitive to use. It leverages Swift's powerful macro system and SwiftUI's declarative nature to provide a seamless experience for defining models, storing them, and fetching them in your applications. If you've ever wished for a simpler way to handle local data storage without sacrificing power, SwiftData is here to answer that call.

In this article, we'll embark on a journey to get started with SwiftData. We'll cover everything from defining your data models using the new `@Model` macro to setting up your application's data stack, performing basic CRUD (Create, Read, Update, Delete) operations, and integrating it elegantly into your SwiftUI views. By the end, you'll have a solid foundation to build data-driven iOS applications with SwiftData.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="SwiftData Core Components Overview">
  <title>SwiftData Core Components Overview</title>

  <!-- Background for clarity -->
  <rect x="0" y="0" width="600" height="220" fill="#f8f8f8" />

  <!-- Boxes -->
  <rect x="50" y="50" width="120" height="60" rx="10" ry="10" fill="#2A8367" stroke="#1c5e47" stroke-width="2"/>
  <text x="110" y="85" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">@Model</text>
  <text x="110" y="105" font-family="Arial, sans-serif" font-size="12" fill="white" text-anchor="middle">(Data Definition)</text>

  <rect x="240" y="50" width="120" height="60" rx="10" ry="10" fill="#1565c0" stroke="#0e4a8c" stroke-width="2"/>
  <text x="300" y="85" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">ModelContainer</text>
  <text x="300" y="105" font-family="Arial, sans-serif" font-size="12" fill="white" text-anchor="middle">(Storage Setup)</text>

  <rect x="430" y="50" width="120" height="60" rx="10" ry="10" fill="#F04B3E" stroke="#b3382e" stroke-width="2"/>
  <text x="490" y="85" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">ModelContext</text>
  <text x="490" y="105" font-family="Arial, sans-serif" font-size="12" fill="white" text-anchor="middle">(CRUD Operations)</text>

  <rect x="240" y="140" width="120" height="60" rx="10" ry="10" fill="#2A8367" stroke="#1c5e47" stroke-width="2"/>
  <text x="300" y="175" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">@Query</text>
  <text x="300" y="195" font-family="Arial, sans-serif" font-size="12" fill="white" text-anchor="middle">(Data Fetching)</text>

  <!-- Arrows and labels -->
  <line x1="170" y1="80" x2="240" y2="80" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="205" y="70" font-family="Arial, sans-serif" font-size="12" fill="#333" text-anchor="middle">Configures</text>

  <line x1="360" y1="80" x2="430" y2="80" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="395" y="70" font-family="Arial, sans-serif" font-size="12" fill="#333" text-anchor="middle">Manages</text>

  <line x1="300" y1="110" x2="300" y2="140" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="310" y="125" font-family="Arial, sans-serif" font-size="12" fill="#333" text-anchor="start">Provides Data</text>

  <line x1="430" y1="170" x2="360" y2="170" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="395" y="180" font-family="Arial, sans-serif" font-size="12" fill="#333" text-anchor="middle">Fetches via</text>

  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
    </marker>
  </defs>
</svg>
</div>

## Defining Your Data Model with `@Model`

The first step in using SwiftData is to define your data models. Gone are the days of creating `NSManagedObject` subclasses and manually managing properties. With SwiftData, you simply define a Swift class and adorn it with the `@Model` macro.

Let's imagine we're building a simple to-do list app. We'll need a `TodoItem` model:

```swift
import Foundation
import SwiftData

@Model
final class TodoItem {
    var task: String
    var isComplete: Bool
    var timestamp: Date

    init(task: String, isComplete: Bool = false, timestamp: Date = .now) {
        self.task = task
        self.isComplete = isComplete
        self.timestamp = timestamp
    }
}
```

That's it! By adding `@Model`, SwiftData automatically handles the underlying Core Data entity generation, property mapping, and other boilerplate. Your class must be `final` and inherit from `NSObject` implicitly if it's a class (which `@Model` handles). All stored properties that are `var` become managed properties. Properties that are `let` or `private(set)` will not be persisted unless explicitly handled otherwise.

SwiftData models automatically conform to `Identifiable` (using an internal `PersistentIdentifier`), `Codable`, and `Equatable`. This makes them incredibly easy to use within SwiftUI views, especially with `ForEach`.

### Relationships

SwiftData also makes defining relationships between models straightforward. Let's say our `TodoItem` can belong to a `TodoList`:

```swift
@Model
final class TodoList {
    var title: String
    @Relationship(deleteRule: .cascade, inverse: \TodoItem.list)
    var items: [TodoItem]?

    init(title: String, items: [TodoItem]? = nil) {
        self.title = title
        self.items = items
    }
}

@Model
final class TodoItem {
    var task: String
    var isComplete: Bool
    var timestamp: Date
    var list: TodoList? // Optional, a TodoItem might not be in a list

    init(task: String, isComplete: Bool = false, timestamp: Date = .now, list: TodoList? = nil) {
        self.task = task
        self.isComplete = isComplete
        self.timestamp = timestamp
        self.list = list
    }
}
```

Here, `@Relationship` is used to define the one-to-many relationship.
- `deleteRule: .cascade` means if a `TodoList` is deleted, all its associated `TodoItem`s will also be deleted. Other options include `.nullify`, `.deny`, and `.noAction`.
- `inverse: \TodoItem.list` specifies the inverse relationship. This is crucial for maintaining data integrity and performance in SwiftData. It tells SwiftData that the `items` property of `TodoList` is the inverse of the `list` property on `TodoItem`.

## Setting Up the Model Container

Once your models are defined, you need to tell your application where and how to store them. This is done using a `ModelContainer`. The `ModelContainer` is responsible for managing the underlying persistent store (e.g., SQLite database).

The easiest way to set up `ModelContainer` in a SwiftUI app is using the `modelContainer(for:)` view modifier in your `App` struct:

```swift
import SwiftUI
import SwiftData

@main
struct TodoApp: App {
    var body: some Scene {
        WindowGroup {
            TodoListView()
        }
        .modelContainer(for: TodoItem.self) // Register TodoItem
        // .modelContainer(for: [TodoItem.self, TodoList.self]) // Register multiple models
    }
}
```

By adding `.modelContainer(for: TodoItem.self)`, you're instructing SwiftData to create a default `ModelContainer` that can manage `TodoItem` instances. It will automatically create an SQLite database file in your app's default storage location.

If you need more control, such as storing data in memory for testing or specifying a custom file URL, you can provide a `ModelConfiguration`:

```swift
@main
struct TodoApp: App {
    var body: some Scene {
        WindowGroup {
            TodoListView()
        }
        .modelContainer(for: TodoItem.self, is  InMemory: false) // Explicitly specify not in memory
    }
}
```

Or, for multiple models and more advanced configurations:

```swift
@main
struct TodoApp: App {
    var sharedModelContainer: ModelContainer = {
        let schema = Schema([
            TodoItem.self,
            TodoList.self,
        ])
        let modelConfiguration = ModelConfiguration(schema: schema, isStoredInMemoryOnly: false)

        do {
            return try ModelContainer(for: schema, configurations: [modelConfiguration])
        } catch {
            fatalError("Could not create ModelContainer: \(error)")
        }
    }()

    var body: some Scene {
        WindowGroup {
            TodoListView()
        }
        .modelContainer(sharedModelContainer)
    }
}
```
This setup ensures that all views within the `WindowGroup` have access to the `ModelContainer` and, consequently, a `ModelContext`.

## Interacting with Data: ModelContext

The `ModelContext` is your primary interface for interacting with your SwiftData store. Think of it as a scratchpad where you can create, modify, and delete your model objects. Changes made within a `ModelContext` are not permanently saved until the context's changes are committed to the `ModelContainer`.

You can access the `ModelContext` in any SwiftUI view that's part of a `WindowGroup` managed by a `ModelContainer` using the `@Environment` property wrapper:

```swift
import SwiftUI
import SwiftData

struct TodoListView: View {
    @Environment(\.modelContext) private var modelContext

    // ... rest of your view
}
```

### Creating and Inserting Data

To create a new `TodoItem` and save it, you instantiate the item and then insert it into the `modelContext`:

```swift
func addTodoItem(task: String) {
    let newItem = TodoItem(task: task)
    modelContext.insert(newItem)
    // SwiftData automatically saves changes periodically,
    // or you can explicitly save:
    // try? modelContext.save()
}
```

### Fetching Data with `@Query`

Fetching data is incredibly simple with the `@Query` property wrapper. It acts like a live query, automatically updating your SwiftUI view whenever the underlying data changes.

```swift
struct TodoListView: View {
    @Environment(\.modelContext) private var modelContext
    @Query(sort: \TodoItem.timestamp, order: .reverse) private var todoItems: [TodoItem]

    var body: some View {
        NavigationView {
            List {
                ForEach(todoItems) { item in
                    Text(item.task)
                }
            }
            .navigationTitle("My Todos")
        }
    }
}
```

The `@Query` property wrapper automatically observes changes in the `modelContext` and updates `todoItems` accordingly. You can customize the query with `sort` parameters and `Predicate` for filtering.

#### Filtering with `#Predicate`

SwiftData introduces `#Predicate` for type-safe filtering, making queries much more robust than string-based `NSPredicate`s.

```swift
// Fetch only incomplete items
@Query(filter: #Predicate<TodoItem> { !$0.isComplete }, sort: \TodoItem.timestamp)
private var incompleteTodoItems: [TodoItem]

// Fetch items containing a specific string
@Query(filter: #Predicate<TodoItem> { $0.task.contains("SwiftData") })
private var swiftDataTasks: [TodoItem]
```

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 250" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="SwiftData Data Flow Diagram">
  <title>SwiftData Data Flow Diagram</title>

  <!-- Background for clarity -->
  <rect x="0" y="0" width="600" height="250" fill="#f8f8f8" />

  <!-- Boxes -->
  <rect x="50" y="50" width="100" height="50" rx="10" ry="10" fill="#2A8367" stroke="#1c5e47" stroke-width="2"/>
  <text x="100" y="80" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">SwiftUI View</text>

  <rect x="200" y="50" width="100" height="50" rx="10" ry="10" fill="#F04B3E" stroke="#b3382e" stroke-width="2"/>
  <text x="250" y="80" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">ModelContext</text>

  <rect x="350" y="50" width="100" height="50" rx="10" ry="10" fill="#1565c0" stroke="#0e4a8c" stroke-width="2"/>
  <text x="400" y="80" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">ModelContainer</text>

  <rect x="500" y="50" width="80" height="50" rx="10" ry="10" fill="#333" stroke="#111" stroke-width="2"/>
  <text x="540" y="80" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">Storage</text>
  <text x="540" y="95" font-family="Arial, sans-serif" font-size="10" fill="white" text-anchor="middle">(SQLite)</text>

  <!-- Arrows for Data Operations -->
  <line x1="150" y1="75" x2="200" y2="75" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="175" y="65" font-family="Arial, sans-serif" font-size="12" fill="#333" text-anchor="middle">Request</text>

  <line x1="300" y1="75" x2="350" y2="75" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="325" y="65" font-family="Arial, sans-serif" font-size="12" fill="#333" text-anchor="middle">Commits</text>

  <line x1="450" y1="75" x2="500" y2="75" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="475" y="65" font-family="Arial, sans-serif" font-size="12" fill="#333" text-anchor="middle">Persists</text>

  <!-- Arrows for Data Fetching -->
  <line x1="500" y1="100" x2="450" y2="130" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <line x1="450" y1="130" x2="350" y2="130" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <line x1="350" y1="130" x2="300" y2="160" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <line x1="300" y1="160" x2="150" y2="160" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="325" y="145" font-family="Arial, sans-serif" font-size="12" fill="#333" text-anchor="middle">Notifies</text>
  <text x="225" y="150" font-family="Arial, sans-serif" font-size="12" fill="#333" text-anchor="middle">Updates UI</text>

  <!-- Labels for actions -->
  <text x="175" y="110" font-family="Arial, sans-serif" font-size="12" fill="#F04B3E" text-anchor="middle">Create/Update/Delete</text>
  <text x="175" y="130" font-family="Arial, sans-serif" font-size="12" fill="#2A8367" text-anchor="middle">@Query Fetch</text>

  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
    </marker>
  </defs>
</svg>
</div>

### Updating Data

Updating a SwiftData model is as simple as modifying its properties. When you access a `@Model` instance within a `View`, it's recommended to use the `@Bindable` property wrapper for two-way binding with UI elements like `TextField` or `Toggle`. This wrapper ensures that any changes to the model's properties are observed and automatically saved by the `ModelContext`.

```swift
struct TodoDetailView: View {
    @Bindable var item: TodoItem // Use @Bindable for two-way binding
    @Environment(\.modelContext) private var modelContext

    var body: some View {
        Form {
            TextField("Task", text: $item.task)
            Toggle("Complete", isOn: $item.isComplete)
            Text("Created: \(item.timestamp, formatter: DateFormatter.shortDateTime)")
        }
        .navigationTitle("Edit Todo")
        .navigationBarTitleDisplayMode(.inline)
    }
}

extension DateFormatter {
    static let shortDateTime: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateStyle = .short
        formatter.timeStyle = .short
        return formatter
    }()
}
```

Any changes made to `item.task` or `item.isComplete` will be automatically tracked by the `modelContext`.

### Deleting Data

To delete a `TodoItem`, you use the `delete(_:)` method of the `modelContext`:

```swift
struct TodoListView: View {
    @Environment(\.modelContext) private var modelContext
    @Query(sort: \TodoItem.timestamp, order: .reverse) private var todoItems: [TodoItem]

    var body: some View {
        NavigationView {
            List {
                ForEach(todoItems) { item in
                    Text(item.task)
                }
                .onDelete(perform: deleteItems)
            }
            .navigationTitle("My Todos")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    EditButton()
                }
                ToolbarItem {
                    Button("Add") {
                        addTodoItem()
                    }
                }
            }
        }
    }

    private func addTodoItem() {
        let newItem = TodoItem(task: "New Task \(Date.now.formatted(date: .omitted, time: .standard))")
        modelContext.insert(newItem)
    }

    private func deleteItems(offsets: IndexSet) {
        for index in offsets {
            let item = todoItems[index]
            modelContext.delete(item)
        }
    }
}
```

This typical SwiftUI `.onDelete` pattern integrates seamlessly with SwiftData.

## Data Flow in a SwiftData App

To summarize the interaction between your SwiftUI views, the `ModelContext`, and the `ModelContainer`, consider this simplified flow:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  SwiftUI View   │ ──► │   ModelContext  │ ──► │  ModelContainer │
│                 │     │ (Scratchpad)    │     │ (Persistence)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         ▲                       │                       │
         │                       │                       │
         └─────────── @Query ───┴─────────── Saves/Loads ┴─────────► Storage (e.g., SQLite)
           (Live Data)
```

1.  **SwiftUI View** initiates an action (e.g., button tap, text field edit).
2.  The action calls a method that uses the **`ModelContext`** to perform an `insert`, `update`, or `delete` operation on a `@Model` object.
3.  The `ModelContext` tracks these changes. Periodically, or when explicitly requested, it commits these changes to the **`ModelContainer`**.
4.  The `ModelContainer` then handles persisting these changes to the **Storage** (e.g., an SQLite database file).
5.  Concurrently, the **`@Query`** property wrapper in your SwiftUI views observes changes in the `ModelContext`. When data relevant to its query changes, it automatically re-fetches and updates the view, ensuring your UI always reflects the latest state of your persistent data.

## Summary

SwiftData truly revolutionizes data persistence on Apple platforms, offering a modern, Swift-native, and significantly more developer-friendly alternative to traditional Core Data setups. By leveraging Swift macros and integrating seamlessly with SwiftUI, it abstracts away much of the complexity, allowing you to focus on your app's unique features rather than boilerplate.

We've covered the essential steps:
-   Defining your data models using the `@Model` macro.
-   Setting up the `ModelContainer` in your app.
-   Performing CRUD operations (Create, Read, Update, Delete) using `ModelContext` and `@Query`.
-   Understanding how `@Bindable` helps manage updates in SwiftUI views.

This foundation should empower you to start building robust, data-driven applications with SwiftData today. Dive in, experiment, and enjoy the simplicity and power it brings to your iOS development workflow!

Happy Swifting!
