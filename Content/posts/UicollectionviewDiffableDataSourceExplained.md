---
title: UICollectionView Diffable Data Source Explained
date: 2026-07-18 10:12
description: Simplify UICollectionView updates with Diffable Data Source. Learn how to manage complex list data, automate animations, and eliminate common bugs in your iOS apps.
tags: UIKit, iOS, Development
---

# UICollectionView Diffable Data Source Explained

For years, managing data in `UICollectionView` (and `UITableView`) was a manual and often error-prone process. We'd update our underlying data model, then call `reloadData()` or meticulously calculate `insertItems(at:)`, `deleteItems(at:)`, and `reloadItems(at:)` to animate changes. This often led to out-of-sync data, crashes due to incorrect index paths, and UI glitches. If you've ever battled `NSInternalInconsistencyException` or `Invalid update: invalid number of sections`, you know the pain.

Enter `UICollectionViewDiffableDataSource` (and its table view counterpart `UITableViewDiffableDataSource`), introduced at WWDC 2019. This powerful API fundamentally changes how we interact with `UICollectionView` data, making it safer, simpler, and more robust. It leverages Apple's diffing algorithm to automatically calculate the differences between two states of your data and apply the minimal set of updates to the collection view, complete with seamless animations.

In this article, we'll dive deep into `UICollectionViewDiffableDataSource`, exploring its core concepts, how to set it up, and best practices for managing your collection view data with confidence.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 700 250" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Comparison of Traditional vs Diffable Data Source for UICollectionView">
  <title>Traditional vs Diffable Data Source for UICollectionView</title>

  <!-- Traditional Approach -->
  <rect x="50" y="30" width="280" height="180" rx="10" ry="10" fill="#F0F0F0" stroke="#F04B3E" stroke-width="2"/>
  <text x="190" y="55" font-family="Helvetica Neue, Arial, sans-serif" font-size="18" font-weight="bold" text-anchor="middle" fill="#333">Traditional Data Source</text>

  <rect x="70" y="80" width="100" height="40" rx="5" ry="5" fill="#FFFFFF" stroke="#333" stroke-width="1"/>
  <text x="120" y="105" font-family="Helvetica Neue, Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">Data Array</text>

  <path d="M175 100 L215 100" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="195" y="90" font-family="Helvetica Neue, Arial, sans-serif" font-size="12" text-anchor="middle" fill="#F04B3E">Manual Updates</text>
  <text x="195" y="115" font-family="Helvetica Neue, Arial, sans-serif" font-size="12" text-anchor="middle" fill="#F04B3E">(reloadData(), insert, delete)</text>

  <rect x="220" y="80" width="100" height="40" rx="5" ry="5" fill="#FFFFFF" stroke="#333" stroke-width="1"/>
  <text x="270" y="105" font-family="Helvetica Neue, Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">UICollectionView</text>

  <rect x="70" y="140" width="250" height="50" rx="5" ry="5" fill="#FFFBEB" stroke="#F04B3E" stroke-width="1"/>
  <text x="195" y="165" font-family="Helvetica Neue, Arial, sans-serif" font-size="14" text-anchor="middle" fill="#F04B3E">Error-prone, Index Path Mismatches, Crashes</text>

  <!-- Diffable Data Source -->
  <rect x="370" y="30" width="280" height="180" rx="10" ry="10" fill="#F0F0F0" stroke="#2A8367" stroke-width="2"/>
  <text x="510" y="55" font-family="Helvetica Neue, Arial, sans-serif" font-size="18" font-weight="bold" text-anchor="middle" fill="#333">Diffable Data Source</text>

  <rect x="390" y="80" width="100" height="40" rx="5" ry="5" fill="#FFFFFF" stroke="#333" stroke-width="1"/>
  <text x="440" y="105" font-family="Helvetica Neue, Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">Data Array</text>

  <path d="M495 100 L535 100" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="515" y="90" font-family="Helvetica Neue, Arial, sans-serif" font-size="12" text-anchor="middle" fill="#2A8367">Create Snapshot</text>
  <text x="515" y="115" font-family="Helvetica Neue, Arial, sans-serif" font-size="12" text-anchor="middle" fill="#2A8367">(apply() with diffing)</text>

  <rect x="540" y="80" width="100" height="40" rx="5" ry="5" fill="#FFFFFF" stroke="#333" stroke-width="1"/>
  <text x="590" y="105" font-family="Helvetica Neue, Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">UICollectionView</text>

  <rect x="390" y="140" width="250" height="50" rx="5" ry="5" fill="#F0FFF0" stroke="#2A8367" stroke-width="1"/>
  <text x="515" y="165" font-family="Helvetica Neue, Arial, sans-serif" font-size="14" text-anchor="middle" fill="#2A8367">Automatic Animations, Stable, Less Boilerplate</text>

  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
    </marker>
  </defs>
