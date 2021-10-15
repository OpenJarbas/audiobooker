import requests
from audiobooker import AudioBook, BookGenre, BookAuthor
from audiobooker.scrappers import AudioBookSource


class ThoughtAudioAudioBook(AudioBook):
    base_url = "http://thoughtaudio.com/"

    def parse_page(self):
        streams = []
        for url in self.soup.find_all("a"):
            if url["href"].endswith(".mp3"):
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
        return "ThoughtAudioAudioBook(" + str(
            self) + ", " + self.book_id + ")"


class ThoughtAudio(AudioBookSource):
    base_url = "http://thoughtaudio.com"
    _genres = ["Philosophy"]
    _genre_pages = {"Philosophy": 'http://thoughtaudio.com'}

    @classmethod
    def _parse_page(cls, html, limit=-1):
        soup = cls._get_soup(html)
        for entry in soup.find_all("div", {"class": "bf-item"}):
            try:
                a = entry.find("a")
                img = entry.find("img")
                yield ThoughtAudioAudioBook(from_data={
                    "title": entry.text,
                    "url": a["href"],
                    "img": img["src"]
                })
            except:
                continue

    @classmethod
    def _parse_search_page(cls, html, limit=-1):
        soup = cls._get_soup(html)
        for entry in soup.find_all("article"):
            try:
                a = entry.find("a")
                img = entry.find("img")
                yield ThoughtAudioAudioBook(from_data={
                    "title": a.text,
                    "url": a["href"],
                    "img": img["src"]
                })
            except:
                continue

    @classmethod
    def scrap_popular(cls, limit=-1, offset=0):
        html = requests.get(cls.base_url).text
        return cls._parse_page(html)

    @classmethod
    def search_audiobooks(cls, since=None, author=None, title=None, genre=None,
                          limit=25):
        query = ""
        if title:
            query += title + " "
        if genre:
            query += genre + " "
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
        return cls.scrap_popular()


if __name__ == "__main__":
    from pprint import pprint
   # for book in ThoughtAudio.search_audiobooks(title="Dark Tower"):
   #     pprint(book.as_json)

    scraper = ThoughtAudio()
    for book in scraper.search_audiobooks(title="machine"):
        pprint(book.as_json)

