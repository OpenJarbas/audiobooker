from bs4 import BeautifulSoup
from threading import Thread
from rapidfuzz import process
from audiobooker.exceptions import UnknownAuthorIdException, \
    UnknownBookIdException, ScrappingError, UnknownGenreIdException, \
    UnknownAuthorException, UnknownBookException, UnknownGenreException
from audiobooker import AudioBook, BookAuthor, session, BookGenre
from audiobooker.utils import random_user_agent


class AudioBookSource:
    base_url = ""
    popular_url = ""
    genres_url = ""
    authors_url = ""
    search_url = ""
    _cache = None
    _genres = []
    _genre_pages = {}

    @classmethod
    def populate_cache(self, books=None, threaded=False):
        if self._cache is None:
            if books:
                self._cache = books
                return
            if threaded:
                t = Thread(target=self.get_all_audiobooks,
                           daemon=True).start()
            else:
                self._cache = self.get_all_audiobooks()
        elif books:
            self._cache += books

    @property
    def genres(self):
        return sorted(self._genres) or []

    @staticmethod
    def _get_html(url):
        user_agent = random_user_agent()
        try:
            return session.get(url, headers={'User-Agent': user_agent}).text
        except Exception as e:
            return session.get(url, verify=False,
                                headers={'User-Agent': user_agent}).text

    @staticmethod
    def _get_soup(html):
        return BeautifulSoup(html, "html.parser")

    @classmethod
    def scrap_popular(cls, limit=-1, offset=0):
        raise ScrappingError

    @property
    def genre_pages(self):
        return self._genre_pages or {}

    @classmethod
    def scrap_genres(cls):
        return cls._genre_pages

    @staticmethod
    def scrap_all_audiobooks(limit=-1, offset=0):
        raise ScrappingError

    @classmethod
    def scrap_by_genre(cls, genre, limit=-1, offset=0):
        for book in cls.search_audiobooks(genre=genre):
            yield book

    @classmethod
    def get_all_audiobooks(self, limit=2000, offset=0):
        if self._cache is not None:
            return self._cache
        self._cache = [book for book in self.scrap_all_audiobooks(limit,
                                                                  offset)]
        return self._cache

    @classmethod
    def get_genre_id(cls, genre):
        if genre in cls._genres:
            return str(cls._genres.index(genre))
        genres = []
        for gen in cls.scrap_genres():
            genres.append(gen)
        genres = sorted(genres)
        return str(genres.index(genre))

    @classmethod
    def get_genre(cls, genre_id):
        if genre_id <= len(cls._genres):
            genre = cls._genres[genre_id]
        else:
            genres = []
            for genre in cls.scrap_genres():
                genres.append(genre)
            genres = sorted(genres)
            genre = genres[genre_id]
        return BookGenre(genre_id=genre_id, name=genre)

    @staticmethod
    def get_audiobook(book_id):
        raise UnknownBookIdException

    @staticmethod
    def get_author(author_id):
        raise UnknownAuthorIdException

    @staticmethod
    def get_audiobook_id(book):
        raise UnknownBookException

    @staticmethod
    def get_author_id(author):
        raise UnknownAuthorException

    @classmethod
    def search_audiobooks(self, since=None, author=None, title=None,
                          genre=None, limit=25):
        """
        Args:
            since: a UNIX timestamp; returns all projects cataloged since that time
            author: all records by that author last name
            title: all matching titles
            genre: all projects of the matching genre
            limit: max entries to return (int)

        Returns:
            list : list of AudioBook objects
        """
        # priority for title matches
        alll = self.get_all_audiobooks()
        if title:
            for res in process.extract(title, alll, limit=limit):
                match, score = res
                yield match
                alll.remove(match)

        # second author matches
        if author:
            choices = [" ".join([str(a) for a in b.authors]) for b in alll]
            for res in process.extract(author, choices, limit=limit):
                match, score = res
                match = alll[choices.index(match)]
                yield match
                alll.remove(match)