</svg>
</div>

## Understanding the Core Concepts

At the heart of `UICollectionViewDiffableDataSource` are two main components:

1.  **`UICollectionViewDiffableDataSource<SectionIdentifierType, ItemIdentifierType>`**: This is the data source object itself. You initialize it with your collection view and a cell provider closure. It manages the communication between your data and the collection view.
    *   `SectionIdentifierType`: A type that uniquely identifies your sections.
    *   `ItemIdentifierType`: A type that uniquely identifies your items within sections.
    *   **Crucially, both `SectionIdentifierType` and `ItemIdentifierType` MUST conform to `Hashable`.** This is what allows the diffing algorithm to efficiently compare items and sections.

2.  **`NSDiffableDataSourceSnapshot<SectionIdentifierType, ItemIdentifierType>`**: This is a lightweight, immutable representation of the *current state* of your collection view's data. You create a snapshot, populate it with your sections and items, and then apply it to the `diffableDataSource`. The diffable data source then compares this new snapshot with its previous state, calculates the differences, and performs the necessary updates on the UICollectionView.

## Setting Up a Basic Diffable Data Source

Let's walk through setting up a simple `UICollectionView` that displays a list of items using `DiffableDataSource`.

First, define your `SectionIdentifierType` and `ItemIdentifierType`. For simplicity, we'll use enums here, but structs or even `String` / `UUID` can work as long as they are `Hashable`.

```swift
import UIKit

// 1. Define Section and Item Identifiers
enum Section: Hashable {
    case main
    case favorites
}

struct Fruit: Hashable {
    let name: String
    let emoji: String
    let id = UUID() // Essential for unique identification if name isn't unique

    func hash(into hasher: inout Hasher) {
        hasher.combine(id) // Only hash the unique ID
    }

    static func == (lhs: Fruit, rhs: Fruit) -> Bool {
        lhs.id == rhs.id
    }
}

class FruitsViewController: UIViewController {

    private var collectionView: UICollectionView!
    private var dataSource: UICollectionViewDiffableDataSource<Section, Fruit>!

    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Diffable Fruits"
        configureHierarchy()
        configureDataSource()
        applyInitialSnapshot()
    }

    // 2. Configure Collection View Layout
    private func configureHierarchy() {
        collectionView = UICollectionView(frame: view.bounds, collectionViewLayout: createLayout())
        collectionView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        collectionView.backgroundColor = .systemBackground
        view.addSubview(collectionView)
    }

    private func createLayout() -> UICollectionViewLayout {
        let itemSize = NSCollectionLayoutSize(widthDimension: .fractionalWidth(1.0),
                                              heightDimension: .fractionalHeight(1.0))
        let item = NSCollectionLayoutItem(layoutSize: itemSize)

        let groupSize = NSCollectionLayoutSize(widthDimension: .fractionalWidth(1.0),
                                               heightDimension: .absolute(44))
        let group = NSCollectionLayoutGroup.horizontal(layoutSize: groupSize, subitems: [item])

        let section = NSCollectionLayoutSection(group: group)
        section.contentInsets = NSDirectionalEdgeInsets(top: 10, leading: 10, bottom: 10, trailing: 10)
        section.interGroupSpacing = 5

        return UICollectionViewCompositionalLayout(section: section)
    }

    // 3. Configure the Diffable Data Source
    private func configureDataSource() {
        // Cell Registration: Define how to configure a cell for an item
        let cellRegistration = UICollectionView.CellRegistration<UICollectionViewListCell, Fruit> { (cell, indexPath, fruit) in
            var content = cell.defaultContentConfiguration()
            content.text = "\(fruit.emoji) \(fruit.name)"
            cell.contentConfiguration = content
            cell.accessories = [.disclosureIndicator()]
        }

        // Data Source Initialization: Connects the collection view with your data
        dataSource = UICollectionViewDiffableDataSource<Section, Fruit>(collectionView: collectionView) {
            (collectionView: UICollectionView, indexPath: IndexPath, fruit: Fruit) -> UICollectionViewCell? in
            // Dequeue and configure the cell using the registration
            return collectionView.dequeueConfiguredReusableCell(using: cellRegistration, for: indexPath, item: fruit)
        }
    }

    // 4. Apply an Initial Snapshot
    private func applyInitialSnapshot() {
        var snapshot = NSDiffableDataSourceSnapshot<Section, Fruit>()
        snapshot.appendSections([.main])
        snapshot.appendItems([
            Fruit(name: "Apple", emoji: "🍎"),
            Fruit(name: "Banana", emoji: "🍌"),
            Fruit(name: "Orange", emoji: "🍊"),
            Fruit(name: "Grape", emoji: "🍇")
        ], toSection: .main)

        dataSource.apply(snapshot, animatingDifferences: false) // 'false' for initial load, 'true' for updates
    }
}
```

