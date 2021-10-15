from bs4 import BeautifulSoup
from threading import Thread
from rapidfuzz import process
from audiobooker.exceptions import UnknownAuthorIdException, \
    UnknownBookIdException, ScrappingError, UnknownGenreIdException, \
    UnknownAuthorException, UnknownBookException, UnknownGenreException
from audiobooker import AudioBook, BookAuthor, session, BookTag
from audiobooker.utils import random_user_agent


class AudioBookSource:
    base_url = ""
    popular_url = ""
    tags_url = ""
    authors_url = ""
    search_url = ""
    _cache = None
    _tags = []
    _tag_pages = {}

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
    def tags(self):
        return sorted(self._tags) or []

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
    def tag_pages(self):
        return self._tag_pages or {}

    @classmethod
    def scrap_tags(cls):
        return cls._tag_pages

    @staticmethod
    def scrap_all_audiobooks(limit=-1, offset=0):
        raise ScrappingError

    @classmethod
    def scrap_by_tag(cls, tag, limit=-1, offset=0):
        for book in cls.search_audiobooks(tag=tag):
            yield book

    @classmethod
    def get_all_audiobooks(self, limit=2000, offset=0):
        if self._cache is not None:
            return self._cache
        self._cache = [book for book in self.scrap_all_audiobooks(limit,
                                                                  offset)]
        return self._cache

    @classmethod
    def get_tag_id(cls, tag):
        if tag in cls._tags:
            return str(cls._tags.index(tag))
        tags = []
        for gen in cls.scrap_tags():
            tags.append(gen)
        tags = sorted(tags)
        return str(tags.index(tag))

    @classmethod
    def get_tag(cls, tag_id):
        if tag_id <= len(cls._tags):
            tag = cls._tags[tag_id]
        else:
            tags = []
            for tag in cls.scrap_tags():
                tags.append(tag)
            tags = sorted(tags)
            tag = tags[tag_id]
        return BookTag(tag_id=tag_id, name=tag)

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
                          tag=None, limit=25):
        """
        Args:
            since: a UNIX timestamp; returns all projects cataloged since that time
            author: all records by that author last name
            title: all matching titles
            tag: all projects of the matching tag
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
