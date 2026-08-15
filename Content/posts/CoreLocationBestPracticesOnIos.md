---
title: Core Location Best Practices on iOS
date: 2026-08-15 09:18
description: Master Core Location on iOS with best practices for authorization, accuracy, power efficiency, and user experience in your Swift apps.
tags: Core Location, iOS, Development
---

# Core Location Best Practices on iOS

Location services are an integral part of many modern iOS applications, enabling features from navigation and weather apps to social networking and fitness trackers. Apple's Core Location framework provides robust tools for accessing GPS, Wi-Fi, and cellular data to determine a user's geographical position, orientation, and even proximity to iBeacons.

However, integrating Core Location effectively requires more than just calling a few methods. You need to consider user privacy, power consumption, accuracy requirements, and how to gracefully handle various states and permissions. In this article, we'll dive into the best practices for working with Core Location on iOS, helping you build location-aware apps that are efficient, reliable, and respectful of user privacy.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Core Location Authorization Flow">
  <title>Core Location Authorization Flow</title>

  <!-- Boxes -->
  <rect x="50" y="20" width="120" height="40" rx="5" ry="5" fill="#1565c0" stroke="#0d47a1" stroke-width="1"/>
  <text x="110" y="45" font-family="Arial" font-size="14" fill="white" text-anchor="middle">App Startup</text>

  <rect x="230" y="20" width="120" height="40" rx="5" ry="5" fill="#1565c0" stroke="#0d47a1" stroke-width="1"/>
  <text x="290" y="45" font-family="Arial" font-size="14" fill="white" text-anchor="middle">Check Auth Status</text>

  <rect x="410" y="20" width="120" height="40" rx="5" ry="5" fill="#2A8367" stroke="#1b5e20" stroke-width="1"/>
  <text x="470" y="45" font-family="Arial" font-size="14" fill="white" text-anchor="middle">Authorized?</text>

  <rect x="230" y="100" width="120" height="40" rx="5" ry="5" fill="#F04B3E" stroke="#c62828" stroke-width="1"/>
  <text x="290" y="125" font-family="Arial" font-size="14" fill="white" text-anchor="middle">Request Auth</text>

  <rect x="410" y="100" width="120" height="40" rx="5" ry="5" fill="#2A8367" stroke="#1b5e20" stroke-width="1"/>
  <text x="470" y="125" font-family="Arial" font-size="14" fill="white" text-anchor="middle">Start Location</text>

  <rect x="410" y="180" width="120" height="40" rx="5" ry="5" fill="#F04B3E" stroke="#c62828" stroke-width="1"/>
  <text x="470" y="205" font-family="Arial" font-size="14" fill="white" text-anchor="middle">Handle Denied</text>

  <!-- Arrows -->
  <line x1="170" y1="40" x2="230" y2="40" stroke="black" stroke-width="1" marker-end="url(#arrowhead)"/>
  <line x1="350" y1="40" x2="410" y2="40" stroke="black" stroke-width="1" marker-end="url(#arrowhead)"/>
  <line x1="470" y1="60" x2="470" y2="100" stroke="black" stroke-width="1" marker-end="url(#arrowhead)"/>
  <line x1="290" y1="60" x2="290" y2="100" stroke="black" stroke-width="1" marker-end="url(#arrowhead)"/>
  <line x1="350" y1="120" x2="410" y2="120" stroke="black" stroke-width="1" marker-end="url(#arrowhead)"/>
  <line x1="470" y1="140" x2="470" y2="180" stroke="black" stroke-width="1" marker-end="url(#arrowhead)"/>
  <line x1="410" y1="40" x2="350" y2="40" stroke="black" stroke-width="0" /> <!-- Invisible line for text -->
  <text x="380" y="30" font-family="Arial" font-size="12" fill="black" text-anchor="middle">No</text>
  <text x="380" y="55" font-family="Arial" font-size="12" fill="black" text-anchor="middle">Yes</text>
  <text x="485" y="85" font-family="Arial" font-size="12" fill="black" text-anchor="start">Yes</text>
  <text x="275" y="85" font-family="Arial" font-size="12" fill="black" text-anchor="end">No</text>
  <text x="485" y="165" font-family="Arial" font-size="12" fill="black" text-anchor="start">No</text>

  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="black" />
    </marker>
  </defs>
