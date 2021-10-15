import feedparser
from audiobooker import AudioBook, BookTag, BookAuthor, session
from audiobooker.scrappers import AudioBookSource


class LibrivoxAudioBook(AudioBook):
    def __init__(self, title="", authors=None, description="", tags=None,
                 book_id="", runtime=0, url="", img="", rss_url="",
                 copyright_year=0, language='english', from_data=None):
        self.rss_url = rss_url
        self.copyright_year = copyright_year
        AudioBook.__init__(self, title, authors, description, tags,
                           book_id, runtime, url, img, language, from_data=from_data)

    @property
    def description(self):
        return self._description.replace("<p>", "").replace("</p>", "") \
            .replace("(summary from Wikipedia)", "").strip().rstrip("\"") \
            .lstrip("\"")

    @property
    def rss_data(self):
        return feedparser.parse(self.rss_url)

    @property
    def streamer(self):
        for stream in self.rss_data["entries"]:
            try:
                yield stream['media_content'][0]["url"]
            except Exception as e:
                print(e)
                continue

    def from_json(self, json_data):
        AudioBook.from_json(self, json_data)
        self.url = json_data.get("url_librivox", self.url)
        self.runtime = json_data.get("totaltimesecs", self.runtime)
        self.copyright_year = json_data.get("copyright_year",
                                            self.copyright_year)
        self.rss_url = json_data.get("url_rss", self.rss_url)

    def __repr__(self):
        return "LibrivoxAudioBook(" + str(self) + ", " + self.book_id + ")"


class Librivox(AudioBookSource):
    base_url = "https://librivox.org/api/feed/audiobooks/?%s&format=json"
    authors_url = "https://librivox.org/api/feed/authors/?%s&format=json"

    @classmethod
    def scrap_all_audiobooks(cls, limit=2000, offset=0):
        """
        Generator, yields LibrivoxAudioBook objects
        Args:
            limit:
            offset:
        """
        url = cls.base_url % \
              ("limit=" + str(limit) + "offset=" + str(offset) + "&extended=1")
        json_data = session.get(url).json()['books']
        for k in json_data:
            yield LibrivoxAudioBook(from_data=json_data[k])

    @classmethod
    def get_audiobook(cls, book_id):
        url = cls.base_url % ("id=" + str(book_id),)
        json_data = session.get(url).json()['books']
        return LibrivoxAudioBook(from_data=json_data[0])

    @classmethod
    def get_author(cls, author_id):
        url = cls.authors_url % ("id=" + str(author_id),)
        json_data = session.get(url).json()["authors"]
        return BookAuthor(from_data=json_data[0])

    @classmethod
    def search_audiobooks(cls, since=None, author=None, title=None, tag=None,
                          limit=25):
        """
        Args:
            since: a UNIX timestamp; returns all projects cataloged since that time
            author: all records by that author last name
            title: all matching titles
            tag: all projects of the matching tag

        Returns:
            list : list of LibrivoxAudioBook objects
        """
        searchterm = []
        if limit:
            # TODO validate
            searchterm.append("limit=" + str(limit))
        if since:
            # TODO validate
            searchterm.append("since=" + since)
        if author:
            searchterm.append("author=" + author)
        if title:
            searchterm.append("title=" + title)
        if tag:
            # TODO validate
            searchterm.append("tag=" + tag)
        if not searchterm:
            raise TypeError
        searchterm = "&".join(searchterm)
        url = cls.base_url % (searchterm,)
        json_data = session.get(url).json()
        if "error" in json_data:
            return []
        return [LibrivoxAudioBook(from_data=a) for a in json_data["books"]]


if __name__ == "__main__":
    book = Librivox.search_audiobooks(title="War of the worlds")[0]
    book.play_mplayer()
