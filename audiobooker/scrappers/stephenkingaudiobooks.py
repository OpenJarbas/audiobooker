from dataclasses import dataclass
from typing import Iterable

from sitemapparser import SiteMapParser

from audiobooker.exceptions import ParseErrorException
from audiobooker.base import AudioBook, BookAuthor, AudiobookNarrator
from audiobooker.scrappers import AudioBookSource
from audiobooker.utils import get_soup, extractor_narrator, extract_year


@dataclass
class StephenKingAudioBook:
    url: str

    def parse_page(self):
        soup = get_soup(self.url)
        tags = soup.find("span", {"class": "post-meta-category"})
        title = soup.find("h1", {"class": "title-page"}).text.replace("\xa0", " ")
        content = soup.find("div", {"class": "post-single clearfix"})
        desc = content.find("p").text.replace("\xa0", " ")

        img = content.find("img")["src"]

        if "Harry Potter" not in tags.text:
            authors = [BookAuthor(first_name="Stephen", last_name="King")]
        else:
            authors = [BookAuthor(first_name="J.K.", last_name="Rowling")]

        if "Stephen Fry" in title and "Harry Potter" in tags.text:
            narrator = AudiobookNarrator(first_name="Stephen",
                                         last_name="Fry")
        else:
            narrator = (extractor_narrator(title) or
                        extractor_narrator(desc))

        streams = [s.find("a").text for s in content.find_all("audio")]

        if not streams:
            raise ParseErrorException("No streams found")
        return AudioBook(
            title=title.replace(" Audiobook", ""),
            streams=streams,
            description=desc,
            narrator=narrator,
            image=img,
            tags=[],
            authors=authors,
            year=extract_year(title) or
                 extract_year(desc),
            language="en"
        )


class StephenKingAudioBooks(AudioBookSource):
    base_url = "https://stephenkingaudiobooks.com"
    @classmethod
    def _parse_page(cls,url = "https://stephenkingaudiobooks.com", limit=-1, **params):
        soup = get_soup(url, **params)
        for entry in soup.find_all("article"):
            try:
                a = entry.find("a")
                url = a["href"]
                yield StephenKingAudioBook(url=url).parse_page()
            except:
                continue
        if limit == -1 or limit > 0:
            limit -= 1
            next_page = soup.find("div", {"class": "nav-previous"})
            if next_page:
                url = next_page.find("a")["href"]
                for ntry in cls._parse_page(url=url, limit=limit, **params):
                    yield ntry

    def search(self, query):
        return self._parse_page(params={"s": query})


    def iterate_all(self):
        sm = SiteMapParser('https://stephenkingaudiobook.net/wp-sitemap-posts-post-1.xml')  # reads /sitemap.xml
        urls = sm.get_urls()  # returns iterator of sitemapper.Url instances
        for url in urls:
            try:
                yield StephenKingAudioBook(url=str(url)).parse_page()
            except:
                pass

if __name__ == "__main__":
    from pprint import pprint

    scraper = StephenKingAudioBooks()
    for book in scraper.search("Dark Tower"):
        pprint(book)

    exit()
    for book in scraper.iterate_all():
        pprint(book)