</svg>
</div>

## 1. Requesting and Managing Authorization

Before your app can access location services, you must request and obtain user authorization. This is a critical first step and involves configuring your `Info.plist` and using `CLLocationManager`.

### Info.plist Entries

You need to add specific privacy keys to your app's `Info.plist` file, along with user-facing descriptions explaining *why* your app needs location data. These messages are displayed to the user when the authorization prompt appears.

*   `NSLocationWhenInUseUsageDescription`: For accessing location when the app is in use (foreground).
*   `NSLocationAlwaysAndWhenInUseUsageDescription`: For accessing location both in the foreground and background. This key replaced `NSLocationAlwaysUsageDescription` in iOS 11.

Choose the least permissive authorization that meets your app's needs. If `WhenInUse` is sufficient, don't ask for `Always`. This builds trust with users.

```xml
<key>NSLocationWhenInUseUsageDescription</key>
<string>Your location is used to show nearby points of interest and provide local weather updates.</string>

<key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
<string>Your location is used to track your journey even when the app is in the background, to record your fitness activities.</string>
```

### Initializing CLLocationManager and Requesting Permission

The `CLLocationManager` class is your gateway to location services.

```swift
import CoreLocation

class LocationService: NSObject, CLLocationManagerDelegate {
    private let locationManager = CLLocationManager()
    var authorizationStatus: CLAuthorizationStatus {
        locationManager.authorizationStatus
    }

    override init() {
        super.init()
        locationManager.delegate = self
        // Set other configuration here, e.g., desiredAccuracy
    }

    func requestLocationAuthorization() {
        switch locationManager.authorizationStatus {
        case .notDetermined:
            // Request WhenInUse authorization
            locationManager.requestWhenInUseAuthorization()
            // Or request Always authorization if truly needed:
            // locationManager.requestAlwaysAuthorization()
        case .restricted, .denied:
            print("Location access restricted or denied. Prompt user to enable in settings.")
            // Guide the user to app settings
            if let url = URL(string: UIApplication.openSettingsURLString) {
                UIApplication.shared.open(url, options: [:], completionHandler: nil)
            }
        case .authorizedAlways, .authorizedWhenInUse:
            print("Location access already authorized.")
            // You can start location updates here or elsewhere
        @unknown default:
            fatalError("Unknown authorization status")
        }
    }

    // MARK: - CLLocationManagerDelegate

    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        // This delegate method is called whenever the authorization status changes.
        // It's crucial for reacting to user choices or system changes.
        switch manager.authorizationStatus {
        case .authorizedWhenInUse, .authorizedAlways:
            print("Location authorization granted.")
            // Start location updates or other location-aware features
        case .denied, .restricted:
            print("Location authorization denied or restricted.")
            // Handle the denial gracefully, e.g., disable location-dependent features
        case .notDetermined:
            print("Location authorization not determined.")
        @unknown default:
            fatalError("Unknown authorization status")
        }
    }

    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        if let clError = error as? CLError {
            switch clError.code {
            case .locationUnknown, .denied, .network:
                print("Location error: \(clError.localizedDescription)")
            default:
                print("Other location error: \(clError.localizedDescription)")
            }
        } else {
            print("Generic location error: \(error.localizedDescription)")
        }
    }
}
```

**Best Practice**: Always check the current authorization status before attempting to request it. Only prompt the user if the status is `.notDetermined`. If it's `.denied` or `.restricted`, guide them to your app's settings.

## 2. Configuring Location Services for Optimal Performance

Once authorized, you need to configure `CLLocationManager` to provide the right balance between accuracy and power consumption.

### Desired Accuracy

The `desiredAccuracy` property is crucial for power management. Requesting higher accuracy consumes significantly more power.

*   `.bestForNavigation`: Highest accuracy, uses GPS, consumes most power. Suitable for turn-by-turn navigation.
*   `.best`: Very high accuracy, generally within 10 meters.
*   `.nearestTenMeters`: Accuracy within 10 meters.
*   `.hundredMeters`: Accuracy within 100 meters.
*   `.kilometer`: Accuracy within a kilometer.
*   `.threeKilometers`: Accuracy within three kilometers, consumes least power.

**Best Practice**: Choose the lowest `desiredAccuracy` that meets your feature's needs. For example, a weather app might only need `.hundredMeters`, while a running tracker needs `.best`.

