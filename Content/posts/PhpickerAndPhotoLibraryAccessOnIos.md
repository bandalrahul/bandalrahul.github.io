---
title: PHPicker and Photo Library Access on iOS
date: 2026-08-18 09:24
description: Learn how to integrate PHPickerViewController for secure, modern photo and video selection, and manage Photo Library permissions on iOS.
tags: Photos, iOS, Development
---

# PHPicker and Photo Library Access on iOS

Accessing a user's photo and video library is a fundamental feature for many iOS applications, from social media platforms to utility tools. However, handling sensitive user data like personal photos comes with significant privacy implications and requires careful implementation. For years, `UIImagePickerController` was the go-to solution, but with iOS 14, Apple introduced `PHPickerViewController`, a modern, privacy-focused alternative that has become the recommended way to interact with the user's media library.

In this article, we'll dive deep into `PHPickerViewController`, exploring its advantages, how to implement it, and how to properly manage photo library access permissions in your iOS applications.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 700 250" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Comparison of UIImagePickerController and PHPickerViewController access models">
  <title>Comparison of UIImagePickerController and PHPickerViewController access models</title>

  <!-- UIImagePickerController Path -->
  <rect x="20" y="30" width="180" height="60" rx="8" fill="#1565c0" stroke="#0e4a8c" stroke-width="2"/>
  <text x="110" y="65" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">UIImagePickerController</text>

  <path d="M200 60 H230 L250 50 L250 70 L230 60 Z" fill="#2A8367" stroke="#2A8367" stroke-width="1"/>
  <text x="250" y="65" font-family="Arial, sans-serif" font-size="14" fill="#333" text-anchor="start">App requests full access</text>

  <rect x="400" y="30" width="120" height="60" rx="8" fill="#F04B3E" stroke="#c03c32" stroke-width="2"/>
  <text x="460" y="65" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">User Grants</text>

  <path d="M520 60 H550 L570 50 L570 70 L550 60 Z" fill="#2A8367" stroke="#2A8367" stroke-width="1"/>
  <text x="570" y="65" font-family="Arial, sans-serif" font-size="14" fill="#333" text-anchor="start">App browses library directly</text>

  <!-- PHPickerViewController Path -->
  <rect x="20" y="150" width="180" height="60" rx="8" fill="#1565c0" stroke="#0e4a8c" stroke-width="2"/>
  <text x="110" y="185" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">PHPickerViewController</text>

  <path d="M200 180 H230 L250 170 L250 190 L230 180 Z" fill="#2A8367" stroke="#2A8367" stroke-width="1"/>
  <text x="250" y="185" font-family="Arial, sans-serif" font-size="14" fill="#333" text-anchor="start">App presents picker</text>

  <rect x="400" y="150" width="120" height="60" rx="8" fill="#2A8367" stroke="#1f624d" stroke-width="2"/>
  <text x="460" y="185" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">System UI</text>

  <path d="M520 180 H550 L570 170 L570 190 L550 180 Z" fill="#2A8367" stroke="#2A8367" stroke-width="1"/>
  <text x="570" y="185" font-family="Arial, sans-serif" font-size="14" fill="#333" text-anchor="start">System delivers assets</text>

  <!-- Labels -->
  <text x="350" y="15" font-family="Arial, sans-serif" font-size="18" fill="#333" text-anchor="middle" font-weight="bold">Older Approach (Full Access)</text>
  <text x="350" y="135" font-family="Arial, sans-serif" font-size="18" fill="#333" text-anchor="middle" font-weight="bold">Modern Approach (Privacy-Preserving)</text>
</svg>
</div>

## Why PHPickerViewController is the Modern Choice

Before `PHPickerViewController`, `UIImagePickerController` allowed apps to present a system interface for selecting photos or videos. However, using `UIImagePickerController` inherently required your app to request and be granted full read access to the user's entire photo library (or at least the limited selection if the user chose that in iOS 14+). This meant if your user selected a single photo, your app still had the potential to access all their photos, which was a significant privacy concern.

`PHPickerViewController`, introduced in iOS 14, fundamentally changes this model:

1.  **Enhanced Privacy**: Your app does not need explicit photo library access permission to present `PHPickerViewController`. The picker runs in a separate process, and only the items explicitly selected by the user are shared with your app via `NSItemProvider`. This means your app never gains full access to the user's entire photo library.
2.  **Multi-Selection**: It natively supports selecting multiple photos and videos, a feature that was cumbersome or impossible with `UIImagePickerController`.
3.  **Search and Filtering**: Users can search their library directly within the picker, and you can configure filters to show only specific media types (images, videos, Live Photos).
4.  **Modern UI**: It offers a more modern and consistent user interface, aligning with the Photos app.

For these reasons, `PHPickerViewController` is now the recommended API for allowing users to select media from their photo library.

