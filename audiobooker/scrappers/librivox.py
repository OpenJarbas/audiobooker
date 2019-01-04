import requests
import feedparser
from audiobooker import AudioBook, BookGenre, BookAuthor
from audiobooker.scrappers import AudioBookSource


class LibrivoxAudioBook(AudioBook):
    """
    """

    def __init__(self, title="", authors=None, description="", genres=None,
                 book_id="", runtime=0, url="", img="", rss_url="",
                 copyright_year=0, language='english', from_data=None):
        """

        Args:
            title:
            authors:
            description:
            genres:
            book_id:
            runtime:
            url:
            rss_url:
            copyright_year:
            language:
            from_data:
        """
        AudioBook.__init__(self, title, authors, description, genres,
                           book_id, runtime, url, img, language)
        self.rss_url = rss_url
        self.copyright_year = copyright_year
        if from_data:
            self.from_json(from_data)
        self.raw = from_data or {}

    @property
    def description(self):
        """

        Returns:

        """
        return self._description.replace("<p>", "").replace("</p>", "") \
            .replace("(summary from Wikipedia)", "").strip().rstrip("\"") \
            .lstrip("\"")

    @property
    def rss_data(self):
        """

        Returns:

        """
        return feedparser.parse(self.rss_url)

    @property
    def streamer(self):
        """

        """
        for stream in self.rss_data["entries"]:
            try:
                yield stream['media_content'][0]["url"]
            except Exception as e:
                print(e)
                continue

    @property
    def authors(self):
        """

        Returns:

        """
        return [BookAuthor(from_data=a) for a in self._authors]

    @property
    def genres(self):
        """

        Returns:

        """
        return [BookGenre(from_data=a) for a in self._genres]

    def from_json(self, json_data):
        """

        Args:
            json_data:
        """
        AudioBook.from_json(self, json_data)
        self.url = json_data.get("url_librivox", self.url)
        self.runtime = json_data.get("totaltimesecs", self.runtime)
        self.copyright_year = json_data.get("copyright_year",
                                            self.copyright_year)
        self.rss_url = json_data.get("url_rss", self.rss_url)

    def __repr__(self):
        """

        Returns:

        """
        return "LibrivoxAudioBook(" + str(self) + ", " + self.book_id + ")"


class Librivox(AudioBookSource):
    """
    """
    base_url = "https://librivox.org/api/feed/audiobooks/?%s&format=json"
    authors_url = "https://librivox.org/api/feed/authors/?%s&format=json"

    @staticmethod
    def scrap_all_audiobooks(limit=2000, offset=0):
        """

        Generator, yields LibrivoxAudioBook objects

        Args:
            limit:
            offset:
        """
        url = Librivox.base_url % \
              ("limit=" + str(limit) + "offset=" + str(offset) + "&extended=1")
        json_data = requests.get(url).json()['books']
        for k in json_data:
            yield LibrivoxAudioBook(from_data=json_data[k])

    @staticmethod
    def get_audiobook(book_id):
        """

        Args:
            book_id:

        Returns:
            LibrivoxAudioBook

        """
        url = Librivox.base_url % ("id=" + str(book_id),)
        json_data = requests.get(url).json()['books']
        return LibrivoxAudioBook(from_data=json_data[0])

    @staticmethod
    def get_author(author_id):
        """

        Args:
            author_id:

        Returns:

        """
        url = Librivox.authors_url % ("id=" + str(author_id),)
        json_data = requests.get(url).json()["authors"]
        return BookAuthor(from_data=json_data[0])

    @staticmethod
    def search_audiobooks(since=None, author=None, title=None, genre=None,
                          limit=25):
        """

        Args:
            since: a UNIX timestamp; returns all projects cataloged since that time
            author: all records by that author last name
            title: all matching titles
            genre: all projects of the matching genre

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
        if genre:
            # TODO validate
            searchterm.append("genre=" + genre)
        if not searchterm:
            raise TypeError
        searchterm = "&".join(searchterm)
        url = Librivox.base_url % (searchterm,)
        json_data = requests.get(url).json()["books"]
        return [LibrivoxAudioBook(from_data=a) for a in json_data]


if __name__ == "__main__":
    book = Librivox.search_audiobooks(title="War of the worlds")[0]
    book.play_mplayer()
