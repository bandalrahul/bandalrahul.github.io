---
title: Core Data Lightweight Migration on iOS
date: 2026-07-26 10:38
description: Learn how to handle simple Core Data model changes using lightweight migration, enabling smooth app updates without data loss.
tags: Core Data, iOS, Development
---

# Core Data Lightweight Migration on iOS

As iOS developers, we often build apps that store data persistently. Core Data is Apple's powerful framework for managing object graphs and persisting them to disk. It's a fantastic tool, but like any data persistence solution, it comes with a challenge: schema evolution. What happens when your app's data model changes after users have already started storing data with an older version of your app?

This is where Core Data migration comes into play. If you simply change your data model without telling Core Data how to handle the existing data, your app will crash with an `NSInternalInconsistencyException`, complaining that the persistent store doesn't match the current model. Nobody wants that!

Fortunately, Core Data offers several ways to migrate data, and the simplest and often most applicable is **Lightweight Migration**. In this article, we'll dive deep into what lightweight migration is, when to use it, and how to implement it in your iOS applications to ensure smooth updates and preserve user data.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Core Data Model Evolution">
  <title>Core Data Model Evolution</title>
  <style>
    .box { fill: #1565c0; stroke: #0d47a1; stroke-width: 2; }
    .arrow { stroke: #2A8367; stroke-width: 3; marker-end: url(#arrowhead); }
    .text { font-family: sans-serif; font-size: 18px; fill: #fff; text-anchor: middle; }
    .label { font-family: sans-serif; font-size: 16px; fill: #333; text-anchor: middle; }
  </style>
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#2A8367" />
    </marker>
  </defs>

  <rect x="50" y="50" width="200" height="100" rx="10" ry="10" class="box"/>
  <text x="150" y="105" class="text">Old Data Model</text>
  <text x="150" y="130" class="text" font-size="16px">v1.0</text>

  <rect x="350" y="50" width="200" height="100" rx="10" ry="10" class="box"/>
  <text x="450" y="105" class="text">New Data Model</text>
  <text x="450" y="130" class="text" font-size="16px">v2.0</text>

  <line x1="250" y1="100" x2="350" y2="100" class="arrow"/>
  <text x="300" y="180" class="label">Schema Change Detected!</text>
  <text x="300" y="200" class="label" fill="#F04B3E">Migration Required</text>
</svg>
</div>

### The Problem: When Your Model Changes

Imagine you've released an app that stores `User` entities with `name: String` and `age: Int`. A few months later, you decide to add an `email: String?` attribute to the `User` entity. If a user updates your app, their existing data was saved using the old model. When Core Data tries to load that data with the new model, it finds a mismatch. This leads to the infamous error:

```
The model used to open the store is incompatible with the one that was used to create the store.
```

To avoid this, you need to provide Core Data with instructions on how to transform the old data into the new format.

### What is Lightweight Migration?

Lightweight migration is Core Data's simplest form of migration. It's "lightweight" because Core Data can automatically infer the mapping between the old and new models without you having to write any explicit mapping model files. This automatic inference works for a surprising number of common schema changes.

**Lightweight migration can handle the following types of changes:**

*   **Adding new entities, attributes, or relationships:** New attributes will be initialized with their default values (if specified) or `nil` for optionals.
*   **Deleting entities, attributes, or relationships:** The corresponding data will simply be removed from the store.
*   **Changing an attribute from optional to non-optional (and vice-versa):** If changing from optional to non-optional, ensure your data model provides a default value for existing `nil` entries, or the migration will fail.
*   **Changing an attribute's type:** This works if the new type is compatible with the old type (e.g., `Int16` to `Int32`, `String` to `Data` for encoded data, or `Date` to `String` if the string format is parsable). More complex type changes might require heavy migration.
*   **Renaming entities, attributes, or relationships:** This is a crucial one. For Core Data to infer a rename, you *must* set the `renamingIdentifier` for the old attribute/entity/relationship to match the *new* name. We'll look at this in detail.

### Prerequisites for Lightweight Migration

Before Core Data can perform a lightweight migration, you need to set up your project correctly:

1.  **Model Versioning:** You must use Core Data's model versioning feature. Every time you make a change to your data model that requires migration, you should create a new version of your `.xcdatamodeld` file.
2.  **Renaming Identifiers (for renames):** If you rename an entity, attribute, or relationship, Core Data needs a hint. You provide this hint by setting the `renamingIdentifier` property of the *old* entity/attribute/relationship to its *new* name. This tells Core Data, "Hey, this `oldName` is actually `newName` in the new model."

### Step-by-Step Implementation

Let's walk through an example. Suppose we have a `Person` entity with `name: String` and `age: Int`. We want to add an `email: String?` attribute.

#### Step 1: Create a New Model Version

In Xcode, select your `.xcdatamodeld` file in the Project Navigator.
Go to `Editor > Add Model Version...`.
Give your new version a meaningful name (e.g., `MyAppDataModel v2`). Xcode will create a copy of your existing model and add it as a new version.

#### Step 2: Make Your Schema Changes

Now, select your *new* model version (e.g., `MyAppDataModel v2.xcdatamodel`) in the Project Navigator. Make your desired changes. In our example, we'd add a new attribute `email` of type `String` and make it optional.

If you were *renaming* an attribute (e.g., `age` to `yearsOld`), you would:
1.  In the *old* model version (`MyAppDataModel v1.xcdatamodel`), select the `age` attribute.
2.  In the Data Model Inspector (right sidebar), find the `Renaming ID` field and enter `yearsOld`.
3.  In the *new* model version (`MyAppDataModel v2.xcdatamodel`), rename the `age` attribute to `yearsOld`.
This tells Core Data that `age` in v1 maps to `yearsOld` in v2.

#### Step 3: Mark New Version as Current

With your `.xcdatamodeld` file still selected, go to the File Inspector (right sidebar). Under "Model Version," select your newly created version (e.g., `MyAppDataModel v2`) as the "Current" version. This tells Core Data which model to use when your app launches.

#### Step 4: Enable Automatic Migration in Code

The final step is to tell Core Data to attempt lightweight migration when it encounters a store that doesn't match the current model. This is done by setting two options when you add your persistent store to the `NSPersistentContainer`.

Here's a typical `PersistenceController` setup that enables lightweight migration:

```swift
import CoreData

struct PersistenceController {
    static let shared = PersistenceController()

    let container: NSPersistentContainer

    init(inMemory: Bool = false) {
        container = NSPersistentContainer(name: "MyAppDataModel") // Replace with your .xcdatamodeld file name
        
        // Define migration options
        let description = container.persistentStoreDescriptions.first
        description?.setOption(true as NSNumber, forKey: NSMigratePersistentStoresAutomaticallyOption)
        description?.setOption(true as NSNumber, forKey: NSInferMappingModelAutomaticallyOption)

        if inMemory {
            description?.url = URL(fileURLWithPath: "/dev/null")
        }

        container.loadPersistentStores { (storeDescription, error) in
            if let error = error as NSError? {
                // Replace this implementation with code to handle the error appropriately.
                // fatalError() causes the application to generate a crash log and terminate. You should not use this function in a shipping application, although it may be useful during development.

                /*
                 Typical reasons for an error here include:
                 * The parent directory does not exist, cannot be created, or disallows writing.
                 * The persistent store is not accessible, due to permissions or data protection when the device is locked.
                 * The device is out of space.
                 * The store could not be migrated to the current model version.
                 Check the error message to determine what the actual problem was.
                 */
                fatalError("Unresolved error \(error), \(error.userInfo)")
            }
        }
    }
}
```

The two key options here are:

*   `NSMigratePersistentStoresAutomaticallyOption`: Set to `true` to enable automatic store migration.
*   `NSInferMappingModelAutomaticallyOption`: Set to `true` to tell Core Data to automatically infer a mapping model between compatible store and model versions.

With these options, when your app launches and Core Data detects an older store file, it will automatically attempt a lightweight migration to update the store to your current model version.

```
┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│ Old Persistent    │     │                   │     │ New Persistent    │
│ Store (v1)        │────►│ Lightweight       │────►│ Store (v2)        │
│                   │     │ Migration Process │     │                   │
└───────────────────┘     └───────────────────┘     └───────────────────┘
```

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 280" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Lightweight Migration Example">
  <title>Lightweight Migration Example</title>
  <style>
    .box-before { fill: #F04B3E; stroke: #c62828; stroke-width: 2; }
    .box-after { fill: #2A8367; stroke: #1b5e20; stroke-width: 2; }
    .arrow { stroke: #1565c0; stroke-width: 3; marker-end: url(#arrowhead-blue); }
    .text-white { font-family: sans-serif; font-size: 18px; fill: #fff; text-anchor: middle; }
    .text-black { font-family: sans-serif; font-size: 16px; fill: #333; text-anchor: middle; }
    .title-text { font-family: sans-serif; font-size: 20px; font-weight: bold; fill: #333; text-anchor: middle; }
  </style>
  <defs>
    <marker id="arrowhead-blue" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#1565c0" />
    </marker>
  </defs>

  <text x="150" y="30" class="title-text">Before Migration (v1)</text>
  <rect x="50" y="50" width="200" height="150" rx="10" ry="10" class="box-before"/>
  <text x="150" y="80" class="text-white">Person Entity</text>
  <text x="150" y="110" class="text-white">name: String</text>
  <text x="150" y="140" class="text-white">age: Int</text>
  <text x="150" y="170" class="text-white">(no email attribute)</text>

  <text x="450" y="30" class="title-text">After Migration (v2)</text>
  <rect x="350" y="50" width="200" height="150" rx="10" ry="10" class="box-after"/>
  <text x="450" y="80" class="text-white">Person Entity</text>
  <text x="450" y="110" class="text-white">name: String</text>
  <text x="450" y="140" class="text-white">age: Int</text>
  <text x="450" y="170" class="text-white">email: String? (new)</text>

  <line x1="250" y1="125" x2="350" y2="125" class="arrow"/>
  <text x="300" y="240" class="text-black">Adding 'email' attribute is handled</text>
  <text x="300" y="260" class="text-black">automatically by Lightweight Migration.</text>
</svg>
</div>

### When Lightweight Migration Isn't Enough

While powerful for many common changes, lightweight migration has its limits. It cannot handle situations where Core Data cannot automatically infer the mapping. This typically includes:

*   **Complex data transformations:** For example, combining two attributes into one, splitting one attribute into two, or performing calculations to derive new attribute values.
*   **Merging or splitting entities:** If you combine two entities into one, or break one entity into multiple new ones.
*   **Custom validation logic:** If you need to run specific code to validate or transform data during the migration process.
*   **Non-inferable type changes:** For instance, changing a `String` attribute that stores a raw JSON string into a `Transformable` attribute that stores a custom `Codable` struct.

In these more complex scenarios, you'll need to resort to **Heavyweight Migration**. This involves manually creating a mapping model (`.xcmappingmodel` file) and often writing custom `NSEntityMigrationPolicy` subclasses to define the exact transformation logic. This is a more involved process and beyond the scope of lightweight migration.

### Practical Considerations and Best Practices

*   **Test, Test, Test:** Always thoroughly test your migrations. Create a test environment with an older version of your app's data, then update to the new version and verify that all data migrates correctly and the app functions as expected.
*   **Backup During Development:** When developing and testing migrations, it's wise to frequently back up your app's data store (usually located in the app's Documents or Application Support directory on the simulator/device).
*   **Schema Evolution Planning:** Think about potential future schema changes early in your app's lifecycle. Designing your initial model with flexibility can sometimes reduce the need for complex migrations down the line.
*   **Default Values:** When adding non-optional attributes, make sure to provide a default value in your model. If you don't, and existing objects have `nil` for that attribute, the migration will fail.

### Summary

Core Data lightweight migration is an essential tool for any iOS developer working with persistent data. By correctly versioning your data models and enabling the automatic migration options, you can gracefully handle many common schema changes without writing complex migration code. This ensures a smooth update experience for your users, preserving their valuable data as your app evolves. Remember to always test your migrations thoroughly to catch any unforeseen issues!

Happy Swifting!
