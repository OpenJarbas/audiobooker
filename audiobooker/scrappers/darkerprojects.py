import requests
from sitemapparser import SiteMapParser

from audiobooker import AudioBook
from audiobooker.scrappers import AudioBookSource


class DarkerProjectsAudioBook(AudioBook):
    base_url = "http://darkerprojects.com"

    def parse_page(self):
        streams = []
        for url in self.soup.find_all("a"):
            if not url.get("href"):
                continue
            if url["href"].endswith(".mp3"):
                if url["href"] not in streams:
                    streams.append(url["href"])
        title = self.soup.find("title").text
        img = self.img

        return {"title": title.strip(),
                "streams": streams,
                "img": img}

    def from_page(self):
        data = self.parse_page()
        self.title = data["title"]
        self.img = data.get("img", self.img)
        self._stream_list = data["streams"]
        self.raw.update(data)

    def __repr__(self):
        return "DarkerProjectsAudioBook(" + str(
            self) + ", " + self.book_id + ")"


class DarkerProjects(AudioBookSource):
    base_url = "http://darkerprojects.com"

    @classmethod
    def _parse_page(cls, html, limit=-1):
        soup = cls._get_soup(html)
        for entry in soup.find_all("article"):
            try:
                if not entry.find("div", {"class": "powerpress_player"}):
                    continue  # no audio streams, text only post
                a = entry.find("a")
                desc = ""
                for p in entry.find_all("p"):
                    desc = p.text

                tags = []
                try:
                    cat = entry.find("span", {"class": "cat-links"}).find("a")
                    tags.append({"name": cat.text, "url": cat["href"]})
                except:
                    pass
                dl = entry.find("a", {"class": "powerpress_link_d"})
                yield DarkerProjectsAudioBook(
                    title=a.text,
                    description=desc,
                    stream_list=[dl["href"]],
                    tags=tags,
                    url=a["href"]
                )
            except:
                continue

    @classmethod
    def scrap_popular(cls, limit=-1, offset=0):
        html = requests.get(cls.base_url).text
        return cls._parse_page(html)

    @classmethod
    def scrap_tags(cls):
        bucket = {}
        sm = SiteMapParser('https://darkerprojects.com/wp-sitemap-taxonomies-category-1.xml')  # reads /sitemap.xml
        urls = sm.get_urls()  # returns iterator of sitemapper.Url instances
        for url in urls:
            url = str(url)
            title = url.strip("/").split("/")[-1].replace("-", " ").title()
            bucket[title] = url
        return bucket

    @classmethod
    def scrap_collections(cls, limit=-1, offset=0):
        for tag in cls.scrap_tags():
            yield cls.get_collection(tag)

    @classmethod
    def get_collection(cls, collection):
        for tag, url in cls.scrap_tags().items():
            if tag == collection:
                html = requests.get(url).text
                streams = []
                for book in cls._parse_page(html):
                    streams += book.streams
                streams.reverse()
                return DarkerProjectsAudioBook(title=tag,
                                               stream_list=streams,
                                               url=url)

    @classmethod
    def search_audiobooks(cls, since=None, author=None, title=None, tag=None,
                          limit=25):
        query = ""
        if title:
            query += title + " "
        if tag:
            query += tag + " "
        if author:
            query += author + " "
        html = requests.get(cls.base_url, params={"s": query}).text
        return cls._parse_page(html)

    @classmethod
    def get_audiobook(cls, book_id):
        url = cls.base_url + '/' + book_id
        book = DarkerProjectsAudioBook(url=url)
        return book

    @classmethod
    def scrap_all_audiobooks(cls, limit=-1, offset=0):
        sm = SiteMapParser('https://darkerprojects.com/wp-sitemap-posts-post-1.xml')  # reads /sitemap.xml
        urls = sm.get_urls()  # returns iterator of sitemapper.Url instances
        for url in urls:
            url = str(url)
            title = url.strip("/").split("/")[-1].replace("-", " ").title()
            book = DarkerProjectsAudioBook(url=url, title=title)
            book.from_page()
            yield book


if __name__ == "__main__":
    from pprint import pprint

    scraper = DarkerProjects()

    print(scraper.scrap_tags())

    for book in scraper.scrap_all_audiobooks():
        pprint(book.as_json)
