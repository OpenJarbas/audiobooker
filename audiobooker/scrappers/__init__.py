import json
import subprocess
import requests
from bs4 import BeautifulSoup
from audiobooker.exceptions import UnknownAuthorIdException, \
    UnknownBookIdException, UnknownDurationError, ScrappingError, \
    UnknownGenreIdException, UnknownAuthorException, UnknownBookException, \
    UnknownGenreException, ParseErrorException


class BookGenre(object):
    """
    """

    def __init__(self, name="", genre_id="", url="", from_data=None):
        """

        Args:
            name:
            genre_id:
            from_data:
        """
        self.name = name
        self.genre_id = genre_id
        self.url = url
        if from_data:
            self.from_json(from_data)

    @property
    def as_json(self):
        return {"name": self.name, "id": self.genre_id, "url": self.url}

    def from_json(self, json_data):
        """

        Args:
            json_data:
        """
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
        if isinstance(json_data, BookGenre):
            json_data = json_data.as_json
        if not isinstance(json_data, dict):
            raise TypeError
        self.name = json_data.get("name", self.name)
        self.genre_id = json_data.get("id", self.genre_id)
        self.url = json_data.get("url", self.url)

    def __str__(self):
        """

        Returns:

        """
        return self.name

    def __repr__(self):
        """

        Returns:

        """
        return "BookGenre(" + str(self) + ", " + self.genre_id + ")"


class BookAuthor(object):
    """
    """

    def __init__(self, first_name="", last_name="", author_id="", url="",
                 from_data=None):
        """

        Args:
            first_name:
            last_name:
            author_id:
            from_data:
        """
        self.first_name = first_name
        self.last_name = last_name
        self.author_id = author_id
        self.url = url
        if from_data:
            self.from_json(from_data)

    def from_json(self, json_data):
        """

        Args:
            json_data:
        """
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
        if isinstance(json_data, BookAuthor):
            json_data = json_data.as_json
        if not isinstance(json_data, dict):
            print(json_data, type(json_data))
            raise TypeError
        self.first_name = json_data.get("first_name", self.first_name)
        self.last_name = json_data.get("last_name", self.last_name)
        self.author_id = json_data.get("id", self.author_id)
        self.url = json_data.get("url", self.url)

    @property
    def as_json(self):
        return {"first_name": self.first_name, "last_name": self.last_name,
                "id": self.author_id, "url": self.url}

    def __str__(self):
        """

        Returns:

        """
        return (self.first_name + " " + self.last_name).strip()

    def __repr__(self):
        """

        Returns:

        """
        return "BookAuthor(" + str(self) + ", " + self.author_id + ")"


class AudioBook(object):
    """
    """

    def __init__(self, title="", authors=None, description="", genres=None,
                 book_id="", runtime=0, url="", img="", language='english',
                 from_data=None):
        """

        Args:
            title:
            authors:
            description:
            genres:
            book_id:
            runtime:
            language:
            from_data:
        """

        self.img = img
        self.url = url
        self.title = title
        self._authors = authors or []
        self._description = description
        self._genres = genres or []
        self.book_id = book_id
        self.runtime = runtime
        self.lang = language.lower()
        if from_data:
            self.from_json(from_data)
        self.raw = from_data or {}

    def calc_runtime(self, data=None):
        raise UnknownDurationError

    def parse_page(self):
        raise ParseErrorException

    def from_page(self):
        data = self.parse_page()

    @property
    def html(self):
        try:
            return requests.get(self.url).text
        except Exception as e:
            try:
                return requests.get(self.url, verify=False).text
            except:
                return None

    @property
    def soup(self):
        return BeautifulSoup(self.html, "html.parser")

    @property
    def description(self):
        """

        Returns:

        """
        return self._description.strip()

    @property
    def streamer(self):
        """

        """
        return []

    @property
    def streams(self):
        """

        Returns:

        """
        return [s for s in self.streamer]

    def play_sox(self):
        """

        """
        self.play("play %1")

    def play_mplayer(self):
        """

        """
        self.play("mplayer %1")

    def play_vlc(self):
        """

        """
        self.play("cvlc %1 --play-and-exit")

    def play(self, cmd="cvlc %1 --play-and-exit"):
        """

        Args:
            cmd:
        """
        for stream_url in self.streamer:
            print("playing", stream_url)
            if isinstance(cmd, str):
                cmd = cmd.split(" ")
            if isinstance(cmd, list):
                play_cmd = cmd
                for idx, c in enumerate(cmd):
                    if c == "%1":
                        play_cmd[idx] = stream_url
                subprocess.call(" ".join(play_cmd), shell=True)
            else:
                raise TypeError

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

    @property
    def as_json(self):
        bucket = self.raw
        bucket["url"] = self.url
        bucket["img"] = self.img
        bucket["title"] = self.title
        bucket["authors"] = self._authors
        bucket["description"] = self._description
        bucket["genres"] = self._genres
        bucket["id"] = self.book_id
        bucket["runtime"] = self.runtime
        bucket["language"] = self.lang
        return bucket

    def from_json(self, json_data):
        """

        Args:
            json_data:
        """
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
        if not isinstance(json_data, dict):
            raise TypeError
        json_data = json_data or {}
        self.url = json_data.get("url", self.url)
        self.img = json_data.get("img",
                                 json_data.get("pic",
                                               json_data.get("image",
                                                             self.img)))
        self.title = json_data.get("title", json_data.get("name", self.title))
        self._authors = json_data.get("authors", self._authors)
        self._description = json_data.get("description", self._description)
        self._genres = json_data.get("genres", self._genres)
        self.book_id = json_data.get("id", self.book_id)
        self.runtime = json_data.get("runtime", self.runtime)
        self.lang = json_data.get('language',
                                  json_data.get('lang', self.lang)).lower()
        self.raw = json_data

    def __str__(self):
        """

        Returns:

        """
        return self.title

    def __repr__(self):
        """

        Returns:

        """
        return "AudioBook(" + str(self) + ", " + self.book_id + ")"


