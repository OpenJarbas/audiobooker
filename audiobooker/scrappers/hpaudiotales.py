from dataclasses import dataclass

from sitemapparser import SiteMapParser

from audiobooker.base import AudioBook
from audiobooker.scrappers import AudioBookSource
from audiobooker.utils import get_soup


@dataclass
class HPTalesAudioBook:
    url: str

    def parse_page(self):
        soup = get_soup(self.url)
        title = soup.find("h1", {"class": "entry-title"}).text
        tags = ["Harry Potter", "Fantasy", "Magic"]

        d = soup.find("div", {"class": "audioigniter-root"})["data-tracks-url"]
        data = AudioBookSource.session.get(d).json()
        tags += list(set(s["subtitle"] for s in data))

        streams = [s["audio"] for s in data]

        return AudioBook(
            title=title.strip(),
            streams=streams,
            tags=tags,
            language="en"
        )


class HPTalesAudioBooks(AudioBookSource):

    @classmethod
    def iterate_all(cls, limit=-1, offset=0):
        sm = SiteMapParser('https://hpaudiotales.com/wp-sitemap-posts-post-1.xml')  # reads /sitemap.xml
        urls = sm.get_urls()  # returns iterator of sitemapper.Url instances
        for url in urls:
            yield HPTalesAudioBook(url=str(url)).parse_page()


if __name__ == "__main__":
    from pprint import pprint

    scraper = HPTalesAudioBooks()
    for book in scraper.iterate_all():
        pprint(book)
