---
title: Compositional Layout in UICollectionView
date: 2026-07-19 10:20
description: Dive into UICollectionViewCompositionalLayout to build complex, adaptive layouts with ease and flexibility in your iOS apps.
tags: UIKit, iOS, Development
---

# Compositional Layout in UICollectionView

`UICollectionView` has been a cornerstone of iOS development for displaying ordered data sets in customizable layouts. From simple lists to complex grids, it has empowered developers to create rich, dynamic interfaces. However, achieving truly intricate, adaptive layouts—especially those mixing different visual styles within a single collection view—often required significant boilerplate code, custom `UICollectionViewLayout` subclasses, or even multiple collection views.

Enter `UICollectionViewCompositionalLayout`. Introduced in iOS 13, this powerful declarative layout system revolutionized how we approach collection view layouts. It provides a flexible and intuitive way to describe your layout visually, empowering you to build highly complex and adaptive UIs with significantly less effort than ever before. If you've ever struggled with `UICollectionViewFlowLayout`'s limitations or felt overwhelmed by custom layout subclassing, `CompositionalLayout` is here to be your new best friend.

This article will guide you through the core concepts of `UICollectionViewCompositionalLayout`, demonstrating how to construct various layouts, from simple lists to more complex, multi-section designs, all while keeping your code clean and maintainable.

## The Evolution of UICollectionView Layouts

Historically, `UICollectionViewFlowLayout` was the go-to choice for `UICollectionView`. It's excellent for grid-based or line-based layouts, but its "flow" nature meant that all items in a section generally followed the same pattern. If you wanted a section with a horizontal scrolling list and another section with a three-column grid, you were looking at either hacky workarounds, multiple collection views, or diving deep into custom `UICollectionViewLayout` subclasses—a path often fraught with challenges.

`UICollectionViewCompositionalLayout` changes this paradigm entirely. Instead of calculating frames directly, you _compose_ your layout from smaller, reusable components: items, groups, and sections. This declarative approach allows you to describe *what* your layout should look like, rather than *how* to calculate every single coordinate.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 700 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="UICollectionView Layout Evolution Diagram">
  <title>UICollectionView Layout Evolution</title>

  <!-- FlowLayout Box -->
  <rect x="50" y="40" width="250" height="100" rx="10" ry="10" fill="#F04B3E" opacity="0.1" stroke="#F04B3E" stroke-width="2"/>
  <text x="175" y="75" font-family="Arial, sans-serif" font-size="18" fill="#F04B3E" text-anchor="middle" font-weight="bold">UICollectionViewFlowLayout</text>
  <text x="175" y="110" font-family="Arial, sans-serif" font-size="14" fill="#666" text-anchor="middle">Simple grids & lists</text>
  <text x="175" y="130" font-family="Arial, sans-serif" font-size="14" fill="#666" text-anchor="middle">Limited flexibility</text>

  <!-- Arrow -->
  <line x1="300" y1="90" x2="400" y2="90" stroke="#1565c0" stroke-width="3" marker-end="url(#arrowhead)"/>
  <polyline points="390,80 400,90 390,100" fill="none" stroke="#1565c0" stroke-width="3" />
  <text x="350" y="120" font-family="Arial, sans-serif" font-size="14" fill="#1565c0" text-anchor="middle">Introduced iOS 13</text>

  <!-- CompositionalLayout Box -->
  <rect x="400" y="40" width="250" height="100" rx="10" ry="10" fill="#2A8367" opacity="0.1" stroke="#2A8367" stroke-width="2"/>
  <text x="525" y="75" font-family="Arial, sans-serif" font-size="18" fill="#2A8367" text-anchor="middle" font-weight="bold">UICollectionViewCompositionalLayout</text>
  <text x="525" y="110" font-family="Arial, sans-serif" font-size="14" fill="#666" text-anchor="middle">Declarative, flexible, adaptive</text>
  <text x="525" y="130" font-family="Arial, sans-serif" font-size="14" fill="#666" text-anchor="middle">Complex & mixed layouts</text>
</svg>
</div>

## Understanding the Building Blocks

`UICollectionViewCompositionalLayout` is built upon a hierarchy of four fundamental components:

