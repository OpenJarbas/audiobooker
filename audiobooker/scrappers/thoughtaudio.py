import requests
from audiobooker import AudioBook, BookTag, BookAuthor
from audiobooker.scrappers import AudioBookSource
from sitemapparser import SiteMapParser


class ThoughtAudioAudioBook(AudioBook):
    base_url = "http://thoughtaudio.com/"

    def parse_page(self):
        streams = []
        for url in self.soup.find_all("a"):
            if url["href"].endswith(".mp3"):
                streams.append(url["href"])
        for url in self.soup.find_all("iframe"):
            if "youtube" not in url["src"]:
                continue
            streams.append(
                url["src"].split("?feature=oembed")[0].
                replace("https://www.youtube.com/embed/", "https://www.youtube.com/watch?v=")
            )
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
        return "ThoughtAudioAudioBook(" + str(
            self) + ", " + self.book_id + ")"


class ThoughtAudio(AudioBookSource):
    base_url = "http://thoughtaudio.com"
    _tags = ["Philosophy"]
    _tag_pages = {"Philosophy": 'http://thoughtaudio.com'}

    @classmethod
    def _parse_page(cls, html, limit=-1):
        soup = cls._get_soup(html)
        for entry in soup.find_all("div", {"class": "bf-item"}):
            try:
                a = entry.find("a")
                img = entry.find("img")
                book = ThoughtAudioAudioBook(from_data={
                    "title": entry.text,
                    "url": a["href"],
                    "img": img["src"]
                })
                book.from_page()  # parse url
                yield book
            except:
                continue

    @classmethod
    def _parse_search_page(cls, html, limit=-1):
        soup = cls._get_soup(html)
        for entry in soup.find_all("article"):
            try:
                a = entry.find("a")
                img = entry.find("img")
                book = ThoughtAudioAudioBook(from_data={
                    "title": a.text,
                    "url": a["href"],
                    "img": img["src"]
                })
                book.from_page()  # parse url
                yield book
            except:
                continue

    @classmethod
    def scrap_popular(cls, limit=-1, offset=0):
        html = requests.get(cls.base_url).text
        return cls._parse_page(html)

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
        return cls._parse_search_page(html)

    @classmethod
    def get_audiobook(cls,book_id):
        url = cls.base_url + '/' + book_id
        book = ThoughtAudioAudioBook(url=url)
        return book

    @classmethod
    def scrap_all_audiobooks(cls, limit=-1, offset=0):
        sm = SiteMapParser('http://thoughtaudio.com/wp-sitemap-posts-post-1.xml')  # reads /sitemap.xml
        urls = sm.get_urls()  # returns iterator of sitemapper.Url instances
        for url in urls:
            url = str(url)
            title = url.strip("/").split("/")[-1].replace("-", " ").title()
            yield ThoughtAudioAudioBook(url=url, title=title)


if __name__ == "__main__":
    from pprint import pprint

    scraper = ThoughtAudio()
    for book in scraper.search_audiobooks(title="machine"):
        pprint(book.as_json)

    for book in scraper.scrap_all_audiobooks():
        pprint(book.as_json)