## Implementing PHPickerViewController

Integrating `PHPickerViewController` into your app involves a few straightforward steps:

1.  **Import `PhotosUI`**: This framework contains `PHPickerViewController` and related types.
2.  **Configure the Picker**: Create a `PHPickerConfiguration` instance to specify selection limits, media types, and other options.
3.  **Present the Picker**: Initialize `PHPickerViewController` with your configuration and present it modally.
4.  **Handle Selections**: Implement the `PHPickerViewControllerDelegate` protocol to receive the selected assets.

Let's look at a practical example. We'll create a simple view controller that presents the picker and displays the selected images.

```swift
import UIKit
import PhotosUI // Don't forget to import PhotosUI!

class PhotoSelectionViewController: UIViewController {

    private lazy var selectPhotosButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("Select Photos", for: .normal)
        button.addTarget(self, action: #selector(selectPhotosTapped), for: .touchUpInside)
        return button
    }()

    private lazy var imageView: UIImageView = {
        let imageView = UIImageView()
        imageView.contentMode = .scaleAspectFit
        imageView.backgroundColor = .systemGray6
        imageView.layer.cornerRadius = 8
        imageView.clipsToBounds = true
        return imageView
    }()

    private lazy var activityIndicator: UIActivityIndicatorView = {
        let indicator = UIActivityIndicatorView(style: .large)
        indicator.hidesWhenStopped = true
        return indicator
    }()

    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
    }

    private func setupUI() {
        view.backgroundColor = .systemBackground

        let stackView = UIStackView(arrangedSubviews: [selectPhotosButton, imageView])
        stackView.axis = .vertical
        stackView.spacing = 20
        stackView.alignment = .fill
        stackView.translatesAutoresizingMaskIntoConstraints = false

        view.addSubview(stackView)
        view.addSubview(activityIndicator)

        NSLayoutConstraint.activate([
            stackView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 20),
            stackView.leadingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.leadingAnchor, constant: 20),
            stackView.trailingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.trailingAnchor, constant: -20),
            stackView.bottomAnchor.constraint(lessThanOrEqualTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -20),
            imageView.heightAnchor.constraint(equalToConstant: 300),

            activityIndicator.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            activityIndicator.centerYAnchor.constraint(equalTo: imageView.centerYAnchor)
        ])
    }

    @objc private func selectPhotosTapped() {
        var configuration = PHPickerConfiguration()
        configuration.filter = .images // We only want images
        configuration.selectionLimit = 1 // Allow selecting only one image. Use 0 for unlimited.
        configuration.preferredAssetRepresentationMode = .current // Use .current for the highest quality available

        let picker = PHPickerViewController(configuration: configuration)
        picker.delegate = self
        present(picker, animated: true)
    }
}
```

Now, let's implement the `PHPickerViewControllerDelegate` to handle the selected photos.

```swift
extension PhotoSelectionViewController: PHPickerViewControllerDelegate {
    func picker(_ picker: PHPickerViewController, didFinishPicking results: [PHPickerResult]) {
        picker.dismiss(animated: true)

        guard let itemProvider = results.first?.itemProvider else { return }

        // Start activity indicator while loading
        activityIndicator.startAnimating()
        imageView.image = nil // Clear previous image

        if itemProvider.canLoadObject(ofClass: UIImage.self) {
            itemProvider.loadObject(ofClass: UIImage.self) { [weak self] (image, error) in
                DispatchQueue.main.async {
                    self?.activityIndicator.stopAnimating()
                    if let image = image as? UIImage {
                        self?.imageView.image = image
                    } else if let error = error {
                        print("Error loading image: \(error.localizedDescription)")
                        // Handle error, e.g., show an alert
                    }
                }
            }
        } else {
            DispatchQueue.main.async {
                self.activityIndicator.stopAnimating()
                print("Item provider cannot load UIImage.")
            }
        }
    }
}
```
In this example, we're loading a `UIImage` directly. For videos or other media types, you'd check for `AVAsset`, `Data`, or `URL` using `itemProvider.canLoadObject(ofClass:)` and `itemProvider.loadObject(ofClass:)` accordingly. Remember that `loadObject` is asynchronous, so update your UI on the main thread.

## Photo Library Access Permissions

As mentioned, `PHPickerViewController` does **not** require explicit photo library access permission to function. This is its core privacy advantage. However, there are scenarios where your app might still need direct access to the photo library:

*   **Saving photos/videos**: If your app creates new media and wants to save it to the user's photo library.
*   **Custom photo browser**: If you're building your own UI to browse the user's entire library, rather than using `PHPickerViewController`.
*   **Modifying existing assets**: For advanced editing apps that need to alter metadata or content of existing photos.

For these cases, you still need to request permission using `PHPhotoLibrary.requestAuthorization(for:)` and provide appropriate `Info.plist` entries.