1.  **`NSCollectionLayoutItem`**: The smallest unit. This represents a single cell in your collection view. You define its size relative to its container (the group).
2.  **`NSCollectionLayoutGroup`**: A container for one or more items. Groups define how items are arranged (e.g., horizontally, vertically, or custom). You define the group's size relative to its container (the section).
3.  **`NSCollectionLayoutSection`**: A container for one or more groups. Sections define the overall layout for a specific part of your collection view, including its content insets, inter-group spacing, and supplementary views (like headers/footers).
4.  **`UICollectionViewCompositionalLayout`**: The top-level object that takes one or more `NSCollectionLayoutSection` instances to define the complete layout for your `UICollectionView`.

This hierarchical structure allows for incredible flexibility. You define the layout from the inside out: item sizes are defined relative to their group, group sizes relative to their section, and section layouts make up the whole collection view layout.

Here's an ASCII diagram illustrating this hierarchy:

```
UICollectionViewCompositionalLayout
       │
       ▼
  NSCollectionLayoutSection
       │
       ▼
   NSCollectionLayoutGroup
       │
       ▼
   NSCollectionLayoutItem
```

## Crafting Your First Compositional Layout: A Simple List

Let's start with a common scenario: a simple vertical list. Each item takes the full width and has a fixed height.

```swift
import UIKit

class ListViewController: UIViewController {

    enum Section {
        case main
    }

    var collectionView: UICollectionView!
    var dataSource: UICollectionViewDiffableDataSource<Section, Int>!

    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Simple List"
        configureHierarchy()
        configureDataSource()
    }

    private func configureHierarchy() {
        collectionView = UICollectionView(frame: view.bounds, collectionViewLayout: createLayout())
        collectionView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        collectionView.backgroundColor = .systemBackground
        view.addSubview(collectionView)

        // Register cell
        collectionView.register(UICollectionViewListCell.self, forCellWithReuseIdentifier: "ListCell")
    }

    private func createLayout() -> UICollectionViewLayout {
        // Item: full width, fixed height
        let itemSize = NSCollectionLayoutSize(widthDimension: .fractionalWidth(1.0),
                                              heightDimension: .absolute(44))
        let item = NSCollectionLayoutItem(layoutSize: itemSize)

        // Group: vertical stack of items, full width, dynamic height
        let groupSize = NSCollectionLayoutSize(widthDimension: .fractionalWidth(1.0),
                                               heightDimension: .estimated(44)) // Estimated height for self-sizing cells
        let group = NSCollectionLayoutGroup.vertical(layoutSize: groupSize, subitems: [item])

        // Section: contains the group
        let section = NSCollectionLayoutSection(group: group)
        section.contentInsets = NSDirectionalEdgeInsets(top: 10, leading: 10, bottom: 10, trailing: 10)
        section.interGroupSpacing = 8 // Spacing between groups (items in this case)

        return UICollectionViewCompositionalLayout(section: section)
    }

    private func configureDataSource() {
        dataSource = UICollectionViewDiffableDataSource<Section, Int>(collectionView: collectionView) {
            (collectionView: UICollectionView, indexPath: IndexPath, identifier: Int) -> UICollectionViewCell? in

            let cell = collectionView.dequeueReusableCell(withReuseIdentifier: "ListCell", for: indexPath) as! UICollectionViewListCell
            var content = cell.defaultContentConfiguration()
            content.text = "Item \(identifier)"
            cell.contentConfiguration = content
            return cell
        }

        // Initial snapshot
        var snapshot = NSDiffableDataSourceSnapshot<Section, Int>()
        snapshot.appendSections([.main])
        snapshot.appendItems(Array(0..<30))
        dataSource.apply(snapshot, animatingDifferences: false)
    }
}
```

In this example:
-   `itemSize`: `fractionalWidth(1.0)` means the item will take 100% of its group's width. `absolute(44)` gives it a fixed height.
-   `groupSize`: `fractionalWidth(1.0)` means the group will take 100% of its section's width. `estimated(44)` is important for vertical groups containing items with `absolute` heights, or for self-sizing cells.
-   `NSCollectionLayoutGroup.vertical`: This convenience initializer creates a group that stacks its subitems vertically.
-   `NSCollectionLayoutSection`: The section holds our group. We add `contentInsets` and `interGroupSpacing` for visual appeal.
-   `UICollectionViewCompositionalLayout(section: section)`: For a single-section layout, you can pass the section directly.

