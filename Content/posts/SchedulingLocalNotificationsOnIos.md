---
title: Scheduling Local Notifications on iOS
date: 2026-08-22 09:19
description: Learn how to implement and schedule local notifications on iOS using UserNotifications framework, covering authorization, content, triggers, and delegate methods.
tags: Notifications, iOS, Development
---

# Scheduling Local Notifications on iOS

Notifications are a cornerstone of modern mobile app engagement. They allow your app to deliver timely and relevant information to users, even when the app isn't actively in use. While push notifications (remote notifications) rely on a server to send alerts, **local notifications** are entirely managed by your iOS device. They are perfect for reminders, alarms, or any time-sensitive information that can be generated directly by your app without needing an internet connection.

In this article, we'll dive deep into the `UserNotifications` framework, the powerful API Apple provides for handling both local and remote notifications. We'll cover everything from requesting user permission to crafting rich notification content, setting various triggers, and handling user interactions. By the end, you'll be able to confidently integrate robust local notification capabilities into your iOS applications.

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Local Notification Workflow Overview">
  <title>Local Notification Workflow Overview</title>

  <!-- Styles for elements -->
  <style>
    .box { fill: #fff; stroke: #1565c0; stroke-width: 2; }
    .text { font-family: sans-serif; font-size: 14px; fill: #333; }
    .arrow { stroke: #2A8367; stroke-width: 2; marker-end: url(#arrowhead); }
    .header { font-weight: bold; font-size: 16px; }
  </style>

  <!-- Arrowhead definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#2A8367" />
    </marker>
  </defs>

  <!-- Step 1: Request Authorization -->
  <rect x="20" y="50" width="120" height="60" rx="8" ry="8" class="box"/>
  <text x="80" y="75" text-anchor="middle" class="text header">Request</text>
  <text x="80" y="95" text-anchor="middle" class="text">Authorization</text>

  <!-- Step 2: Create Content & Trigger -->
  <rect x="180" y="30" width="120" height="40" rx="8" ry="8" class="box"/>
  <text x="240" y="55" text-anchor="middle" class="text">UNNotificationContent</text>
  <rect x="180" y="90" width="120" height="40" rx="8" ry="8" class="box"/>
  <text x="240" y="115" text-anchor="middle" class="text">UNNotificationTrigger</text>

  <!-- Step 3: Create Request -->
  <rect x="340" y="50" width="120" height="60" rx="8" ry="8" class="box"/>
  <text x="400" y="75" text-anchor="middle" class="text header">UNNotificationRequest</text>
  <text x="400" y="95" text-anchor="middle" class="text">(Content + Trigger)</text>

  <!-- Step 4: Add Request to Center -->
  <rect x="500" y="50" width="80" height="60" rx="8" ry="8" class="box" fill="#2A8367"/>
  <text x="540" y="75" text-anchor="middle" class="text header" fill="#fff">Schedule</text>
  <text x="540" y="95" text-anchor="middle" class="text" fill="#fff">Notification</text>

  <!-- Arrows -->
  <line x1="140" y1="80" x2="180" y2="80" class="arrow"/>
  <line x1="300" y1="60" x2="340" y2="60" class="arrow"/>
  <line x1="300" y1="100" x2="340" y2="100" class="arrow"/>
  <path d="M300 80 Q 320 80, 320 70 L 320 60" class="arrow" style="stroke: none; fill: none;"/> <!-- Invisible path for smooth curve -->
  <path d="M300 80 Q 320 80, 320 90 L 320 100" class="arrow" style="stroke: none; fill: none;"/> <!-- Invisible path for smooth curve -->
  <line x1="460" y1="80" x2="500" y2="80" class="arrow"/>

  <!-- Footer text -->
  <text x="300" y="190" text-anchor="middle" class="text" fill="#1565c0">UserNotifications Framework</text>
</svg>
</div>

## Requesting User Authorization

Before your app can schedule and present notifications, you must ask the user for permission. This is a critical privacy control on iOS. You specify the types of alerts you want to use (e.g., sound, badge, alert UI).

To request authorization, you'll use the shared `UNUserNotificationCenter` instance:

```swift
import UserNotifications

class NotificationManager {

    static let shared = NotificationManager()

    func requestAuthorization() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { granted, error in
            if granted {
                print("Notification permission granted.")
            } else if let error = error {
                print("Notification permission denied: \(error.localizedDescription)")
            } else {
                print("Notification permission denied.")
            }
        }
    }

    // You might want to check current settings
    func getNotificationSettings() {
        UNUserNotificationCenter.current().getNotificationSettings { settings in
            print("Notification settings: \(settings.authorizationStatus.rawValue)")
            // authorizationStatus can be .notDetermined, .denied, .authorized, .provisional, .ephemeral
            guard settings.authorizationStatus == .authorized else { return }
            // Check other settings like sound, badge, alert
            if settings.alertSetting == .enabled {
                print("Alerts are enabled.")
            }
        }
    }
}
```

You should call `requestAuthorization()` at an appropriate time in your app's lifecycle, typically when the user is about to interact with a feature that relies on notifications, or during an onboarding flow. Avoid requesting it immediately on app launch unless notifications are central to the app's functionality, as users might deny it if they don't understand the context.

## Anatomy of a Local Notification

A local notification is composed of three main parts: content, trigger, and request.

### 1. Notification Content (`UNMutableNotificationContent`)

This defines what the user sees and hears. It's encapsulated by `UNMutableNotificationContent` (or `UNNotificationContent` if you don't need to modify it).

```swift
let content = UNMutableNotificationContent()
content.title = "Daily Reminder"
content.subtitle = "Don't forget your task!"
content.body = "It's time to check off your to-do list for today."
content.sound = .default // Play the default notification sound
content.badge = 1 // Increment the app icon badge count

// You can also add userInfo for custom data
content.userInfo = ["customData": "someValue", "notificationType": "dailyReminder"]

// For rich notifications, you can add attachments (images, video, audio)
if let imageUrl = Bundle.main.url(forResource: "exampleImage", withExtension: "png"),
   let attachment = try? UNNotificationAttachment(identifier: "image", url: imageUrl, options: nil) {
    content.attachments = [attachment]
}
```

### 2. Notification Trigger (`UNNotificationTrigger`)

The trigger determines *when* the notification should be delivered. iOS provides several types of triggers:

*   **Time Interval Trigger (`UNTimeIntervalNotificationTrigger`)**: Delivers a notification after a specified time interval. Can be repeating.
*   **Calendar Trigger (`UNCalendarNotificationTrigger`)**: Delivers a notification at a specific date and time, or on a recurring schedule (e.g., every Tuesday at 9 AM).
*   **Location Trigger (`UNLocationNotificationTrigger`)**: Delivers a notification when the user enters or exits a specified geographic region. Requires Core Location permissions.

```swift
// Example 1: Time Interval Trigger (5 seconds from now, non-repeating)
let timeIntervalTrigger = UNTimeIntervalNotificationTrigger(timeInterval: 5, repeats: false)

// Example 2: Calendar Trigger (Every day at 9:00 AM)
var dateComponents = DateComponents()
dateComponents.hour = 9
dateComponents.minute = 0
let calendarTrigger = UNCalendarNotificationTrigger(dateMatching: dateComponents, repeats: true)

// Example 3: Location Trigger (when entering a specific region)
// Requires Core Location import and authorization
// let region = CLCircularRegion(center: CLLocationCoordinate2D(latitude: 37.332, longitude: -122.031), radius: 500, identifier: "ApplePark")
// region.notifyOnEntry = true
// region.notifyOnExit = false
// let locationTrigger = UNLocationNotificationTrigger(region: region, repeats: false)
```

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 700 200" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Comparison of UNNotificationTrigger Types">
  <title>Comparison of UNNotificationTrigger Types</title>

  <style>
    .trigger-box { fill: #fff; stroke: #1565c0; stroke-width: 2; border-radius: 8px; }
    .trigger-title { font-family: sans-serif; font-size: 16px; font-weight: bold; fill: #1565c0; }
    .trigger-desc { font-family: sans-serif; font-size: 13px; fill: #333; }
    .icon-text { font-family: "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji", sans-serif; font-size: 28px; }
  </style>

  <!-- Time Interval Trigger -->
  <rect x="20" y="20" width="200" height="160" rx="10" ry="10" class="trigger-box"/>
  <text x="120" y="45" text-anchor="middle" class="trigger-title">Time Interval</text>
  <text x="120" y="85" text-anchor="middle" class="icon-text">⏳</text>
  <text x="120" y="125" text-anchor="middle" class="trigger-desc">After a fixed duration</text>
  <text x="120" y="145" text-anchor="middle" class="trigger-desc">(e.g., 5 seconds, 1 minute)</text>

  <!-- Calendar Trigger -->
  <rect x="250" y="20" width="200" height="160" rx="10" ry="10" class="trigger-box"/>
  <text x="350" y="45" text-anchor="middle" class="trigger-title">Calendar</text>
  <text x="350" y="85" text-anchor="middle" class="icon-text">📅</text>
  <text x="350" y="125" text-anchor="middle" class="trigger-desc">At specific date/time</text>
  <text x="350" y="145" text-anchor="middle" class="trigger-desc">(e.g., daily 9 AM, every Monday)</text>

  <!-- Location Trigger -->
  <rect x="480" y="20" width="200" height="160" rx="10" ry="10" class="trigger-box"/>
  <text x="580" y="45" text-anchor="middle" class="trigger-title">Location</text>
  <text x="580" y="85" text-anchor="middle" class="icon-text">📍</text>
  <text x="580" y="125" text-anchor="middle" class="trigger-desc">Upon entering/exiting a region</text>
  <text x="580" y="145" text-anchor="middle" class="trigger-desc">(Requires Core Location)</text>
</svg>
</div>

### 3. Notification Request (`UNNotificationRequest`)

The request combines your content and trigger into a single object that you submit to the notification center. Each request needs a unique identifier. This identifier is crucial for managing (updating or removing) specific notifications later.

```swift
let requestIdentifier = UUID().uuidString // A unique identifier for this notification
let request = UNNotificationRequest(identifier: requestIdentifier, content: content, trigger: timeIntervalTrigger)

// Or with the calendar trigger:
// let request = UNNotificationRequest(identifier: requestIdentifier, content: content, trigger: calendarTrigger)
```

## Scheduling the Notification

Once you have a `UNNotificationRequest`, you add it to the `UNUserNotificationCenter` to schedule its delivery.

```swift
func scheduleNotification(content: UNMutableNotificationContent, trigger: UNNotificationTrigger, identifier: String) {
    let request = UNNotificationRequest(identifier: identifier, content: content, trigger: trigger)

    UNUserNotificationCenter.current().add(request) { error in
        if let error = error {
            print("Error scheduling notification: \(error.localizedDescription)")
        } else {
            print("Notification scheduled successfully with ID: \(identifier)")
        }
    }
}

// Example usage:
let content = UNMutableNotificationContent()
content.title = "Workout Time!"
content.body = "It's 5 PM, time for your daily workout."
content.sound = .default

var dateComponents = DateComponents()
dateComponents.hour = 17 // 5 PM
dateComponents.minute = 0
let trigger = UNCalendarNotificationTrigger(dateMatching: dateComponents, repeats: true)

NotificationManager.shared.scheduleNotification(
    content: content,
    trigger: trigger,
    identifier: "dailyWorkoutReminder"
)
```

## Managing Pending and Delivered Notifications

The `UNUserNotificationCenter` provides methods to inspect and modify scheduled (pending) and already-delivered notifications.

```swift
// Get all pending notifications
func getPendingNotifications() {
    UNUserNotificationCenter.current().getPendingNotificationRequests { requests in
        print("Pending notifications: \(requests.count)")
        for request in requests {
            print("- \(request.identifier): \(request.content.title)")
        }
    }
}

// Remove a specific pending notification
func removePendingNotification(identifier: String) {
    UNUserNotificationCenter.current().removePendingNotificationRequests(withIdentifiers: [identifier])
    print("Removed pending notification with ID: \(identifier)")
}

// Remove all pending notifications
func removeAllPendingNotifications() {
    UNUserNotificationCenter.current().removeAllPendingNotificationRequests()
    print("Removed all pending notifications.")
}

// Get all delivered notifications (those the user has seen or dismissed)
func getDeliveredNotifications() {
    UNUserNotificationCenter.current().getDeliveredNotifications { notifications in
        print("Delivered notifications: \(notifications.count)")
        for notification in notifications {
            print("- \(notification.request.identifier): \(notification.request.content.title)")
        }
    }
}

// Remove specific delivered notifications
func removeDeliveredNotification(identifier: String) {
    UNUserNotificationCenter.current().removeDeliveredNotifications(withIdentifiers: [identifier])
    print("Removed delivered notification with ID: \(identifier)")
}

// Remove all delivered notifications
func removeAllDeliveredNotifications() {
    UNUserNotificationCenter.current().removeAllDeliveredNotifications()
    print("Removed all delivered notifications.")
}
```

## Responding to Local Notifications (`UNUserNotificationCenterDelegate`)

To handle what happens when a notification is delivered or when a user interacts with it, you need to conform to the `UNUserNotificationCenterDelegate` protocol. You should set your app delegate or a dedicated class as the delegate for `UNUserNotificationCenter`.

```swift
// In your AppDelegate or a dedicated NotificationDelegate class:
extension AppDelegate: UNUserNotificationCenterDelegate {

    // Called when a notification is delivered while the app is in the foreground
    func userNotificationCenter(_ center: UNUserNotificationCenter,
                                willPresent notification: UNNotification,
                                withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void) {
        print("Notification will be presented in foreground: \(notification.request.content.title)")
        // Decide how to present the notification in the foreground
        // .banner displays a banner, .list displays in Notification Center, .sound plays a sound, .badge updates badge count
        completionHandler([.banner, .sound, .badge])
    }

    // Called when the user interacts with a notification (taps it, or selects an action)
    func userNotificationCenter(_ center: UNUserNotificationCenter,
                                didReceive response: UNNotificationResponse,
                                withCompletionHandler completionHandler: @escaping () -> Void) {
        let identifier = response.actionIdentifier
        let request = response.notification.request
        let content = request.content

        print("User interacted with notification: \(content.title)")
        print("Action identifier: \(identifier)")

        switch identifier {
        case UNNotificationDefaultActionIdentifier:
            // User tapped the notification body
            print("User tapped the notification.")
            // Handle navigation or specific action based on content.userInfo
            if let customData = content.userInfo["customData"] as? String {
                print("Custom data from notification: \(customData)")
            }
        case UNNotificationDismissActionIdentifier:
            // User dismissed the notification
            print("User dismissed the notification.")
        default:
            // Handle custom actions (if any)
            print("Unhandled custom action: \(identifier)")
        }

        completionHandler() // Must be called when you're done processing the response
    }
}
```

To make your `AppDelegate` the delegate, add this to `application(_:didFinishLaunchingWithOptions:)`:

```swift
func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    // ... other setup
    UNUserNotificationCenter.current().delegate = self
    NotificationManager.shared.requestAuthorization() // Request permission on launch
    return true
}
```

### ASCII Diagram: UNUserNotificationCenterDelegate Methods

```
┌─────────────────────────────────────────────────────────┐
│              UNUserNotificationCenterDelegate           │
└─────────────────────────────────────────────────────────┘
        │
        │  User interacts with notification (tap, dismiss, action)
        ▼
┌─────────────────────────────────────────────────────────┐
│ userNotificationCenter(_:didReceive:withCompletionHandler:) │
│  (Handles user interaction, app in background/foreground) │
└─────────────────────────────────────────────────────────┘
        │
        │  Notification delivered while app is in foreground
        ▼
┌─────────────────────────────────────────────────────────┐
│ userNotificationCenter(_:willPresent:withCompletionHandler:)│
│       (Decides presentation options in foreground)      │
└─────────────────────────────────────────────────────────┘
```

## Custom Actions and Categories

For a richer user experience, you can define custom actions that appear on your notifications. These actions are grouped into categories.

1.  **Define Actions**:
    ```swift
    let snoozeAction = UNNotificationAction(identifier: "SNOOZE_ACTION", title: "Snooze (5 min)", options: [])
    let completeAction = UNNotificationAction(identifier: "COMPLETE_ACTION", title: "Mark Complete", options: [.foreground]) // .foreground opens app
    ```

2.  **Define Category**:
    ```swift
    let taskCategory = UNNotificationCategory(
        identifier: "TASK_REMINDER",
        actions: [snoozeAction, completeAction],
        intentIdentifiers: [],
        options: []
    )
    ```

3.  **Register Category**: You need to register your categories with the notification center. This is typically done once, for example, in `application(_:didFinishLaunchingWithOptions:)`.
    ```swift
    UNUserNotificationCenter.current().setNotificationCategories([taskCategory])
    ```

4.  **Assign Category to Content**: When creating your `UNMutableNotificationContent`, assign the category identifier.
    ```swift
    let content = UNMutableNotificationContent()
    // ... set title, body, etc.
    content.categoryIdentifier = "TASK_REMINDER"
    ```

Now, when a notification with the "TASK_REMINDER" category is delivered, the user will see "Snooze (5 min)" and "Mark Complete" buttons. Your `userNotificationCenter(_:didReceive:withCompletionHandler:)` method will then receive the corresponding action identifier.

## Best Practices for Local Notifications

*   **Be Respectful**: Only send notifications that are truly valuable to the user. Excessive or irrelevant notifications can lead to users disabling them.
*   **Provide Context**: Make sure the notification content is clear and actionable. The user should immediately understand why they received it.
*   **Unique Identifiers**: Always use unique identifiers for your `UNNotificationRequest`s, especially for non-repeating notifications. This allows you to update or remove specific notifications if needed.
*   **Manage Pending Notifications**: Clean up old or irrelevant scheduled notifications to avoid clutter and potential issues.
*   **Test Thoroughly**: Test your notifications in various scenarios: app in foreground, background, killed, with different triggers, and with user interactions.

## Summary

Local notifications are a powerful tool for enhancing user engagement and providing timely information within your iOS apps. By understanding the `UserNotifications` framework, you can effectively request authorization, craft engaging content, set precise triggers, and manage the lifecycle of your notifications. Remember to always prioritize the user experience and respect their preferences regarding notifications.

Happy Swifting!