### Distance Filter

The `distanceFilter` property specifies the minimum distance (in meters) a device must move horizontally before a location update is generated.

```swift
locationManager.distanceFilter = 10 // Only update if device moves 10 meters or more
```

**Best Practice**: Set a `distanceFilter` to avoid unnecessary updates if your app doesn't need to react to every small movement. A value of `CLLocationManager.distanceFilterNone` (the default) means all movements, no matter how small, will trigger updates, which is very power-intensive.

### Pauses Location Updates Automatically

When `pausesLocationUpdatesAutomatically` is set to `true` (the default), Core Location can temporarily pause updates when the device is stationary for a period, saving power. Updates resume automatically when the device moves again.

```swift
locationManager.pausesLocationUpdatesAutomatically = true // Recommended
```

**Best Practice**: Keep `pausesLocationUpdatesAutomatically` set to `true` unless your app absolutely requires continuous updates even when the user is stationary (e.g., a highly precise indoor navigation system, which is rare).

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Core Location Accuracy vs. Power Consumption">
  <title>Core Location Accuracy vs. Power Consumption</title>

  <!-- Title -->
  <text x="300" y="25" font-family="Arial" font-size="18" fill="black" text-anchor="middle">Desired Accuracy vs. Power Consumption</text>

  <!-- Labels for Accuracy & Power -->
  <text x="100" y="70" font-family="Arial" font-size="14" fill="#1565c0" text-anchor="middle">Higher Accuracy</text>
  <text x="500" y="70" font-family="Arial" font-size="14" fill="#F04B3E" text-anchor="middle">Higher Power</text>

  <!-- Accuracy Levels -->
  <rect x="50" y="90" width="100" height="30" rx="5" ry="5" fill="#1565c0" stroke="#0d47a1" stroke-width="1"/>
  <text x="100" y="110" font-family="Arial" font-size="12" fill="white" text-anchor="middle">.bestForNavigation</text>

  <rect x="50" y="130" width="100" height="30" rx="5" ry="5" fill="#1565c0" stroke="#0d47a1" stroke-width="1"/>
  <text x="100" y="150" font-family="Arial" font-size="12" fill="white" text-anchor="middle">.best</text>

  <rect x="50" y="170" width="100" height="30" rx="5" ry="5" fill="#1565c0" stroke="#0d47a1" stroke-width="1"/>
  <text x="100" y="190" font-family="Arial" font-size="12" fill="white" text-anchor="middle">.nearestTenMeters</text>

  <rect x="250" y="90" width="100" height="30" rx="5" ry="5" fill="#2A8367" stroke="#1b5e20" stroke-width="1"/>
  <text x="300" y="110" font-family="Arial" font-size="12" fill="white" text-anchor="middle">.hundredMeters</text>

  <rect x="250" y="130" width="100" height="30" rx="5" ry="5" fill="#2A8367" stroke="#1b5e20" stroke-width="1"/>
  <text x="300" y="150" font-family="Arial" font-size="12" fill="white" text-anchor="middle">.kilometer</text>

  <rect x="250" y="170" width="100" height="30" rx="5" ry="5" fill="#2A8367" stroke="#1b5e20" stroke-width="1"/>
  <text x="300" y="190" font-family="Arial" font-size="12" fill="white" text-anchor="middle">.threeKilometers</text>

  <!-- Power Consumption Indicators -->
  <rect x="450" y="90" width="100" height="30" rx="5" ry="5" fill="#F04B3E" stroke="#c62828" stroke-width="1"/>
  <text x="500" y="110" font-family="Arial" font-size="12" fill="white" text-anchor="middle">Very High</text>

  <rect x="450" y="130" width="100" height="30" rx="5" ry="5" fill="#F04B3E" stroke="#c62828" stroke-width="1"/>
  <text x="500" y="150" font-family="Arial" font-size="12" fill="white" text-anchor="middle">High</text>

  <rect x="450" y="170" width="100" height="30" rx="5" ry="5" fill="#2A8367" stroke="#1b5e20" stroke-width="1"/>
  <text x="500" y="190" font-family="Arial" font-size="12" fill="white" text-anchor="middle">Low</text>

  <!-- Arrows -->
  <line x1="150" y1="105" x2="450" y2="105" stroke="black" stroke-width="1" marker-end="url(#arrowhead)"/>
  <line x1="150" y1="145" x2="450" y2="145" stroke="black" stroke-width="1" marker-end="url(#arrowhead)"/>
  <line x1="150" y1="185" x2="450" y2="185" stroke="black" stroke-width="1" marker-end="url(#arrowhead)"/>
  <line x1="350" y1="105" x2="450" y2="105" stroke="black" stroke-width="0" /> <!-- Invisible line for text -->
  <text x="400" y="100" font-family="Arial" font-size="12" fill="black" text-anchor="middle">Uses</text>
  <text x="400" y="140" font-family="Arial" font-size="12" fill="black" text-anchor="middle">Uses</text>
  <text x="400" y="180" font-family="Arial" font-size="12" fill="black" text-anchor="middle">Uses</text>

  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="black" />
    </marker>
  </defs>