## Adding Complexity: A Simple Grid Layout

Now, let's create a grid layout with multiple items per row. This is where `CompositionalLayout` really shines compared to `FlowLayout` for custom grid arrangements.

```swift
// ... (ListViewController structure, but for a new GridViewController)

class GridViewController: UIViewController {

    enum Section {
        case main
    }

    var collectionView: UICollectionView!
    var dataSource: UICollectionViewDiffableDataSource<Section, Int>!

    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Simple Grid"
        configureHierarchy()
        configureDataSource()
    }

    private func configureHierarchy() {
        collectionView = UICollectionView(frame: view.bounds, collectionViewLayout: createGridLayout())
        collectionView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        collectionView.backgroundColor = .systemBackground
        view.addSubview(collectionView)

        collectionView.register(GridCell.self, forCellWithReuseIdentifier: GridCell.reuseIdentifier)
    }

    private func createGridLayout() -> UICollectionViewLayout {
        // Item: one-third width, full height of its group
        let itemSize = NSCollectionLayoutSize(widthDimension: .fractionalWidth(1/3),
                                              heightDimension: .fractionalHeight(1.0))
        let item = NSCollectionLayoutItem(layoutSize: itemSize)
        item.contentInsets = NSDirectionalEdgeInsets(top: 5, leading: 5, bottom: 5, trailing: 5)

        // Group: horizontal stack of 3 items, full width, one-third height of its section
        let groupSize = NSCollectionLayoutSize(widthDimension: .fractionalWidth(1.0),
                                               heightDimension: .fractionalWidth(1/3)) // Make group height proportional to width
        let group = NSCollectionLayoutGroup.horizontal(layoutSize: groupSize, subitems: [item, item, item])
        // Or, more dynamically: NSCollectionLayoutGroup.horizontal(layoutSize: groupSize, count: 3)

        // Section: contains the group
        let section = NSCollectionLayoutSection(group: group)
        section.contentInsets = NSDirectionalEdgeInsets(top: 10, leading: 10, bottom: 10, trailing: 10)
        
        return UICollectionViewCompositionalLayout(section: section)
    }

    private func configureDataSource() {
        dataSource = UICollectionViewDiffableDataSource<Section, Int>(collectionView: collectionView) {
            (collectionView: UICollectionView, indexPath: IndexPath, identifier: Int) -> UICollectionViewCell? in

            let cell = collectionView.dequeueReusableCell(withReuseIdentifier: GridCell.reuseIdentifier, for: indexPath) as! GridCell
            cell.label.text = "\(identifier)"
            return cell
        }

        var snapshot = NSDiffableDataSourceSnapshot<Section, Int>()
        snapshot.appendSections([.main])
        snapshot.appendItems(Array(0..<90))
        dataSource.apply(snapshot, animatingDifferences: false)
    }
}

// Example custom cell for grid
class GridCell: UICollectionViewCell {
    static let reuseIdentifier = "GridCell"
    let label = UILabel()

    override init(frame: CGRect) {
        super.init(frame: frame)
        configure()
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    private func configure() {
        backgroundColor = .systemTeal.withAlphaComponent(0.6)
        layer.cornerRadius = 8
        label.font = UIFont.preferredFont(forTextStyle: .title2)
        label.textAlignment = .center
        label.textColor = .white
        
        contentView.addSubview(label)
        label.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            label.centerXAnchor.constraint(equalTo: contentView.centerXAnchor),
            label.centerYAnchor.constraint(equalTo: contentView.centerYAnchor)
        ])
    }
}
```

Key changes for the grid:
-   `itemSize`: Each item is `1/3` of the group's width and `1.0` (full) of the group's height.
-   `groupSize`: We use `fractionalWidth(1.0)` for the group's width and `fractionalWidth(1/3)` for its height. This makes the group's height always `1/3` of its width, ensuring square cells if the items within the group are also square.
-   `NSCollectionLayoutGroup.horizontal(layoutSize:subitems:)`: This creates a horizontal row of items. We explicitly pass `[item, item, item]` to ensure 3 items per row. Alternatively, `count: 3` can be used.

