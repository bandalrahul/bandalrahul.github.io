//
//  CustomeThemeHTMLFactory.swift
//  PublishSBR
//
//  Created by Rahul Bandal on 27/03/25.
//
import Foundation
import Ink
import Publish
import Plot
import SplashPublishPlugin

private struct Wrapper: ComponentContainer {
    @ComponentBuilder var content: ContentProvider

    var body: Component {
        Div(content: content).class("wrapper")
    }
}

struct MyHTMLFactory<Site: Website>: HTMLFactory {
    func makeIndexHTML(for index: Index,
                       context: PublishingContext<Site>) throws -> HTML {
        HTML(
            .lang(context.site.language),
            .head(for: index, on: context.site),
            .body {
                SiteHeader(context: context, selectedSelectionID: nil)
                Wrapper {
                    Div {
                        H1(index.title)
                        Paragraph("Swift tutorials & iOS development")
                            .class("site-tagline")
                        Paragraph("by Rahul Bandal")
                            .class("site-author")
                    }
                    .class("hero")

                    ItemList(
                        items: context.allItems(
                            sortedBy: \.date,
                            order: .descending
                        ),
                        site: context.site
                    )
                }
                SiteFooter()
            }
        )
    }

    func makeSectionHTML(for section: Section<Site>,
                         context: PublishingContext<Site>) throws -> HTML {
        HTML(
            .lang(context.site.language),
            .head(for: section, on: context.site),
            .body {
                SiteHeader(context: context, selectedSelectionID: section.id)
                Wrapper {
                    H1(section.title)
                    ItemList(items: section.items, site: context.site)
                }
                SiteFooter()
            }
        )
    }

    func makeItemHTML(for item: Item<Site>,
                      context: PublishingContext<Site>) throws -> HTML {
        HTML(
            .lang(context.site.language),
            .head(for: item, on: context.site),
            .head(
                .stylesheet("/css/prism.css"),
                .script(.src("/js/prism.js")),
                .script(.src("/js/article.js")),
                adsenseLoaderScript(),
                .meta(.name("twitter:card"), .content("summary_large_image")),
                .meta(.property("og:image"), .content(itemSocialImageURL(for: item, on: context.site))),
                .meta(.property("og:image:alt"), .content(item.title)),
                .meta(.name("twitter:image"), .content(itemSocialImageURL(for: item, on: context.site)))
            ),
            .body(
                .class("item-page"),
                .components {
                    SiteHeader(context: context, selectedSelectionID: item.sectionID)
                    Wrapper {
                        Article {
                            Div {
                                tocToggleButton()

                                Div {
                                    Aside {
                                        Paragraph("On this page")
                                            .class("toc-heading")
                                        Navigation()
                                            .class("toc-nav")
                                            .id("article-toc-nav")
                                    }
                                    .class("toc")
                                    .id("article-toc")

                                    Div {
                                        ArticleMeta(item: item, site: context.site)
                                        Div(item.content.body).class("content")
                                        Div {
                                            Span("Tagged: ")
                                                .class("tags-label")
                                            ItemTagList(item: item, site: context.site)
                                        }
                                        .class("article-tags")
                                        adsenseBanner()
                                    }
                                    .class("article-main")
                                }
                                .class("article-layout")
                            }
                        }
                    }
                    SiteFooter()
                }
            )
        )
    }

    func makePageHTML(for page: Page,
                      context: PublishingContext<Site>) throws -> HTML {
        HTML(
            .lang(context.site.language),
            .head(for: page, on: context.site),
            .body {
                SiteHeader(context: context, selectedSelectionID: nil)
                Wrapper(page.body)
                SiteFooter()
            }
        )
    }

    func makeTagListHTML(for page: TagListPage,
                         context: PublishingContext<Site>) throws -> HTML? {
        HTML(
            .lang(context.site.language),
            .head(for: page, on: context.site),
            .body {
                SiteHeader(context: context, selectedSelectionID: nil)
                Wrapper {
                    H1("Browse all tags")
                    List(page.tags.sorted()) { tag in
                        ListItem {
                            Link(tag.string,
                                 url: context.site.path(for: tag).absoluteString
                            )
                        }
                        .class("tag")
                    }
                    .class("all-tags")
                }
                SiteFooter()
            }
        )
    }

    func makeTagDetailsHTML(for page: TagDetailsPage,
                            context: PublishingContext<Site>) throws -> HTML? {
        HTML(
            .lang(context.site.language),
            .head(for: page, on: context.site),
            .body {
                SiteHeader(context: context, selectedSelectionID: nil)
                Wrapper {
                    H1 {
                        Text("Tagged with ")
                        Span(page.tag.string).class("tag")
                    }

                    Link("Browse all tags",
                        url: context.site.tagListPath.absoluteString
                    )
                    .class("browse-all")

                    ItemList(
                        items: context.items(
                            taggedWith: page.tag,
                            sortedBy: \.date,
                            order: .descending
                        ),
                        site: context.site
                    )
                }
                SiteFooter()
            }
        )
    }
}