</svg>
</div>

## 3. Managing Location Updates Efficiently

Receiving location updates is straightforward, but managing them to be power-efficient and responsive is key.

### Starting and Stopping Updates

Always start and stop location updates explicitly.

```swift
extension LocationService {
    func startUpdatingLocation() {
        guard locationManager.authorizationStatus == .authorizedWhenInUse ||
              locationManager.authorizationStatus == .authorizedAlways else {
            print("Cannot start updates: Not authorized.")
            return
        }
        locationManager.startUpdatingLocation()
        print("Started continuous location updates.")
    }

    func stopUpdatingLocation() {
        locationManager.stopUpdatingLocation()
        print("Stopped continuous location updates.")
    }

    // Delegate method for receiving updates
    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let latestLocation = locations.last else { return }

        // Filter out old or inaccurate locations
        let age = -latestLocation.timestamp.timeIntervalSinceNow
        if age > 10 { // Location is older than 10 seconds
            print("Ignoring stale location: \(age)s old.")
            return
        }
        if latestLocation.horizontalAccuracy > 100 { // Accuracy worse than 100 meters
            print("Ignoring inaccurate location: horizontal accuracy \(latestLocation.horizontalAccuracy)m.")
            return
        }

        print("Received new location: \(latestLocation.coordinate.latitude), \(latestLocation.coordinate.longitude) (Accuracy: \(latestLocation.horizontalAccuracy)m)")

        // Stop updates if you only need a single, accurate location
        // stopUpdatingLocation()
    }
}
```

**Best Practice**: Stop updates as soon as you have the location data you need or when the app moves to the background (if `WhenInUse` authorization is used). Continuous updates drain battery rapidly.

### One-Shot Location Requests

For scenarios where you only need a single, current location, use `requestLocation()`. This method is more power-efficient than `startUpdatingLocation()` because Core Location automatically stops updates after delivering a valid location.

```swift
extension LocationService {
    func requestSingleLocation() {
        guard locationManager.authorizationStatus == .authorizedWhenInUse ||
              locationManager.authorizationStatus == .authorizedAlways else {
            print("Cannot request single location: Not authorized.")
            return
        }
        locationManager.requestLocation() // Triggers didUpdateLocations once
        print("Requested single location.")
    }
}
```

### Background Location Updates

If your app truly needs to track location in the background (e.g., a fitness app), you must:
1.  Request `Always` authorization.
2.  Enable the "Location updates" background mode in your app's capabilities.
3.  Set `allowsBackgroundLocationUpdates = true` on `CLLocationManager`.

```swift
// In LocationService init or setup
locationManager.allowsBackgroundLocationUpdates = true
```

**Best Practice**: Only enable background location updates if absolutely necessary and only after requesting `Always` authorization. Misusing this can lead to app rejections and poor user experience.

### Significant Location Changes

For less frequent background location monitoring, consider `startMonitoringSignificantLocationChanges()`. This mode delivers updates only when the device moves a significant distance (typically several hundred meters) and is far more power-efficient. It can even relaunch your app in the background if it was terminated.

```swift
extension LocationService {
    func startMonitoringSignificantLocationChanges() {
        guard locationManager.authorizationStatus == .authorizedAlways else {
            print("Cannot start significant location changes: Requires Always authorization.")
            return
        }
        locationManager.startMonitoringSignificantLocationChanges()
        print("Started monitoring significant location changes.")
    }

    func stopMonitoringSignificantLocationChanges() {
        locationManager.stopMonitoringSignificantLocationChanges()
        print("Stopped monitoring significant location changes.")
    }
}
```

