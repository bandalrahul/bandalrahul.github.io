---
title: Building a Camera Feature with AVFoundation on iOS
date: 2026-08-17 09:33
description: Dive into AVFoundation to build a custom camera on iOS, covering permissions, session setup, live preview, and photo capture in Swift.
tags: AVFoundation, iOS, Development
---

# Building a Camera Feature with AVFoundation on iOS

Modern iOS applications often require more than just static content; many leverage the device's powerful camera for features like scanning QR codes, taking profile pictures, or creating augmented reality experiences. While `UIImagePickerController` offers a quick way to access the camera, it provides limited customization. For full control over the camera experience, from live preview to advanced capture settings, `AVFoundation` is the framework you need.

`AVFoundation` is Apple's comprehensive framework for working with time-based audiovisual media. It's powerful, but can also be intimidating due to its granular control. In this article, we'll demystify `AVFoundation` by walking through the essential steps to build a basic custom camera feature in your iOS app, capable of displaying a live preview and capturing photos.

We'll cover:
1.  Requesting camera permissions.
2.  Setting up an `AVCaptureSession`.
3.  Displaying a live camera preview.
4.  Capturing still photos.
5.  Switching between front and back cameras.
6.  Managing the session lifecycle.

Let's dive in!

## 1. Requesting Camera Permissions

Before your app can access the camera, you must request user permission. This involves two steps:
1.  Adding a usage description to your `Info.plist`.
2.  Programmatically requesting access.

