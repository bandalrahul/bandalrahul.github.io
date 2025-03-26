// swift-tools-version:5.5

import PackageDescription

let package = Package(
    name: "PublishSBR",
    platforms: [.macOS(.v12)],
    products: [
        .executable(
            name: "PublishSBR",
            targets: ["PublishSBR"]
        )
    ],
    dependencies: [
        .package(name: "Publish", url: "https://github.com/johnsundell/publish.git", from: "0.8.0"),
        .package(name: "SplashPublishPlugin", url: "https://github.com/johnsundell/splashpublishplugin", from: "0.1.0")
    ],
    targets: [
        .executableTarget(
            name: "PublishSBR",
            dependencies: ["Publish", "SplashPublishPlugin"]
        )
    ]
)
