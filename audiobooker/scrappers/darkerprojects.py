from sitemapparser import SiteMapParser
from dataclasses import dataclass
from audiobooker.base import AudioBook, BookAuthor
from audiobooker.scrappers import AudioBookSource
from audiobooker.utils import get_soup


@dataclass
class DarkerProjectsAudioBook:
    url: str

    def parse_page(self):
        streams = []
        soup = get_soup(self.url)
        img = ""
        desc = ""

        for d in soup.find("div", {"class": "inner-entry-content"}).find_all("i"):
            desc = d.text
            break

        for url in soup.find_all("img")[1:]:
            img = url["src"]
            break

        for url in soup.find_all("a"):
            if not url.get("href"):
                continue
            if url["href"].endswith(".mp3"):
                if url["href"] not in streams:
                    streams.append(url["href"])
        title = soup.find("title").text

        return AudioBook(
            title=title,
            streams=streams,
            image=img,
            tags=["audio drama"],
            description=desc,
            authors=[BookAuthor(last_name="Darker Projects")],
            language="en"
        )


class DarkerProjects(AudioBookSource):

    def iterate_all(self):
        sm = SiteMapParser('https://darkerprojects.com/wp-sitemap-posts-post-1.xml')  # reads /sitemap.xml
        urls = sm.get_urls()  # returns iterator of sitemapper.Url instances
        for url in urls:
            url = str(url)
            book = DarkerProjectsAudioBook(url=url)
            yield book.parse_page()


if __name__ == "__main__":
    from pprint import pprint

    scraper = DarkerProjects()

    for book in scraper.iterate_all():
        pprint(book)