In this setup:
*   We define `Section` and `Fruit` types that conform to `Hashable`. `Fruit` has a `UUID` to ensure uniqueness, even if two fruits have the same name.
*   `configureHierarchy()` sets up a basic `UICollectionView` with a compositional layout.
*   `configureDataSource()` is where the magic happens. We use `UICollectionView.CellRegistration` for modern cell configuration and then initialize our `UICollectionViewDiffableDataSource`, providing a closure that dequeues and configures cells.
*   `applyInitialSnapshot()` creates an `NSDiffableDataSourceSnapshot`, adds sections and items, and then applies it to the `dataSource`.

## Working with Snapshots

The real power of `DiffableDataSource` comes when your data changes. Instead of manually updating the collection view, you create a *new* snapshot representing the desired state and apply it.

Let's add some functionality to our `FruitsViewController` to update the data.

```swift
// ... inside FruitsViewController class ...

private var currentFruits: [Fruit] = [
    Fruit(name: "Apple", emoji: "🍎"),
    Fruit(name: "Banana", emoji: "🍌"),
    Fruit(name: "Orange", emoji: "🍊"),
    Fruit(name: "Grape", emoji: "🍇")
]

private var favoriteFruits: [Fruit] = []

// Modify applyInitialSnapshot to use currentFruits
override func viewDidLoad() {
    super.viewDidLoad()
    title = "Diffable Fruits"
    navigationItem.rightBarButtonItem = UIBarButtonItem(barButtonSystemItem: .add, target: self, action: #selector(addRandomFruit))
    navigationItem.leftBarButtonItem = UIBarButtonItem(title: "Toggle Favorites", style: .plain, target: self, action: #selector(toggleFavoriteSection))
    configureHierarchy()
    configureDataSource()
    applyCurrentStateSnapshot() // Renamed for clarity
}

// New method to apply the current state from our arrays
private func applyCurrentStateSnapshot(animatingDifferences: Bool = true) {
    var snapshot = NSDiffableDataSourceSnapshot<Section, Fruit>()

    // Add main section
    snapshot.appendSections([.main])
    snapshot.appendItems(currentFruits, toSection: .main)

    // Add favorites section if there are favorites
    if !favoriteFruits.isEmpty {
        snapshot.appendSections([.favorites])
        snapshot.appendItems(favoriteFruits, toSection: .favorites)
    }

    dataSource.apply(snapshot, animatingDifferences: animatingDifferences)
}

@objc private func addRandomFruit() {
    let newFruitNames = ["Kiwi", "Mango", "Pineapple", "Strawberry", "Cherry"]
    let newFruitEmojis = ["🥝", "🥭", "🍍", "🍓", "🍒"]
    let randomIndex = Int.random(in: 0..<newFruitNames.count)
    let newFruit = Fruit(name: newFruitNames[randomIndex], emoji: newFruitEmojis[randomIndex])

    currentFruits.append(newFruit)
    applyCurrentStateSnapshot() // Apply the new snapshot with animation
}

@objc private func toggleFavoriteSection() {
    if favoriteFruits.isEmpty {
        // Move a fruit from main to favorites
        if let fruitToMove = currentFruits.first {
            currentFruits.removeFirst()
            favoriteFruits.append(fruitToMove)
        }
    } else {
        // Move a fruit from favorites back to main
        if let fruitToMove = favoriteFruits.first {
            favoriteFruits.removeFirst()
            currentFruits.append(fruitToMove)
        }
    }
    applyCurrentStateSnapshot()
}

// You might also want to add a header for sections
private func createLayout() -> UICollectionViewLayout {
    // ... (existing item and group setup) ...

    let section = NSCollectionLayoutSection(group: group)
    section.contentInsets = NSDirectionalEdgeInsets(top: 10, leading: 10, bottom: 10, trailing: 10)
    section.interGroupSpacing = 5

    // Section Header
    let sectionHeaderSize = NSCollectionLayoutSize(widthDimension: .fractionalWidth(1.0),
                                                   heightDimension: .estimated(44))
    let sectionHeader = NSCollectionLayoutBoundarySupplementaryItem(
        layoutSize: sectionHeaderSize,
        elementKind: UICollectionView.elementKindSectionHeader,
        alignment: .top
    )
    section.boundarySupplementaryItems = [sectionHeader]

    return UICollectionViewCompositionalLayout(section: section)
}

// Configure supplementary views (like headers)
private func configureDataSource() {
    // ... (existing cell registration) ...

    dataSource = UICollectionViewDiffableDataSource<Section, Fruit>(collectionView: collectionView) {
        (collectionView: UICollectionView, indexPath: IndexPath, fruit: Fruit) -> UICollectionViewCell? in
        return collectionView.dequeueConfiguredReusableCell(using: cellRegistration, for: indexPath, item: fruit)
    }

    // Supplementary View Provider for headers
    let headerRegistration = UICollectionView.SupplementaryRegistration<UICollectionViewListCell>(elementKind: UICollectionView.elementKindSectionHeader) {
        (supplementaryView, elementKind, indexPath) in
        guard let section = self.dataSource.sectionIdentifier(for: indexPath.section) else { return }
        var content = supplementaryView.defaultContentConfiguration()
        content.text = (section == .main) ? "All Fruits" : "Favorite Fruits"
        supplementaryView.contentConfiguration = content
    }

    dataSource.supplementaryViewProvider = { (collectionView, elementKind, indexPath) -> UICollectionReusableView? in
        return collectionView.dequeueConfiguredReusableSupplementary(using: headerRegistration, for: indexPath)
    }
}
```

