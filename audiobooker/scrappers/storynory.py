import requests
from audiobooker import AudioBook, BookTag, BookAuthor
from audiobooker.scrappers import AudioBookSource


class StoryNoryAudioBook(AudioBook):
    base_url = "https://www.storynory.com/"

    def parse_page(self):
        streams = []
        for url in self.soup.find_all("a"):
            if url["href"].endswith(".mp3"):
                if url["href"] not in streams:
                    streams.append(url["href"])

        title = self.soup.find("title").text
        img = self.soup.find("img")
        if img.get("data-ezsrc"):
            img = img["data-ezsrc"]
        elif img.get("src"):
            img = img["src"]
        else:
            img = self.img
        print(streams)
        return {"title": title.strip(),
                "streams": streams,
                "img": img}

    def from_page(self):
        data = self.parse_page()
        self.title = data["title"]
        self.img = data.get("img", self.img)
        self.raw.update(data)
        self._stream_list = data["streams"]

    def __repr__(self):
        return "StoryNoryAudioBook(" + str(
            self) + ", " + self.book_id + ")"


class StoryNory(AudioBookSource):
    # TODO categories / tags
    base_url = "https://www.storynory.com"

    @classmethod
    def _parse_page(cls, html, limit=-1):
        soup = cls._get_soup(html)
        for entry in soup.find_all("div", {"class": "bf-item"}):
            try:
                a = entry.find("a")
                img = entry.find("img")
                book = StoryNoryAudioBook(from_data={
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
        for entry in soup.find_all("div", {"class": "panel-body"}):
            try:
                a = entry.find("a")
                img = entry.find("img")
                book = StoryNoryAudioBook(from_data={
                    "title": a.text,
                    "description": entry.find("p").text,
                    "url": a["href"],
                    "img": img["src"] if img else ""
                })
                print(book)
                book.from_page()  # parse url
                print(book)
                yield book
            except:
                continue

        if limit == -1 or limit > 0:
            limit -= 1
            next_page = soup.find("li", {"class": "bpn-next-link"})
            if next_page:
                html = requests.get(next_page.find("a")["href"]).text
                for ntry in cls._parse_search_page(html, limit=limit):
                    yield ntry

    @classmethod
    def scrap_popular(cls, limit=-1, offset=0):
        html = requests.get(cls.base_url).text
        soup = cls._get_soup(html)
        for a in soup.find_all("a"):
            url = a["href"]
            if not url.startswith("https://www.storynory.com/"):
                continue
            img = a.find("img")
            if not img:
                continue
            p = a.find("p")
            desc = ""
            if p:
                desc = p.text
            try:
                book = StoryNoryAudioBook(description=desc,
                                         url=url,
                                         title=img["alt"],
                                         img=img["data-ezsrc"])
            except:
                book = StoryNoryAudioBook(description=desc,
                                         url=url,
                                         img=img["src"])
            book.from_page()  # parse book url for streams
            yield book

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
    def get_audiobook(cls, book_id):
        url = cls.base_url + '/' + book_id
        book = StoryNoryAudioBook(url=url)
        return book

    @classmethod
    def scrap_all_audiobooks(cls, limit=-1, offset=0):
        return cls.scrap_popular()


if __name__ == "__main__":
    from pprint import pprint
   # for book in StoryNory.search_audiobooks(title="Dark Tower"):
   #     pprint(book.as_json)

    scraper = StoryNory()
    for book in scraper.scrap_popular():
        print(book.as_json)

