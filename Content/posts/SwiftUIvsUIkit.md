---
date: 2024-12-22 17:08
description: At the 2019 WWDC Apple introduced a new UI framework called SwiftUI. From the initial phase of iOS development, we are looking at Xibs and storyboards to build a user interface in ios, macOS and WatchOS app, many more developers were fed-up from developing UI by Storyboard, maybe you are one of them, there are a lot of drawbacks of UIkit over SwiftUI.
tags: first, article
---
# SwiftUI vs UIKit

At the 2019 WWDC Apple introduced a new UI framework called SwiftUI. From the initial phase of iOS development, we are looking at Xibs and storyboards to build a user interface in ios, macOS and WatchOS app, many more developers were fed-up from developing UI by Storyboard, maybe you are one of them, there are a lot of drawbacks of UIkit over SwiftUI.

Yeah….  but the SwiftUI also has one major drawback, Apps created in SwiftUI only support iOS 13 and the next version, and SwiftUI don’t allow us to debug hierarchy of views. For now, SwiftUI requires the following pieces of stuff: Xcode 11.4  macOS Catalina to start building apps in SwiftUI. 

It starts and end with view: 

Whole SwiftUI framework is completely looping in view, no more UITableView, UIcollectionView, UIView, UICollectionViewCell, UITableViewCell classes in SwiftUI framework.

The given example SwiftUI uses Struct to initialize and define through the View protocol. Some properties return View. As Swift UI uses DSL like syntax, the return is omitted from the Struct body.
```swift
import SwiftUI

struct ContentView: View {
    var body: some View {
        Text("Welcome to Swift By Rahul")
    }
}
```
```swift
struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
```
<h4>Sync Design and code  (Declarative Programming): </h4>

From the launch day of Xcode we are using xibs, storyboards and programmatically UI for developing UI content such as Static  & dynamic content, Animation, Graphics, etc. When your user interface is created in code. You can see dynamic previews of this code on-canvas preview. You also have a choice, you can code user interface by yourself or you can use canvas editor(drag and drop UI building tool)  to code on behalf.

<h4>Benefits of declarative programming : </h4>

Easy to write. 
Fast.
Adaptive (Does Not need recompilation for the preview of the coded User interface)
Important Note: Canvas editor UI content reflects in code at the movement,  but in UIKit changes done in storyboard or xib are not visualized in UIViewcontroller class.

<h4>Adopt existing UIKit app with swiftUI:  </h4>

Yes UIKit and SwiftUI framework can communicate with each other, SwiftUI designed very perfectly to deal with existing frameworks, the UIHostingViewController class is becoming a mediator here. It integrates SwiftUI view with UIKIt ViewController, honestly in genuine SwiftUI App use UIHostingViewController for specifying root view controller to UIWindow. 

<h4>SwiftUI is Reactive :  </h4>

Traditional iOS development doesn’t support any bindable mechanism in pure swift, that’s why React Swift and React cocoa came into the picture, in SwiftUI Apple achieved some mechanism by state management and binding, though variables and property can bind with the user interface. SwiftUI supports By default MVVM architecture. A combine framework allows us to perform event-oriented operations. Omitted to create and to implement observer and delegate communication patterns by the reactive mechanism.

 Protocols, Classes, and properties like @publisher, @publishers, @anyPublisher, @published, @cancellable and  @subscriber are designed to achieve reactive goals in SwiftUI.
 
```swift
import SwiftUI

struct ContentView: View {
    @State var name = ""
    var body: some View {
        NavigationView {
            VStack {
                TextField("Swift By Rahul", text: $name).padding(12)
                Text(name).padding(12)
            }
        }.background(Color.white)
    }
}
struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
```
As you can see the variable name is stated by @State property, and the name variable is bound with TextField, so whenever any action performed with TextField, the string value of TextField will eventually store in the name variable.

Some small benefits of SwiftUI:

The compilation time of storyboard and xib is far more than SwiftUI. So its quickly compiling and running on the simulator.

No headache of xib xml file conflicts while merging multiple code commits

Canvas preview is awesome, needs not to compile the whole project to see UI preview.

No headache of Constraints, AutoLayout like storyboard.

App created for iOS can use for MacOS as well. Hardware platform portability is a very crucial feature provided in SwiftUI.

IBOutlets and UI properties need not to be handle in ViewController class.

No delegates and datasource methods for UI Components.

 <h4>Conclusion:  </h4>

SwiftUI is a newborn programming language, its very adaptive to learn but as SwiftUI framework is not working with previous iOS versions like iOS versions less than iOS 13. Start a new project in swift UI, for now, it’s very risky. Because it will not cover 100% audience due to platform compatibility. Yes But SwiftUI is the future of iOS.

Keep learning…..