## Working with Multiple Sections and Different Layouts

The true power of `CompositionalLayout` comes when you need different layouts for different sections within the same collection view. This is achieved by creating an array of `NSCollectionLayoutSection` instances and passing a section provider closure to the `UICollectionViewCompositionalLayout` initializer.

Let's create a layout with a horizontal scrolling list in the first section and a grid in the second.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 350" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Compositional Layout with Multiple Sections">
  <title>Compositional Layout with Multiple Sections</title>

  <!-- Overall CollectionView -->
  <rect x="50" y="20" width="500" height="300" rx="15" ry="15" fill="#E0F2F7" stroke="#1565c0" stroke-width="2"/>
  <text x="300" y="45" font-family="Arial, sans-serif" font-size="16" fill="#1565c0" text-anchor="middle" font-weight="bold">UICollectionView</text>

  <!-- Section 1 (Horizontal List) -->
  <rect x="70" y="60" width="460" height="100" rx="10" ry="10" fill="#FCE4EC" stroke="#F04B3E" stroke-width="1.5"/>
  <text x="300" y="80" font-family="Arial, sans-serif" font-size="14" fill="#F04B3E" text-anchor="middle">Section 0: Horizontal List</text>
  
  <!-- Items in Section 1 -->
  <rect x="80" y="100" width="80" height="50" rx="5" ry="5" fill="#F8BBD0" stroke="#F04B3E" stroke-width="1"/>
  <text x="120" y="128" font-family="Arial, sans-serif" font-size="12" fill="#880E4F" text-anchor="middle">Item A</text>
  <rect x="170" y="100" width="80" height="50" rx="5" ry="5" fill="#F8BBD0" stroke="#F04B3E" stroke-width="1"/>
  <text x="210" y="128" font-family="Arial, sans-serif" font-size="12" fill="#880E4F" text-anchor="middle">Item B</text>
  <rect x="260" y="100" width="80" height="50" rx="5" ry="5" fill="#F8BBD0" stroke="#F04B3E" stroke-width="1"/>
  <text x="300" y="128" font-family="Arial, sans-serif" font-size="12" fill="#880E4F" text-anchor="middle">Item C</text>
  <!-- ... more items indicating scroll -->
  <text x="380" y="128" font-family="Arial, sans-serif" font-size="20" fill="#880E4F" text-anchor="middle">...</text>
  <text x="450" y="128" font-family="Arial, sans-serif" font-size="12" fill="#880E4F" text-anchor="middle">(Scrollable)</text>


  <!-- Section 2 (Grid) -->
  <rect x="70" y="180" width="460" height="130" rx="10" ry="10" fill="#E8F5E9" stroke="#2A8367" stroke-width="1.5"/>
  <text x="300" y="200" font-family="Arial, sans-serif" font-size="14" fill="#2A8367" text-anchor="middle">Section 1: Grid Layout</text>

  <!-- Items in Section 2 -->
  <rect x="80" y="220" width="100" height="40" rx="5" ry="5" fill="#C8E6C9" stroke="#2A8367" stroke-width="1"/>
  <text x="130" y="243" font-family="Arial, sans-serif" font-size="12" fill="#1B5E20" text-anchor="middle">Cell 1</text>
  <rect x="200" y="220" width="100" height="40" rx="5" ry="5" fill="#C8E6C9" stroke="#2A8367" stroke-width="1"/>
  <text x="250" y="243" font-family="Arial, sans-serif" font-size="12" fill="#1B5E20" text-anchor="middle">Cell 2</text>
  <rect x="320" y="220" width="100" height="40" rx="5" ry="5" fill="#C8E6C9" stroke="#2A8367" stroke-width="1"/>
  <text x="370" y="243" font-family="Arial, sans-serif" font-size="12" fill="#1B5E20" text-anchor="middle">Cell 3</text>

  <rect x="80" y="270" width="100" height="40" rx="5" ry="5" fill="#C8E6C9" stroke="#2A8367" stroke-width="1"/>
  <text x="130" y="293" font-family="Arial, sans-serif" font-size="12" fill="#1B5E20" text-anchor="middle">Cell 4</text>
  <rect x="200" y="270" width="100" height="40" rx="5" ry="5" fill="#C8E6C9" stroke="#2A8367" stroke-width="1"/>
  <text x="250" y="293" font-family="Arial, sans-serif" font-size="12" fill="#1B5E20" text-anchor="middle">Cell 5</text>
  <rect x="320" y="270" width="100" height="40" rx="5" ry="5" fill="#C8E6C9" stroke="#2A8367" stroke-width="1"/>
  <text x="370" y="293" font-family="Arial, sans-serif" font-size="12" fill="#1B5E20" text-anchor="middle">Cell 6</text>

