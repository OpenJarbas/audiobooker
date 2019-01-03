import json
import subprocess


class BookGenre(object):
    """
    """

    def __init__(self, name="", genre_id="", json_data=None):
        """

        Args:
            name:
            genre_id:
            json_data:
        """
        self.name = name
        self.genre_id = genre_id
        if json_data:
            self.from_json(json_data)

    def from_json(self, json_data):
        """

        Args:
            json_data:
        """
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
        if not isinstance(json_data, dict):
            raise TypeError
        self.name = json_data.get("name", self.name)
        self.genre_id = json_data.get("id", self.genre_id)

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

    def __init__(self, first_name="", last_name="", author_id="",
                 json_data=None):
        """

        Args:
            first_name:
            last_name:
            author_id:
            json_data:
        """
        self.first_name = first_name
        self.last_name = last_name
        self.author_id = author_id
        if json_data:
            self.from_json(json_data)

    def from_json(self, json_data):
        """

        Args:
            json_data:
        """
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
        if not isinstance(json_data, dict):
            raise TypeError
        self.first_name = json_data.get("first_name", self.first_name)
        self.last_name = json_data.get("last_name", self.last_name)
        self.author_id = json_data.get("id", self.author_id)

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
                 book_id="", runtime=0, url="", language='english',
                 json_data=None):
        """

        Args:
            title:
            authors:
            description:
            genres:
            book_id:
            runtime:
            language:
            json_data:
        """
        self.url = url
        self.title = title
        self._authors = authors or []
        self._description = description
        self._genres = genres or []
        self.book_id = book_id
        self.runtime = runtime
        self.lang = language.lower()
        if json_data:
            self.from_json(json_data)
        self.raw = json_data or {}

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
        return [BookAuthor(json_data=a) for a in self._authors]

    @property
    def genres(self):
        """

        Returns:

        """
        return [BookGenre(json_data=a) for a in self._genres]

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
        self.title = json_data.get("title", self.title)
        self._authors = json_data.get("authors", self._authors)
        self._description = json_data.get("description", self._description)
        self._genres = json_data.get("genres", self._genres)
        self.book_id = json_data.get("id", self.book_id)
        self.runtime = json_data.get("totaltimesecs", self.runtime)
        self.lang = json_data.get('language', self.lang).lower()
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
    """
    """

    @staticmethod
    def scrap_all_audiobooks(limit=2000, offset=0):
        """

        Generator, yields AudioBook objects

        Args:
            limit:
            offset:
        """
        return []

    @staticmethod
    def get_all_audiobooks(limit=2000, offset=0):
        """

        Args:
            limit:
            offset:

        Returns:
            list : list of LibrivoxAudioBook objects

        """
        return []

    @staticmethod
    def get_audiobook(book_id):
        """

        Args:
            book_id:

        Returns:
            AudioBook

        """
        return None

    @staticmethod
    def get_author(author_id):
        """

        Args:
            author_id:

        Returns:

        """
        return None

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
        return []