class AudioBookSource(object):
    base_url = ""
    popular_url = ""
    genres_url = ""
    authors_url = ""
    search_url = ""

    @property
    def genres(self):
        return sorted(['Advice', 'Instruction', 'Ancient Texts',
                       'Biography', 'Memoirs', 'Languages',
                       'Myths/Legends', 'Holiday', 'Art',
                       'Politics', 'Short stories', 'Romance',
                       'Essay/Short nonfiction', 'Fiction',
                       'Epistolary fiction', 'Science',
                       'Nature', 'Dramatic Works',
                       'Spy stories', 'History', 'Non-fiction',
                       'Historical Fiction', 'Play', 'Children',
                       'Satire', 'Humor',
                       'Classics (antiquity)', 'Travel',
                       'Religion', 'Adventure', 'Animals',
                       'Psychology', 'Sea stories',
                       'Horror/Ghost stories', 'Fantasy',
                       'Cookery', 'Poetry', 'Self Published',
                       'Westerns', 'Comedy', 'Music',
                       'Economics', 'Fairy tales', 'Tragedy',
                       'Teen/Young adult', 'Literature',
                       'War stories', 'Science fiction',
                       'Philosophy', 'Mystery'])

    @staticmethod
    def _get_html(url):
        try:
            return requests.get(url).text
        except Exception as e:
            return requests.get(url, verify=False).text

    @staticmethod
    def _get_soup(html):
        return BeautifulSoup(html, "html.parser")

    @staticmethod
    def scrap_popular(limit=-1, offset=0):
        """

        Generator, yields AudioBook objects

        Args:
            limit:
            offset:
        """
        raise ScrappingError

    @staticmethod
    def scrap_all_audiobooks(limit=-1, offset=0):
        """

        Generator, yields AudioBook objects

        Args:
            limit:
            offset:
        """
        raise ScrappingError

    @staticmethod
    def scrap_by_genre(genre, limit=-1, offset=0):
        """

        Generator, yields AudioBook objects

        Args:
            genre:
            limit:
            offset:
        """
        raise ScrappingError

    @staticmethod
    def get_all_audiobooks(limit=2000, offset=0):
        """

        Args:
            limit:
            offset:

        Returns:
            list : list of LibrivoxAudioBook objects

        """
        raise ScrappingError

    @staticmethod
    def get_genre_id(genre):
        """

        Args:
            genre:

        Returns:
            genre_id (str)

        """
        raise UnknownGenreException

    @staticmethod
    def get_genre(genre_id):
        """

        Args:
            genre_id:

        Returns:
            BookGenre

        """
        raise UnknownGenreIdException

    @staticmethod
    def get_audiobook(book_id):
        """

        Args:
            book_id:

        Returns:
            AudioBook

        """
        raise UnknownBookIdException

    @staticmethod
    def get_author(author_id):
        """

        Args:
            author_id:

        Returns:
            BookAuthor
        """
        raise UnknownAuthorIdException

    @staticmethod
    def get_audiobook_id(book):
        """

        Args:
            book:

        Returns:

            book_id (str)
        """
        raise UnknownBookException

    @staticmethod
    def get_author_id(author):
        """

        Args:
            author_id:

        Returns:
            author id (str)
        """
        raise UnknownAuthorException

    @staticmethod
    def search_audiobooks(since=None, author=None, title=None, genre=None):
        """

        Args:
            since: a UNIX timestamp; returns all projects cataloged since that time
            author: all records by that author last name
            title: all matching titles
            genre: all projects of the matching genre

        Returns:
            list : list of AudioBook objects
        """
        raise ScrappingError