### Info.plist Entries

You must include one or both of these keys in your `Info.plist` file with a user-facing description:

*   `NSPhotoLibraryUsageDescription`: Required for **read and write** access to the photo library.
*   `NSPhotoLibraryAddUsageDescription`: Required only for **write-only** access (e.g., saving a photo without browsing).

Without these entries, your app will crash when attempting to request photo library access.

### Requesting Authorization

You can check the current authorization status and request it using the `PHPhotoLibrary` class.

```
┌─────────────────┐     ┌───────────────────────┐
│   App Starts    │     │ Check Authorization   │
│                 │────►│ (PHPhotoLibrary.auth) │
└─────────────────┘     └───────────┬───────────┘
                                    │
                       .notDetermined / .denied / .restricted
                                    ▼
                      ┌───────────────────────────┐
                      │ Request Authorization     │
                      │ (PHPhotoLibrary.request)  │
                      └───────────┬───────────┘
                                  │
                                  ▼
                     ┌───────────────────────────┐
                     │   User Grants/Denies      │
                     └───────────┬───────────┘
                                 │
                                 ▼
                    ┌───────────────────────────┐
                    │ Handle New Status         │
                    │ (.authorized, .denied, etc)│
                    └───────────────────────────┘
```

Here's how you might implement a utility to manage photo library authorization:

```swift
import Photos

class PhotoLibraryAccessManager {

    enum AuthorizationStatus {
        case authorized
        case denied
        case restricted
        case notDetermined
        case limited // Specific to iOS 14+ when user grants limited access
    }

    static func currentAuthorizationStatus() -> AuthorizationStatus {
        let status = PHPhotoLibrary.authorizationStatus(for: .readWrite)
        switch status {
        case .authorized: return .authorized
        case .denied: return .denied
        case .restricted: return .restricted
        case .notDetermined: return .notDetermined
        case .limited: return .limited // For iOS 14+
        @unknown default:
            // Future cases might be added, handle them gracefully
            return .notDetermined
        }
    }

    static func requestPhotoLibraryAuthorization(completion: @escaping (AuthorizationStatus) -> Void) {
        PHPhotoLibrary.requestAuthorization(for: .readWrite) { status in
            DispatchQueue.main.async {
                switch status {
                case .authorized: completion(.authorized)
                case .denied: completion(.denied)
                case .restricted: completion(.restricted)
                case .notDetermined: completion(.notDetermined)
                case .limited: completion(.limited)
                @unknown default:
                    completion(.notDetermined)
                }
            }
        }
    }

    // Example usage:
    func checkAndRequestAccess() {
        let status = PhotoLibraryAccessManager.currentAuthorizationStatus()
        switch status {
        case .authorized:
            print("Full photo library access granted.")
            // Proceed with operations that require full access
        case .limited:
            print("Limited photo library access granted (iOS 14+).")
            // Proceed with operations, but be aware of limitations
        case .notDetermined:
            print("Authorization not determined. Requesting...")
            PhotoLibraryAccessManager.requestPhotoLibraryAuthorization { newStatus in
                self.handleAuthorizationStatus(newStatus)
            }
        case .denied:
            print("Photo library access denied. Guide user to settings.")
            // Show alert to user to go to Settings -> Privacy & Security -> Photos
        case .restricted:
            print("Photo library access restricted, possibly by parental controls.")
            // Inform user
        }
    }

    private func handleAuthorizationStatus(_ status: AuthorizationStatus) {
        switch status {
        case .authorized: print("User granted full access.")
        case .limited: print("User granted limited access.")
        case .denied: print("User denied access.")
        case .restricted: print("Access restricted.")
        case .notDetermined: print("Access not determined (shouldn't happen after request).")
        }
        // Update UI or proceed based on new status
    }
}
```
Remember to call `checkAndRequestAccess()` at an appropriate time, typically when the user attempts an action that requires photo library access.

## Advanced PHPicker Configuration

`PHPickerConfiguration` offers more than just filtering images. Here are a few useful properties:

*   `filter`: A `PHPickerFilter` enum that allows you to specify the types of media users can select (`.images`, `.videos`, `.livePhotos`, or combinations).
*   `selectionLimit`: An `Int` that defines the maximum number of items a user can select. Set to `0` for unlimited selection.
*   `selection`: A `PHPickerConfiguration.Selection` enum (introduced in iOS 16) for fine-grained control over how multiple selections are displayed (e.g., `.ordered`, `.continuous`).
*   `preferredAssetRepresentationMode`: A `PHPickerConfiguration.AssetRepresentationMode` enum. `.current` provides the highest quality available, `.compatible` provides a format compatible with the current device, and `.thumbnail` provides a low-resolution thumbnail. Be mindful of memory usage when requesting `.current` for many items.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 700 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Data flow from PHPickerViewController to an iOS application">
  <title>Data flow from PHPickerViewController to an iOS application</title>

  <!-- Start PHPickerVC -->
  <rect x="20" y="20" width="150" height="60" rx="8" fill="#1565c0" stroke="#0e4a8c" stroke-width="2"/>
  <text x="95" y="55" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">PHPickerViewController</text>

  <!-- Arrow to Delegate -->
  <path d="M170 50 H200 L220 40 L220 60 L200 50 Z" fill="#2A8367" stroke="#2A8367" stroke-width="1"/>
  <text x="225" y="55" font-family="Arial, sans-serif" font-size="14" fill="#333">Delegate Call</text>

  <!-- didFinishPicking -->
  <rect x="280" y="20" width="180" height="60" rx="8" fill="#2A8367" stroke="#1f624d" stroke-width="2"/>
  <text x="370" y="55" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">picker(_:didFinishPicking:)</text>

  <!-- Arrow to PHPickerResult -->
  <path d="M460 50 H490 L510 40 L510 60 L490 50 Z" fill="#2A8367" stroke="#2A8367" stroke-width="1"/>
  <text x="515" y="55" font-family="Arial, sans-serif" font-size="14" fill="#333">Returns</text>

  <!-- PHPickerResult -->
  <rect x="570" y="20" width="100" height="60" rx="8" fill="#F04B3E" stroke="#c03c32" stroke-width="2"/>
  <text x="620" y="55" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">PHPickerResult</text>

  <!-- Arrow from PHPickerResult to itemProvider -->
  <path d="M620 80 V110 L610 130 L630 130 L620 110 Z" fill="#2A8367" stroke="#2A8367" stroke-width="1"/>
  <text x="630" y="125" font-family="Arial, sans-serif" font-size="14" fill="#333">.itemProvider</text>

  <!-- NSItemProvider -->
  <rect x="570" y="150" width="140" height="60" rx="8" fill="#1565c0" stroke="#0e4a8c" stroke-width="2"/>
  <text x="640" y="185" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">NSItemProvider</text>

  <!-- Arrow from NSItemProvider to loadObject -->
  <path d="M640 210 V240 L630 260 L650 260 L640 240 Z" fill="#2A8367" stroke="#2A8367" stroke-width="1"/>
  <text x="650" y="255" font-family="Arial, sans-serif" font-size="14" fill="#333">.loadObject(ofClass:)</text>

  <!-- App Logic -->
  <rect x="570" y="270" width="140" height="60" rx="8" fill="#2A8367" stroke="#1f624d" stroke-width="2"/>
  <text x="640" y="305" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">App Logic/UI</text>

  <!-- Alternative path for multiple selections -->
  <path d="M400 80 V110 L390 130 L410 130 L400 110 Z" fill="#2A8367" stroke="#2A8367" stroke-width="1"/>
  <text x="410" y="125" font-family="Arial, sans-serif" font-size="14" fill="#333">Iterate results</text>
  <path d="M400 130 H570" stroke="#2A8367" stroke-width="1" fill="none"/>
</svg>
</div>

## Best Practices and Considerations

*   **Memory Management**: When dealing with `UIImage` or `Data` from `NSItemProvider`, especially for multiple selections or high-resolution assets, be mindful of memory usage. Process assets off the main thread and ensure you release memory when the assets are no longer needed.
*   **Error Handling**: Always include robust error handling for `itemProvider.loadObject`. Network issues, corrupted files, or permission changes could lead to loading failures.
*   **User Experience**: Provide clear feedback to the user, such as activity indicators while assets are loading, and inform them if access is denied or restricted. If your app requires full photo library access for a core feature, guide them to the Settings app to change permissions.
*   **Background Processing**: If you're performing heavy image processing or uploading after selection, consider using `URLSession` background tasks or `BackgroundTasks` framework to ensure the operation completes even if the app goes to the background.
*   **Limited Access (iOS 14+):** Users can grant "Limited Access" to their photo library, allowing your app to see only a subset of photos they explicitly selected. `PHPickerViewController` respects this. If your app needs to save to the library or interact with assets beyond those chosen in the picker, be aware of this limitation and gracefully handle scenarios where the user has granted limited access.

## Summary

`PHPickerViewController` is a powerful and privacy-centric API that has revolutionized how iOS apps interact with the user's photo and video library. By running in a separate process, it eliminates the need for your app to request broad photo library permissions, enhancing user trust and simplifying development. While `PHPicker` handles media selection, remember that explicit `PHPhotoLibrary` authorization is still necessary for actions like saving new content to the library or building a custom library browser. Embrace `PHPickerViewController` for a modern, secure, and user-friendly media selection experience in your iOS applications.

Happy Swifting!