</svg>
</div>

```swift
import UIKit

class MixedLayoutViewController: UIViewController {

    enum Section: Int, CaseIterable {
        case featuredProducts
        case categories
    }

    var collectionView: UICollectionView!
    var dataSource: UICollectionViewDiffableDataSource<Section, Int>!

    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Mixed Layout"
        configureHierarchy()
        configureDataSource()
    }

    private func configureHierarchy() {
        collectionView = UICollectionView(frame: view.bounds, collectionViewLayout: createMixedLayout())
        collectionView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        collectionView.backgroundColor = .systemBackground
        view.addSubview(collectionView)

        // Register cells
        collectionView.register(ListCell.self, forCellWithReuseIdentifier: ListCell.reuseIdentifier)
        collectionView.register(GridCell.self, forCellWithReuseIdentifier: GridCell.reuseIdentifier)
    }

    private func createMixedLayout() -> UICollectionViewLayout {
        let layout = UICollectionViewCompositionalLayout { (sectionIndex: Int, layoutEnvironment: NSCollectionLayoutEnvironment) -> NSCollectionLayoutSection? in
            guard let sectionKind = Section(rawValue: sectionIndex) else { return nil }

            switch sectionKind {
            case .featuredProducts:
                // Horizontal scrolling list
                let itemSize = NSCollectionLayoutSize(widthDimension: .fractionalWidth(1.0),
                                                      heightDimension: .fractionalHeight(1.0))
                let item = NSCollectionLayoutItem(layoutSize: itemSize)
                item.contentInsets = NSDirectionalEdgeInsets(top: 5, leading: 5, bottom: 5, trailing: 5)

                let groupSize = NSCollectionLayoutSize(widthDimension: .fractionalWidth(0.9), // 90% of screen width
                                                       heightDimension: .absolute(150)) // Fixed height
                let group = NSCollectionLayoutGroup.horizontal(layoutSize: groupSize, subitems: [item])

                let section = NSCollectionLayoutSection(group: group)
                section.orthogonalScrollingBehavior = .continuous // Make it horizontally scrollable
                section.contentInsets = NSDirectionalEdgeInsets(top: 10, leading: 10, bottom: 10, trailing: 10)
                section.interGroupSpacing = 10
                return section

            case .categories:
                // Grid layout (3 items per row)
                let itemSize = NSCollectionLayoutSize(widthDimension: .fractionalWidth(1/3),
                                                      heightDimension: .fractionalHeight(1.0))
                let item = NSCollectionLayoutItem(layoutSize: itemSize)
                item.contentInsets = NSDirectionalEdgeInsets(top: 5, leading: 5, bottom: 5, trailing: 5)

                let groupSize = NSCollectionLayoutSize(widthDimension: .fractionalWidth(1.0),
                                                       heightDimension: .absolute(100)) // Fixed height for grid row
                let group = NSCollectionLayoutGroup.horizontal(layoutSize: groupSize, subitems: [item, item, item])

                let section = NSCollectionLayoutSection(group: group)
                section.contentInsets = NSDirectionalEdgeInsets(top: 10, leading: 10, bottom: 10, trailing: 10)
                section.interGroupSpacing = 10
                return section
            }
        }
        return layout
    }

    private func configureDataSource() {
        dataSource = UICollectionViewDiffableDataSource<Section, Int>(collectionView: collectionView) {
            (collectionView: UICollectionView, indexPath: IndexPath, identifier: Int) -> UICollectionViewCell? in

            guard let sectionKind = Section(rawValue: indexPath.section) else {
                fatalError("Unknown section")
            }

            switch sectionKind {
            case .featuredProducts:
                let cell = collectionView.dequeueReusableCell(withReuseIdentifier: ListCell.reuseIdentifier, for: indexPath) as! ListCell
                cell.label.text = "Featured \(identifier)"
                cell.backgroundColor = .systemRed.withAlphaComponent(0.6)
                return cell
            case .categories:
                let cell = collectionView.dequeueReusableCell(withReuseIdentifier: GridCell.reuseIdentifier, for: indexPath) as! GridCell
                cell.label.text = "Cat \(identifier)"
                cell.backgroundColor = .systemGreen.withAlphaComponent(0.6)
                return cell
            }
        }

        var snapshot = NSDiffableDataSourceSnapshot<Section, Int>()
        snapshot.appendSections([.featuredProducts, .categories])
        snapshot.appendItems(Array(0..<10), toSection: .featuredProducts)
        snapshot.appendItems(Array(100..<120), toSection: .categories)
        dataSource.apply(snapshot, animatingDifferences: false)
    }
}

// Reusing GridCell from before, and adding a ListCell
class ListCell: UICollectionViewCell {
    static let reuseIdentifier = "ListCell"
    let label = UILabel()

    override init(frame: CGRect) {
        super.init(frame: frame)
        configure()
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    private func configure() {
        backgroundColor = .systemBlue.withAlphaComponent(0.6)
        layer.cornerRadius = 8
        label.font = UIFont.preferredFont(forTextStyle: .headline)
        label.textAlignment = .center
        label.textColor = .white
        
        contentView.addSubview(label)
        label.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            label.centerXAnchor.constraint(equalTo: contentView.centerXAnchor),
            label.centerYAnchor.constraint(equalTo: contentView.centerYAnchor),
            label.leadingAnchor.constraint(greaterThanOrEqualTo: contentView.leadingAnchor, constant: 5),
            label.trailingAnchor.constraint(lessThanOrEqualTo: contentView.trailingAnchor, constant: -5)
        ])
    }
}
```