Now, when you tap "Add Random Fruit" or "Toggle Favorites", the `applyCurrentStateSnapshot()` method is called. It reconstructs the *entire* desired state of the collection view and asks the `dataSource` to update. The `dataSource` efficiently calculates the differences and animates the changes for you.

Here's a simple ASCII diagram illustrating the data flow:

```
┌───────────────────┐
│  Your Data Model  │
│ (e.g., [Fruit])   │
└───────────────────┘
         │
         ▼
┌───────────────────┐
│ Create New        │
│ NSDiffableDataSourceSnapshot │
│ (append sections/items)     │
└───────────────────┘
         │
         ▼
┌───────────────────┐
│ dataSource.apply( │
│   newSnapshot,    │
│   animatingDifferences: true │
│ )                 │
└───────────────────┘
         │
         ▼
┌───────────────────┐
│ Diffing Algorithm │
│    (internal)     │
└───────────────────┘
         │
         ▼
┌───────────────────┐
│ UICollectionView  │
│  Updates (e.g.,   │
│  insert, delete,  │
│  reload, move)    │
│  with Animations  │
└───────────────────┘
```

## Benefits and Best Practices

1.  **Automatic Animations**: By simply applying a new snapshot with `animatingDifferences: true`, you get smooth, automatic animations for inserts, deletes, reloads, and moves, without any manual calculation of index paths.
2.  **State-Driven Updates**: You describe *what* your UI should look like, not *how* to change it. This declarative approach makes your code easier to read, write, and maintain.
3.  **Reduced Boilerplate**: Gone are the days of implementing `numberOfSections`, `numberOfItemsInSection`, and `cellForItemAt` alongside complex update logic. The `DiffableDataSource` handles all of that.
4.  **Eliminates `NSInternalInconsistencyException`**: Since the diffing algorithm ensures the data source's state is always consistent with the UI, you largely avoid the notorious crashes caused by mismatched index paths.
5.  **Thread Safety**: While `NSDiffableDataSourceSnapshot` itself is immutable and can be constructed on any thread, `dataSource.apply()` **must be called on the main thread**. If you're performing heavy data processing, do it on a background queue, then dispatch the snapshot application to the main queue.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 700 250" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Flowchart of UICollectionView Diffable Data Source update process">
  <title>UICollectionView Diffable Data Source Update Flow</title>

  <!-- Nodes -->
  <rect x="50" y="20" width="150" height="50" rx="5" ry="5" fill="#1565c0" stroke="#1565c0"/>
  <text x="125" y="48" font-family="Helvetica Neue, Arial, sans-serif" font-size="14" text-anchor="middle" fill="#FFFFFF">1. Data Update</text>
  <text x="125" y="63" font-family="Helvetica Neue, Arial, sans-serif" font-size="12" text-anchor="middle" fill="#FFFFFF">(e.g., fetch, user action)</text>

  <rect x="220" y="20" width="150" height="50" rx="5" ry="5" fill="#2A8367" stroke="#2A8367"/>
  <text x="295" y="48" font-family="Helvetica Neue, Arial, sans-serif" font-size="14" text-anchor="middle" fill="#FFFFFF">2. Create New</text>
  <text x="295" y="63" font-family="Helvetica Neue, Arial, sans-serif" font-size="12" text-anchor="middle" fill="#FFFFFF">NSDiffableDataSourceSnapshot</text>

  <rect x="390" y="20" width="150" height="50" rx="5" ry="5" fill="#2A8367" stroke="#2A8367"/>
  <text x="465" y="48" font-family="Helvetica Neue, Arial, sans-serif" font-size="14" text-anchor="middle" fill="#FFFFFF">3. Apply Snapshot</text>
  <text x="465" y="63" font-family="Helvetica Neue, Arial, sans-serif" font-size="12" text-anchor="middle" fill="#FFFFFF">(dataSource.apply)</text>

  <rect x="560" y="20" width="120" height="50" rx="5" ry="5" fill="#F0F0F0" stroke="#333"/>
  <text x="620" y="48" font-family="Helvetica Neue, Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">4. Diffing</text>
  <text x="620" y="63" font-family="Helvetica Neue, Arial, sans-serif" font-size="12" text-anchor="middle" fill="#333">(system handles)</text>

  <rect x="220" y="150" width="150" height="50" rx="5" ry="5" fill="#F0F0F0" stroke="#333"/>
  <text x="295" y="178" font-family="Helvetica Neue, Arial, sans-serif" font-size="14" text-anchor="middle" fill="#333">UICollectionView</text>
  <text x="295" y="193" font-family="Helvetica Neue, Arial, sans-serif" font-size="12" text-anchor="middle" fill="#333">Animated Updates</text>

  <!-- Arrows -->
  <path d="M125 70 L125 100 L295 100 L295 70" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <path d="M295 70 L295 100 L465 100 L465 70" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <path d="M465 70 L465 100 L620 100 L620 70" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <path d="M620 70 L620 120 L300 120 L300 150" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>

  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
    </marker>
  </defs>