private struct SiteHeader<Site: Website>: Component {
    var context: PublishingContext<Site>
    var selectedSelectionID: Site.SectionID?

    var body: Component {
        Header {
            Wrapper {
                Link(context.site.name, url: "/")
                    .class("site-name")

                Navigation {
                    List {
                        ListItem {
                            Link("Home", url: "/")
                                .class(selectedSelectionID == nil ? "selected" : "")
                        }
                        ListItem {
                            Link("Posts", url: "/posts/")
                                .class(selectedSelectionID != nil ? "selected" : "")
                        }
                        ListItem {
                            Link("Tags", url: context.site.tagListPath.absoluteString)
                        }
                        ListItem {
                            Link("GitHub", url: "https://github.com/bandalrahul")
                        }
                    }
                }
                .class("site-nav")
            }
        }
    }
}

private struct ItemList<Site: Website>: Component {
    var items: [Item<Site>]
    var site: Site

    var body: Component {
        List(items) { item in
            Article {
                Div {
                    if item.path == items.first?.path {
                        Span("Latest")
                            .class("post-badge")
                    }

                    H2(Link(item.title, url: item.path.absoluteString))

                    Paragraph(item.description)

                    Div {
                        Span(item.date.formatted(.dateTime.day().month(.wide).year()))
                        Span(" · ")
                        Span("\(readingTimeMinutes(for: item)) min read")
                    }
                    .class("post-meta")

                    if !item.tags.isEmpty {
                        ItemTagList(item: item, site: site)
                    }
                }
                .class(item.path == items.first?.path ? "post-card latest" : "post-card")
            }
        }
        .class("item-list")
    }
}

private struct ArticleMeta<Site: Website>: Component {
    var item: Item<Site>
    var site: Site

    var body: Component {
        Div {
            Span(item.date.formatted(.dateTime.day().month(.wide).year()))
            Span(" · ")
            Span("\(readingTimeMinutes(for: item)) min read")

            if !item.tags.isEmpty {
                Span(" · ")
                ItemTagList(item: item, site: site)
            }
        }
        .class("article-meta")
    }
}

private struct ItemTagList<Site: Website>: Component {
    var item: Item<Site>
    var site: Site

    var body: Component {
        List(item.tags) { tag in
            Link(tag.string, url: site.path(for: tag).absoluteString)
        }
        .class("tag-list")
    }
}

private struct SiteFooter: Component {
    var body: Component {
        Footer {
            Wrapper {
                Paragraph {
                    Text("© Swift By Rahul · ")
                    Link("RSS", url: "/feed.rss")
                    Text(" · ")
                    Link("GitHub", url: "https://github.com/bandalrahul")
                    Text(" · Built with ")
                    Link("Publish", url: "https://github.com/johnsundell/publish")
                }
            }
        }
    }
}

private func readingTimeMinutes<Site: Website>(for item: Item<Site>) -> Int {
    let plainText = item.content.body.html
        .replacingOccurrences(of: "<[^>]+>", with: " ", options: .regularExpression)
    let wordCount = plainText
        .split(whereSeparator: \.isWhitespace)
        .count
    return max(1, wordCount / 200)
}

private func tocToggleButton() -> Component {
    Node<HTML.BodyContext>.element(
        named: "button",
        nodes: [
            .class("toc-toggle"),
            .id("toc-toggle"),
            .attribute(named: "type", value: "button"),
            .attribute(named: "aria-expanded", value: "false"),
            .text("On this page")
        ]
    )
}

private func itemSlug<Site: Website>(from item: Item<Site>) -> String {
    item.path.absoluteString
        .trimmingCharacters(in: CharacterSet(charactersIn: "/"))
        .split(separator: "/")
        .last
        .map(String.init) ?? ""
}

private func itemSocialImageURL<Site: Website>(for item: Item<Site>, on site: Site) -> String {
    let slug = itemSlug(from: item)
    return site.url.appendingPathComponent("images/posts/\(slug).png").absoluteString
}

private let adsenseClientID = "ca-pub-9268892677399703"
private let adsenseSlotID = "8133392181"

func adsenseLoaderScript() -> Node<HTML.HeadContext> {
    .script(
        .src("https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=\(adsenseClientID)"),
        .async()
    )
}

func adsenseBanner() -> Node<HTML.BodyContext> {
    return .div(
        .class("ads-container"),
        .element(named: "ins", nodes: [
            .attribute(named: "class", value: "adsbygoogle"),
            .attribute(named: "style", value: "display:block"),
            .attribute(named: "data-ad-client", value: adsenseClientID),
            .attribute(named: "data-ad-slot", value: adsenseSlotID),
            .attribute(named: "data-ad-format", value: "auto"),
            .attribute(named: "data-full-width-responsive", value: "true")
        ]),
        .script(.raw("(adsbygoogle = window.adsbygoogle || []).push({});"))
    )
}