Here's an ASCII diagram illustrating different location update strategies:

```
┌──────────────────────────┐    ┌──────────────────────────────┐    ┌──────────────────────────┐
│  Continuous (start/stop) │    │  Significant Changes         │    │  One-Shot (requestLocation)│
│  - High Accuracy          │    │  - Lower Accuracy            │    │  - Single Update           │
│  - High Power             │    │  - Low Power                 │    │  - Low Power               │
│  - Foreground/Background* │    │  - Background (relaunches)   │    │  - Foreground Only         │
└──────────────────────────┘    └──────────────────────────────┘    └──────────────────────────┘
      ▲                           ▲                                      ▲
      │                           │                                      │
      │ (Requires 'Always' for     │ (Requires 'Always' auth,            │ (Foreground 'WhenInUse'
      │  background updates)       │  Background mode enabled)          │  or 'Always' auth)
      ▼                           ▼                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       CLLocationManager                                         │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

*Continuous background updates require 'Always' authorization and background mode capability.
```

## 4. Geocoding and Reverse Geocoding

`CLGeocoder` is used to convert between geographical coordinates (latitude and longitude) and human-readable placemarks (addresses, city names, etc.).

```swift
import CoreLocation

class GeocodingService {
    private let geocoder = CLGeocoder()

    func reverseGeocode(location: CLLocation, completion: @escaping (CLPlacemark?, Error?) -> Void) {
        geocoder.reverseGeocodeLocation(location) { placemarks, error in
            if let error = error {
                print("Reverse geocoding failed with error: \(error.localizedDescription)")
                completion(nil, error)
                return
            }
            completion(placemarks?.first, nil)
        }
    }

    func geocode(addressString: String, completion: @escaping ([CLPlacemark]?, Error?) -> Void) {
        geocoder.geocodeAddressString(addressString) { placemarks, error in
            if let error = error {
                print("Geocoding failed with error: \(error.localizedDescription)")
                completion(nil, error)
                return
            }
            completion(placemarks, nil)
        }
    }
}
```

**Best Practice**: Geocoding requests are network operations. Handle potential errors and consider rate limits if performing many requests. Cache results where appropriate.

## 5. Testing Core Location Features

Testing location-based features can be tricky with real devices. Xcode provides excellent tools for simulation.

*   **Xcode Schemes**: In your active scheme's Run settings, under "Options," you can set a default location or even use a GPX file.
*   **GPX Files**: These XML files define a series of waypoints or a track, allowing you to simulate movement over time. You can create them manually or record them from a real device.
*   **Debug Bar**: While running your app, the Debug Bar (at the bottom of Xcode) offers a location icon to change the simulated location on the fly.

**Best Practice**: Utilize Xcode's location simulation capabilities extensively during development to test different scenarios (e.g., moving, stationary, denied permission, various accuracies).

## 6. Privacy and User Experience

Location data is highly sensitive. Respecting user privacy and providing a transparent experience is paramount.

*   **Clear Usage Descriptions**: Ensure your `Info.plist` descriptions are clear, concise, and accurately explain *why* you need location access. Vague descriptions can lead to user distrust and even app rejection.
*   **Contextual Authorization Requests**: Don't request location authorization immediately upon app launch unless it's absolutely essential for the app's core functionality. Instead, wait until the user attempts to use a feature that requires location. This provides context and makes the request more understandable.
*   **Handle Denied Status Gracefully**: If a user denies location access, don't just disable the feature silently. Inform them that the feature requires location, and perhaps provide a button to open app settings where they can grant permission.
*   **Informational UI**: If your app is tracking location in the background, consider providing a small persistent notification or UI element to remind the user, enhancing transparency.

## Summary

Core Location is a powerful framework, but its effective use requires careful consideration of authorization, power consumption, and user experience. By implementing the best practices outlined here – from choosing the right authorization level and accuracy settings to efficiently managing updates and providing clear privacy explanations – you can build robust, battery-friendly, and user-centric location-aware applications. Always prioritize the user's privacy and device battery life, and your app will stand out.

Happy Swifting!
