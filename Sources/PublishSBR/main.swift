import Foundation
import Publish
import Plot

// This type acts as the configuration for your website.
struct PublishSBR: Website {
    enum SectionID: String, WebsiteSectionID {
        // Add the sections that you want your website to contain here:
        case posts
    }

    struct ItemMetadata: WebsiteItemMetadata {
        // Add any site-specific metadata that you want to use here.
    }

    // Update these properties to configure your website:
    var url = URL(string: "bandalrahul.github.io")!
    var name = "Swift By Rahul"
    var description = ""
    var language: Language { .english }
    var imagePath: Path? { nil }
}

// This will generate your website using the built-in Foundation theme:
try PublishSBR().publish(
    withTheme: .myTheme,
    additionalSteps: [
        .deploy(
            using: .git(
                "git@github.com:bandalrahul/bandalrahul.github.io.git" // Change to SSH URL
            )
        ),
        .installPlugin(
            .splash(
                withClassPrefix: ""
            )
        )
    ]
)

extension Theme where Site == PublishSBR {
    static var myTheme: Self {
        Theme(
            htmlFactory: MyHTMLFactory(),
            resourcePaths: ["Resources/MyTheme/styles.css","Resources/css/prism.css", "Resources/js/prism.js"]
        )
    }
}