In the `createMixedLayout()` function:
-   We use the `UICollectionViewCompositionalLayout(sectionProvider:)` initializer. This closure is called for each section index, allowing you to return a different `NSCollectionLayoutSection` based on the `sectionIndex`.
-   For `.featuredProducts`, we define a horizontal group and set `section.orthogonalScrollingBehavior = .continuous` to make the section scroll horizontally.
-   For `.categories`, we define our 3-column grid again.
-   The `layoutEnvironment` parameter in the section provider closure is crucial for adaptive layouts, allowing you to adjust layout based on the current trait collection, container size, etc.

## Advanced Considerations

-   **Supplementary Views**: You can easily add headers, footers, and other supplementary views to your sections using `NSCollectionLayoutBoundarySupplementaryItem`. These are defined within the `NSCollectionLayoutSection`.
-   **Decoration Views**: For background visuals or custom separators that aren't tied to data, `NSCollectionLayoutDecorationItem` allows you to add aesthetic elements directly to the layout.
-   **Adaptive Layouts**: The `layoutEnvironment` parameter in the `sectionProvider` closure is key. You can check `layoutEnvironment.container.effectiveContentSize` or `layoutEnvironment.traitCollection` to create layouts that respond dynamically to size changes (e.g., device rotation, iPad multitasking).
-   **Performance**: `CompositionalLayout` is highly optimized. By defining layouts declaratively, the system can perform efficient calculations. When combined with `UICollectionViewDiffableDataSource`, you get excellent performance and simplified data management.

## Summary

`UICollectionViewCompositionalLayout` offers a truly modern and flexible approach to building complex and adaptive collection view layouts. By embracing its hierarchical model of items, groups, and sections, you can create intricate designs with significantly less code and greater clarity than traditional methods. Its declarative nature simplifies layout logic, promotes reusability, and integrates seamlessly with `DiffableDataSource` for powerful and performant UIs. If you're building any non-trivial `UICollectionView` layout, `CompositionalLayout` is the way to go.

Happy Swifting!
