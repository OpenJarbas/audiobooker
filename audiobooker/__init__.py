import json
import subprocess
from bs4 import BeautifulSoup
from requests_cache import CachedSession
from datetime import timedelta

from audiobooker.exceptions import UnknownAuthorIdException, \
    UnknownBookIdException, UnknownDurationError, ScrappingError, \
    UnknownGenreIdException, UnknownAuthorException, UnknownBookException, \
    UnknownGenreException, ParseErrorException

expire_after = timedelta(hours=1)
session = CachedSession(backend='memory', expire_after=expire_after)


class BookGenre:
    def __init__(self, name="", genre_id="", url="", from_data=None):
        self.name = name
        self.genre_id = genre_id
        self.url = url
        if from_data:
            self.from_json(from_data)

    @property
    def as_json(self):
        return {"name": self.name, "id": self.genre_id, "url": self.url}

    def from_json(self, json_data):
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
        if isinstance(json_data, BookGenre):
            json_data = json_data.as_json
        if not isinstance(json_data, dict):
            raise TypeError
        self.name = json_data.get("name", self.name)
        self.genre_id = json_data.get("id", self.genre_id) or self.name
        self.url = json_data.get("url", self.url)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "BookGenre(" + str(self) + ", " + self.genre_id + ")"


class BookAuthor:
    def __init__(self, first_name="", last_name="", author_id="", url="",
                 from_data=None):
        self.first_name = first_name
        self.last_name = last_name
        self.first_name, self.last_name = self.normalize_name()
        self.author_id = author_id
        self.url = url
        if from_data:
            self.from_json(from_data)

    def normalize_name(self):
        author = " ".join([self.first_name, self.last_name])
        names = author.split(" ")
        last_name = " ".join(names[1:])
        first_name = names[0]
        return first_name, last_name

    def from_json(self, json_data):
        if isinstance(json_data, str):
            try:
                json_data = json.loads(json_data)
            except:
                json_data = {"last_name": json_data}
        if isinstance(json_data, BookAuthor):
            json_data = json_data.as_json
        if not isinstance(json_data, dict):
            print(json_data, type(json_data))
            raise TypeError
        self.first_name = json_data.get("first_name", self.first_name)
        self.last_name = json_data.get("last_name", self.last_name)
        self.first_name, self.last_name = self.normalize_name()
        self.author_id = json_data.get("id", self.author_id)
        self.url = json_data.get("url", self.url)

    @property
    def as_json(self):
        return {"first_name": self.first_name, "last_name": self.last_name,
                "id": self.author_id, "url": self.url}

    def __str__(self):
        return (self.first_name + " " + self.last_name).strip()

    def __repr__(self):
        return "BookAuthor(" + str(self) + ", " + self.author_id + ")"


class AudioBook:
    def __init__(self, title="", authors=None, description="", genres=None,
                 book_id="", runtime=0, url="", img="", language='english',
                 from_data=None, stream_list=None):
        self.img = img
        self.url = url
        self.title = title
        self._authors = authors or []
        self._description = description
        self._genres = genres or []
        self.book_id = book_id
        self.runtime = runtime
        self.lang = language.lower()
        self._stream_list = stream_list or []
        if not self.book_id and "/" in self.url:
            self.book_id = self.url.split("/")[-1]
        if from_data:
            self.from_json(from_data)
        self.raw = from_data or {}
        try:
            self.from_page()
        except:
            pass

    def calc_runtime(self, data=None):
        raise UnknownDurationError

    def parse_page(self):
        raise ParseErrorException

    def from_page(self):
        self.raw = self.parse_page()

    @property
    def html(self):
        try:
            return session.get(self.url).text
        except Exception as e:
            try:
                return session.get(self.url, verify=False).text
            except:
                return None

    @property
    def soup(self):
        return BeautifulSoup(self.html, "html.parser")

    @property
    def description(self):
        return self._description.strip()

    @property
    def streamer(self):
        for s in self._stream_list:
            yield s

    @property
    def streams(self):
        return [s for s in self.streamer]

    def play_sox(self):
        self.play("play %1")

    def play_mplayer(self):
        self.play("mplayer %1")

    def play_vlc(self):
        self.play("cvlc %1 --play-and-exit")

    def play(self, cmd="cvlc %1 --play-and-exit"):
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
        authors = []
        for a in self._authors:
            if isinstance(a, str):
                try:
                    a = json.loads(a)
                except Exception as e:
                    a = {"last_name": a}
            if isinstance(a, dict):
                authors += [a]
        return [BookAuthor(from_data=a) for a in authors]

    @property
    def genres(self):
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
        bucket["streams"] = self.streams
        return bucket

    def from_json(self, json_data):
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
        self._authors = self._authors or [json_data.get("author", "")]
        self._description = json_data.get("description", self._description)
        self._genres = json_data.get("genres", self._genres)
        self.book_id = json_data.get("id")
        self.runtime = json_data.get("runtime", self.runtime)
        self.lang = json_data.get('language',
                                  json_data.get('lang', self.lang)).lower()
        self._stream_list = json_data.get("streams", self._stream_list)
        self.raw = json_data
        if not self.book_id and "/" in self.url:
            self.book_id = self.url.split("/")[-1]

    def __str__(self):
        return self.title

    def __repr__(self):
        return "AudioBook(" + str(self) + ", " + self.book_id + ")"
