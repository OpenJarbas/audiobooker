import requests
from audiobooker import AudioBook, BookTag, BookAuthor
from audiobooker.scrappers import AudioBookSource


class AudioAnarchyAudioBook(AudioBook):
    base_url = "http://www.audioanarchy.org/"

    def parse_page(self):
        streams = []
        for url in self.soup.find_all("a"):
            try:
                if not url["href"].endswith(".mp3"):
                    continue
                streams.append(self.base_url + url["href"])
            except:
                continue
        title = self.soup.find("title").text
        author_name = "Audio Anarchy"
        authors = [BookAuthor(first_name=author_name)]
        img = self.img
        return {"authors": authors,
                "title": title.strip(),
                "streams": streams,
                "rating": 0,
                "tags": [],
                "img": img}

    def from_page(self):
        data = self.parse_page()
        if not self.title:
            self.title = data["title"]
        if not self._description:
            self._description = data.get("description") or self.title
        self.img = data.get("img", self.img)
        for tag in data["tags"]:
            if tag.as_json not in self._tags:
                self._tags.append(tag.as_json)
        for author in data["authors"]:
            if author.as_json not in self._authors:
                self._authors.append(author.as_json)
        self._stream_list = data["streams"]
        self.raw.update(data)

    def __repr__(self):
        return "AudioAnarchyAudioBook(" + str(
            self) + ", " + self.book_id + ")"


class AudioAnarchy(AudioBookSource):
    base_url = "http://www.audioanarchy.org"
    _tags = ["Anarchy"]
    _tag_pages = {"Anarchy":'http://www.audioanarchy.org'}

    @staticmethod
    def _parse_page(html, limit=-1):
        soup = AudioAnarchy._get_soup(html)
        for entry in soup.find_all("div", {"id": "album"}):
            try:
                a = entry.find("a")
                img = entry.find("img")
                book = AudioAnarchyAudioBook(from_data={
                    "title": img["alt"],
                    "url": "https://www.audioanarchy.org/" + a["href"],
                    "img": "https://www.audioanarchy.org/" + img["src"]
                })
                book.from_page()  # parse url
                yield book
            except:
                raise
                continue

    def scrap_popular(self, limit=-1, offset=0):
        html = requests.get(self.base_url).text
        return AudioAnarchy._parse_page(html)

    @classmethod
    def search_audiobooks(cls, since=None, author=None, title=None, tag=None,
                          limit=25):
        html = requests.get(AudioAnarchy.base_url).text
        return AudioAnarchy._parse_page(html)

    @classmethod
    def get_audiobook(cls, book_id):
        url = cls.base_url + '/' + book_id
        book = AudioAnarchyAudioBook(url=url)
        return book

    def scrap_all_audiobooks(self, limit=-1, offset=0):
        return self.scrap_popular()


if __name__ == "__main__":
    from pprint import pprint
   # for book in AudioAnarchy.search_audiobooks(title="Dark Tower"):
   #     pprint(book.as_json)

    scraper = AudioAnarchy()
    for book in scraper.scrap_popular():
        pprint(book.as_json)
