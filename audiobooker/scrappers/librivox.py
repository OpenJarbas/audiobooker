import requests
import json
import subprocess
import feedparser


class LibrivoxGenre(object):
    def __init__(self, name="", genre_id="", json_data=None):
        self.name = name
        self.genre_id = genre_id
        if json_data:
            self.from_json(json_data)

    def from_json(self, json_data):
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
        if not isinstance(json_data, dict):
            raise TypeError
        self.name = json_data.get("name", self.name)
        self.genre_id = json_data.get("id", self.genre_id)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "LibrivoxGenre(" + str(self) + ", " + self.genre_id + ")"


class LibrivoxAuthor(object):
    def __init__(self, first_name="", last_name="", author_id="",
                 json_data=None):
        self.first_name = first_name
        self.last_name = last_name
        self.author_id = author_id
        if json_data:
            self.from_json(json_data)

    def from_json(self, json_data):
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
        if not isinstance(json_data, dict):
            raise TypeError
        self.first_name = json_data.get("first_name", self.first_name)
        self.last_name = json_data.get("last_name", self.last_name)
        self.author_id = json_data.get("id", self.author_id)

    def __str__(self):
        return (self.first_name + " " + self.last_name).strip()

    def __repr__(self):
        return "LibrivoxAuthor(" + str(self) + ", " + self.author_id + ")"


class LibrivoxAudioBook(object):
    def __init__(self, title="", authors=None, description="", genres=None,
                 book_id="", runtime=0, url="", rss_url="", copyright_year=0,
                 language='english', json_data=None):

        self.title = title
        self._authors = authors or []
        self._description = description
        self._genres = genres or []
        self.book_id = book_id
        self.runtime = runtime
        self.librivox_url = url
        self.rss_url = rss_url
        self.copyright_year = copyright_year
        self.lang = language.lower()
        if json_data:
            self.from_json(json_data)
        self.raw = json_data or {}

    @property
    def description(self):
        return self._description.replace("<p>", "").replace("</p>", "") \
            .replace("(summary from Wikipedia)", "").strip().rstrip("\"") \
            .lstrip("\"")

    @property
    def rss_data(self):
        return feedparser.parse(self.rss_url)

    @property
    def streams(self):
        for stream in self.rss_data["entries"]:
            try:
                yield stream['media_content'][0]["url"]
            except Exception as e:
                print(e)
                continue

    def get_streams(self):
        return [s for s in self.streams]

    def play_sox(self):
        self.play("play %1")

    def play_mplayer(self):
        self.play("mplayer %1")

    def play_vlc(self):
        self.play("cvlc %1 --play-and-exit")

    def play(self, cmd="cvlc %1 --play-and-exit"):
        for stream_url in self.streams:
            if isinstance(cmd, str):
                cmd = cmd.replace("%1", stream_url)
            elif isinstance(cmd, list):
                for idx, c in enumerate(cmd):
                    if c == "%1":
                        cmd[idx] = stream_url
                        break
            else:
                raise TypeError
            subprocess.check_output(cmd, shell=True)

    @property
    def authors(self):
        return [LibrivoxAuthor(json_data=a) for a in self._authors]

    @property
    def genres(self):
        return [LibrivoxGenre(json_data=a) for a in self._genres]

    def from_json(self, json_data):
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
        if not isinstance(json_data, dict):
            raise TypeError
        json_data = json_data or {}
        self.title = json_data.get("title", self.title)
        self._authors = json_data.get("authors", self._authors)
        self._description = json_data.get("description", self._description)
        self._genres = json_data.get("genres", self._genres)
        self.book_id = json_data.get("id", self.book_id)
        self.runtime = json_data.get("totaltimesecs", self.runtime)
        self.librivox_url = json_data.get("url_librivox", self.librivox_url)
        self.copyright_year = json_data.get("copyright_year",
                                            self.copyright_year)
        self.lang = json_data.get('language', self.lang).lower()
        self.rss_url = json_data.get("url_rss", self.rss_url)
        self.raw = json_data

    def __str__(self):
        return self.title

    def __repr__(self):
        return "LibrivoxAudioBook(" + str(self) + ", " + self.book_id + ")"


class Librivox(object):
    librivox_audiobook_url = "https://librivox.org/api/feed/audiobooks/?%s&format=json"
    librivox_author_url = "https://librivox.org/api/feed/authors/?%s&format=json"

    @staticmethod
    def scrap_all_audiobooks():
        url = Librivox.librivox_audiobook_url % "extended=1"
        json_data = requests.get(url).json()['books']
        for k in json_data:
            yield LibrivoxAudioBook(json_data=json_data[k])

    @staticmethod
    def get_all_audiobooks():
        return [book for book in Librivox.scrap_all_audiobooks()]

    @staticmethod
    def get_audiobook(book_id):
        url = Librivox.librivox_audiobook_url % ("id=" + str(book_id),)
        json_data = requests.get(url).json()['books']
        return LibrivoxAudioBook(json_data=json_data[0])

    @staticmethod
    def get_author(author_id):
        url = Librivox.librivox_author_url % ("id=" + str(author_id),)
        json_data = requests.get(url).json()["authors"]
        return LibrivoxAuthor(json_data=json_data[0])

    @staticmethod
    def search_audiobooks(since=None, author=None, title=None, genre=None):
        searchterm = []
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
        url = Librivox.librivox_audiobook_url % (searchterm,)
        json_data = requests.get(url).json()["books"]
        return [LibrivoxAudioBook(json_data=a) for a in json_data]


if __name__ == "__main__":
    from pprint import pprint

    author = Librivox.get_author("3534")
    pprint(author.last_name)

    book = Librivox.get_audiobook("127")
    pprint(book.title)

    pprint(Librivox.get_all_audiobooks())

    book = Librivox.search_audiobooks(title="Art of War")[0]
    pprint(book.title)
    pprint(book.description)
    pprint(book.authors)
    pprint(book.librivox_url)
    pprint(book.get_streams())
    pprint(book.rss_data)
    book.play()
