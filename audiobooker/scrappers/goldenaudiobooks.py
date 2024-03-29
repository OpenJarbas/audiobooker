from dataclasses import dataclass

from sitemapparser import SiteMapParser

from audiobooker.base import AudioBook, BookAuthor
from audiobooker.scrappers import AudioBookSource
from audiobooker.utils import get_soup, normalize_name


@dataclass
class GoldenAudioBooksAudioBook:
    url: str

    def parse_page(self):
        soup = get_soup(self.url)
        title = soup.find("h1", {"class": "title-page"}).text.replace(" Audiobook", "")
        tags = [t for t in soup.find("span", {"class": "post-meta-category"}).text.split(" ") if len(t) > 2]
        img = soup.find("figure").find("img")["src"]

        authors = []

        if "–" in title:
            pts = title.split("–")
            author_name = pts[0]
            title = " ".join(pts[1:])

            f, l = normalize_name(author_name)

            authors = [BookAuthor(first_name=f, last_name=l)]

        streams = [s.find("a").text for s in soup.find_all("audio")]

        return AudioBook(
            title=title.strip(),
            streams=streams,
            image=img,
            tags=tags,
            authors=authors,
            language="en"
        )


class GoldenAudioBooks(AudioBookSource):
    base_url = "https://goldenaudiobook.co/"

    def iterate_all(self):
        for u in ['https://goldenaudiobook.co/post-sitemap.xml',
                  'https://goldenaudiobook.co/post-sitemap2.xml']:
            sm = SiteMapParser(u)  # reads /sitemap.xml
            urls = sm.get_urls()  # returns iterator of sitemapper.Url instances
            for url in urls:
                yield GoldenAudioBooksAudioBook(url=str(url)).parse_page()


if __name__ == "__main__":
    from pprint import pprint

    scraper = GoldenAudioBooks()
    for book in scraper.iterate_all():
        pprint(book)
