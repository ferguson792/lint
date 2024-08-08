
import feedparser

url = "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml"
feed = feedparser.parse(url)

print("Feed Title:", feed.feed.title)
print("Feed Description:", feed.feed.description)
print("Feed Link:", feed.feed.link)

for entry in feed.entries:
    print("Entry Title:", entry.title)
    print("Entry Link:", entry.link)
    print("Entry Published Date:", entry.published)
    print("Entry Summary:", entry.summary)
    print("GUID:", entry.guid)
    print("\n")
