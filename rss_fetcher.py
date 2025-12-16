import feedparser
from typing import List, Dict

class RSSFetcher:
    def __init__(self, feed_url: str):
        self.feed_url = feed_url

    def fetch(self) -> List[Dict]:
        """
        Fetches news from the RSS feed.
        Returns a list of dictionaries with keys: 'title', 'link', 'published', 'summary', 'id'.
        """
        feed = feedparser.parse(self.feed_url)
        news_items = []
        for entry in feed.entries:
            news_items.append({
                'title': entry.get('title', 'No Title'),
                'link': entry.get('link', ''),
                'published': entry.get('published', ''),
                'summary': entry.get('summary', ''),
                'id': entry.get('id', entry.get('link', ''))
            })
        return news_items

if __name__ == "__main__":
    # Test
    fetcher = RSSFetcher("https://feeds.bloomberg.com/markets/news.rss")
    items = fetcher.fetch()
    print(f"Fetched {len(items)} items.")
    if items:
        print(items[0])