First, open your `Info.plist` file (or your target's Info tab) and add the `Privacy - Camera Usage Description` key (or `NSCameraUsageDescription` in source code view) with a descriptive string explaining why your app needs camera access. For example: "This app needs camera access to take photos."

Next, you'll request access at runtime. It's good practice to do this before attempting to use the camera.

```swift
import AVFoundation
import UIKit

class CameraViewController: UIViewController {

    override func viewDidLoad() {
        super.viewDidLoad()
        checkCameraPermissions()
    }

    private func checkCameraPermissions() {
        switch AVCaptureDevice.authorizationStatus(for: .video) {
        case .authorized:
            // The user has previously granted access to the camera.
            setupCameraSession()
        case .notDetermined:
            // The user has not yet been asked for camera access.
            AVCaptureDevice.requestAccess(for: .video) { [weak self] granted in
                DispatchQueue.main.async {
                    if granted {
                        self?.setupCameraSession()
                    } else {
                        self?.handlePermissionDenied()
                    }
                }
            }
        case .denied, .restricted:
            // The user has previously denied or restricted camera access.
            handlePermissionDenied()
        @unknown default:
            fatalError("Unknown authorization status for camera.")
        }
    }

    private func handlePermissionDenied() {
        let alert = UIAlertController(
            title: "Camera Access Denied",
            message: "Please enable camera access for this app in Settings to use this feature.",
            preferredStyle: .alert
        )
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }

    // ... rest of the camera setup
}
```

## 2. Setting Up the Capture Session

The heart of `AVFoundation`'s camera functionality is `AVCaptureSession`. It coordinates the flow of data from inputs (like the camera) to outputs (like photo or video recorders).

We'll need:
*   An `AVCaptureSession` instance.
*   An `AVCaptureDeviceInput` to feed camera data into the session.
*   An `AVCapturePhotoOutput` to capture still images.

It's crucial to perform all `AVCaptureSession` configuration on a dedicated serial `DispatchQueue` to avoid blocking the main thread and ensure thread safety.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="AVCaptureSession Setup Flow">
  <title>AVCaptureSession Setup Flow</title>
  <!-- Background rect -->
  <rect x="0" y="0" width="600" height="220" fill="#f9f9f9" rx="10" ry="10"/>

  <!-- Nodes -->
  <rect x="20" y="20" width="160" height="60" rx="8" ry="8" fill="#1565c0" stroke="#0e4a8c" stroke-width="2"/>
  <text x="100" y="55" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">AVCaptureSession</text>

  <rect x="220" y="20" width="160" height="60" rx="8" ry="8" fill="#2A8367" stroke="#1c5d49" stroke-width="2"/>
  <text x="300" y="55" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">AVCaptureDeviceInput</text>

  <rect x="420" y="20" width="160" height="60" rx="8" ry="8" fill="#F04B3E" stroke="#b3382e" stroke-width="2"/>
  <text x="500" y="55" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">AVCapturePhotoOutput</text>

  <rect x="220" y="140" width="160" height="60" rx="8" ry="8" fill="#1565c0" stroke="#0e4a8c" stroke-width="2"/>
  <text x="300" y="175" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">AVCaptureVideoPreviewLayer</text>

  <!-- Arrows -->
  <line x1="180" y1="50" x2="220" y2="50" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <line x1="380" y1="50" x2="420" y2="50" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <line x1="100" y1="80" x2="100" y2="150" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <line x1="100" y1="150" x2="220" y2="170" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>

  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
    </marker>
  </defs>

  <!-- Labels for arrows -->
  <text x="200" y="45" font-family="Arial, sans-serif" font-size="12" fill="#333" text-anchor="middle">Add Input</text>
  <text x="400" y="45" font-family="Arial, sans-serif" font-size="12" fill="#333" text-anchor="middle">Add Output</text>
  <text x="160" y="130" font-family="Arial, sans-serif" font-size="12" fill="#333" text-anchor="middle">Connect to</text>
</svg>
</div>

```swift
class CameraViewController: UIViewController {
    private var captureSession: AVCaptureSession?
    private var photoOutput: AVCapturePhotoOutput?
    private var previewLayer: AVCaptureVideoPreviewLayer?

    private let sessionQueue = DispatchQueue(label: "session queue")

    // ... (checkCameraPermissions and handlePermissionDenied methods)

    private func setupCameraSession() {
        captureSession = AVCaptureSession()

        sessionQueue.async { [weak self] in
            guard let self = self, let captureSession = self.captureSession else { return }

            captureSession.beginConfiguration()
            defer { captureSession.commitConfiguration() } // Ensure commitConfiguration is called

            // 1. Add input (camera device)
            guard let videoDevice = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back) else {
                print("Failed to get video device.")
                return
            }
            guard let videoInput = try? AVCaptureDeviceInput(device: videoDevice) else {
                print("Failed to create video input.")
                return
            }
            if captureSession.canAddInput(videoInput) {
                captureSession.addInput(videoInput)
            } else {
                print("Could not add video input to the session.")
                return
            }
            
            // Store the current input for camera switching
            self.currentVideoInput = videoInput

            // 2. Add output (photo output)
            self.photoOutput = AVCapturePhotoOutput()
            self.photoOutput?.isHighResolutionCaptureEnabled = true // Enable high resolution photos
            if captureSession.canAddOutput(self.photoOutput!) {
                captureSession.addOutput(self.photoOutput!)
            } else {
                print("Could not add photo output to the session.")
                return
            }

            // 3. Setup preview layer (on main thread as it's UI)
            DispatchQueue.main.async {
                self.setupPreviewLayer(session: captureSession)
            }
        }
    }
}
```

## 3. Displaying the Camera Preview

To show the live camera feed, you'll use an `AVCaptureVideoPreviewLayer`. This is a `CALayer` subclass that displays video from a capture session. You'll add it as a sublayer to one of your `UIView`'s layers.

```swift
class CameraViewController: UIViewController {
    // ... (previous properties and methods)

    private func setupPreviewLayer(session: AVCaptureSession) {
        previewLayer = AVCaptureVideoPreviewLayer(session: session)
        previewLayer?.videoGravity = .resizeAspectFill // Fills the layer bounds, cropping if necessary
        previewLayer?.connection?.videoOrientation = .portrait // Ensure correct orientation

        // Add the preview layer to your view's layer hierarchy
        if let previewLayer = previewLayer {
            view.layer.insertSublayer(previewLayer, at: 0) // Add it at index 0 so other UI elements are on top
            previewLayer.frame = view.bounds // Match the view's bounds
        }

        // Start the session (important!)
        sessionQueue.async { [weak self] in
            self?.captureSession?.startRunning()
        }
    }

    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        previewLayer?.frame = view.bounds // Update frame on rotation/layout changes
    }
}
```

## 4. Capturing a Photo

With the session running and preview visible, capturing a photo is straightforward using `AVCapturePhotoOutput`. You'll configure `AVCapturePhotoSettings` and then call `capturePhoto(with:delegate:)`. You'll also need to conform to `AVCapturePhotoCaptureDelegate` to receive the captured photo data.

```swift
import Photos // For saving to photo library

class CameraViewController: UIViewController, AVCapturePhotoCaptureDelegate {
    // ... (previous properties and methods)

    private var currentVideoInput: AVCaptureDeviceInput? // Keep track of the current camera input

    // Call this method when a "capture" button is tapped
    @IBAction func captureButtonTapped(_ sender: UIButton) {
        sessionQueue.async { [weak self] in
            guard let self = self, let photoOutput = self.photoOutput else { return }

            let photoSettings = AVCapturePhotoSettings()
            photoSettings.flashMode = .off // Or .on, .auto
            
            // If you want high resolution, ensure `isHighResolutionCaptureEnabled` is true on photoOutput
            if photoOutput.isHighResolutionCaptureEnabled {
                photoSettings.isHighResolutionPhotoEnabled = true
            }

            // Capture the photo using the delegate
            photoOutput.capturePhoto(with: photoSettings, delegate: self)
        }
    }

    // MARK: - AVCapturePhotoCaptureDelegate

    func photoOutput(_ output: AVCapturePhotoOutput, didFinishProcessingPhoto photo: AVCapturePhoto, error: Error?) {
        if let error = error {
            print("Error capturing photo: \(error.localizedDescription)")
            return
        }

        guard let imageData = photo.fileDataRepresentation() else {
            print("Could not get image data from photo.")
            return
        }

        // Process the image data, e.g., save it to the photo library or display it
        UIImage(data: imageData).map { capturedImage in
            DispatchQueue.main.async {
                // For demonstration, let's just print the size and save to Photos
                print("Captured image size: \(capturedImage.size)")
                
                // Request permission to save to photo library
                PHPhotoLibrary.requestAuthorization(for: .addOnly) { status in
                    if status == .authorized {
                        PHPhotoLibrary.shared().performChanges({
                            PHAssetChangeRequest.creationRequestForAsset(from: capturedImage)
                        }) { success, error in
                            if let error = error {
                                print("Error saving photo to library: \(error.localizedDescription)")
                            } else {
                                print("Photo saved successfully!")
                            }
                        }
                    } else {
                        print("Photo library access denied.")
                    }
                }
            }
        }
    }
}
```

## 5. Switching Cameras (Front/Back)

Switching between front and back cameras involves finding the desired device, removing the current input, and adding the new input to the `AVCaptureSession`. Remember to perform these operations within `beginConfiguration()` and `commitConfiguration()` blocks on your `sessionQueue`.

```swift
class CameraViewController: UIViewController {
    // ... (previous properties and methods)

    @IBAction func switchCameraButtonTapped(_ sender: UIButton) {
        sessionQueue.async { [weak self] in
            guard let self = self, let captureSession = self.captureSession,
                  let currentInput = self.currentVideoInput else { return }

            captureSession.beginConfiguration()
            defer { captureSession.commitConfiguration() }

            // Determine the current camera position and find the opposite
            let currentPosition = currentInput.device.position
            let newPosition: AVCaptureDevice.Position = (currentPosition == .back) ? .front : .back

            // Find the new camera device
            guard let newVideoDevice = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: newPosition) else {
                print("Could not find camera for position: \(newPosition.rawValue)")
                return
            }

            // Create new input
            guard let newVideoInput = try? AVCaptureDeviceInput(device: newVideoDevice) else {
                print("Could not create new video input.")
                return
            }

            // Remove the current input and add the new one
            captureSession.removeInput(currentInput)
            if captureSession.canAddInput(newVideoInput) {
                captureSession.addInput(newVideoInput)
                self.currentVideoInput = newVideoInput // Update current input
            } else {
                print("Could not add new video input to the session. Re-adding original input.")
                captureSession.addInput(currentInput) // Fallback to original input
            }
        }
    }
}
```

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 700 180" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Camera Switch Flow Diagram">
  <title>Camera Switch Flow Diagram</title>
  <!-- Background rect -->
  <rect x="0" y="0" width="700" height="180" fill="#f9f9f9" rx="10" ry="10"/>

  <!-- Nodes -->
  <rect x="20" y="60" width="120" height="60" rx="8" ry="8" fill="#1565c0" stroke="#0e4a8c" stroke-width="2"/>
  <text x="80" y="95" font-family="Arial, sans-serif" font-size="14" fill="white" text-anchor="middle">Tap Switch</text>

  <rect x="160" y="60" width="120" height="60" rx="8" ry="8" fill="#2A8367" stroke="#1c5d49" stroke-width="2"/>
  <text x="220" y="95" font-family="Arial, sans-serif" font-size="14" fill="white" text-anchor="middle">Begin Config</text>

  <rect x="300" y="60" width="120" height="60" rx="8" ry="8" fill="#F04B3E" stroke="#b3382e" stroke-width="2"/>
  <text x="360" y="95" font-family="Arial, sans-serif" font-size="14" fill="white" text-anchor="middle">Remove Input</text>

  <rect x="440" y="60" width="120" height="60" rx="8" ry="8" fill="#2A8367" stroke="#1c5d49" stroke-width="2"/>
  <text x="500" y="95" font-family="Arial, sans-serif" font-size="14" fill="white" text-anchor="middle">Add New Input</text>

  <rect x="580" y="60" width="100" height="60" rx="8" ry="8" fill="#1565c0" stroke="#0e4a8c" stroke-width="2"/>
  <text x="630" y="95" font-family="Arial, sans-serif" font-size="14" fill="white" text-anchor="middle">Commit Config</text>

  <!-- Arrows -->
  <line x1="140" y1="90" x2="160" y2="90" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <line x1="280" y1="90" x2="300" y2="90" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <line x1="420" y1="90" x2="440" y2="90" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <line x1="560" y1="90" x2="580" y2="90" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>

  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
    </marker>
  </defs>
</svg>
</div>

## 6. Basic Camera UI

To make our camera usable, we'll need a simple UI. For a `UIViewController` managing the camera, you might lay it out like this:

```
┌───────────────────────────────────────┐
│              Camera View              │
│ ┌───────────────────────────────────┐ │
│ │                                   │ │
│ │  AVCaptureVideoPreviewLayer       │ │
│ │  (filling this area)              │ │
│ │                                   │ │
│ └───────────────────────────────────┘ │
│                                       │
│ ┌───────────────┐ ┌─────────────────┐ │
│ │ Switch Camera │ │ Capture Photo   │ │
│ └───────────────┘ └─────────────────┘ │
└───────────────────────────────────────┘
```

This ASCII diagram represents a `UIViewController`'s view. The `AVCaptureVideoPreviewLayer` covers most of the screen, providing the live feed. At the bottom, we have two buttons: one to switch between front/back cameras, and another to capture a photo. These buttons would be connected to the `@IBAction` methods we defined earlier.

## 7. Handling Session Lifecycle

Starting and stopping the `AVCaptureSession` correctly is vital for performance and battery life.

*   **`startRunning()`**: Call this when your camera view controller appears or is about to become active. This should be done on your `sessionQueue`.
*   **`stopRunning()`**: Call this when your camera view controller disappears or becomes inactive. This also needs to be on your `sessionQueue`.

```swift
class CameraViewController: UIViewController {
    // ... (previous properties and methods)

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        sessionQueue.async { [weak self] in
            self?.captureSession?.startRunning()
        }
    }

    override func viewWillDisappear(_ animated: Bool) {
        sessionQueue.async { [weak self] in
            self?.captureSession?.stopRunning()
        }
        super.viewWillDisappear(animated)
    }
}
```

It's also good practice to observe `AVCaptureSession.wasInterruptedNotification` and `AVCaptureSession.interruptionEndedNotification` to handle scenarios where your app's camera session might be temporarily interrupted (e.g., by a phone call).

## Summary

Building a custom camera feature with `AVFoundation` gives you immense power and flexibility compared to `UIImagePickerController`. We've covered the fundamental steps: requesting permissions, setting up the `AVCaptureSession` with inputs and outputs, displaying a live preview, capturing photos, and even switching cameras.

While this article provides a solid foundation, `AVFoundation` offers much more, including video recording, advanced focus and exposure controls, depth data, and more. Remember to always handle permissions gracefully, perform session operations on a background queue, and manage the session's lifecycle correctly to provide a robust and efficient camera experience.

Happy Swifting!