</svg>
</div>

### `ItemIdentifierType` and `SectionIdentifierType` Considerations

*   **Uniqueness is Key**: The `Hashable` conformance is critical. If your `ItemIdentifierType` or `SectionIdentifierType` has properties that can change, ensure your `hash(into:)` implementation and `==` operator only consider the *stable, unique* identifier (like a `UUID` or a database ID). If you hash mutable properties, changes to those properties will cause the item to be treated as a *new* item, leading to delete/insert animations instead of reload animations.
*   **Structs vs. Enums**: Both are excellent choices. Enums are great for a fixed number of sections or item types, while structs offer more flexibility for dynamic data.

## `UITableViewDiffableDataSource`

It's worth noting that `UITableViewDiffableDataSource` works almost identically to its `UICollectionView` counterpart. The core concepts of `NSDiffableDataSourceSnapshot`, `Hashable` identifiers, and applying snapshots remain the same. If you understand one, you understand the other.

## Summary

`UICollectionViewDiffableDataSource` is a game-changer for UIKit development. It simplifies complex data management, eliminates a common source of bugs, and provides beautiful, automatic animations with minimal effort. By embracing the state-driven approach of snapshots, you'll write cleaner, more robust, and more maintainable collection view code. If you're still using `reloadData()` or manual index path calculations, now is the perfect time to make the switch!

Happy Swifting!
