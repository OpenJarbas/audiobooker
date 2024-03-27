import abc
from requests_cache import CachedSession
from datetime import timedelta
from audiobooker.exceptions import UnknownAuthorIdException, \
    UnknownBookIdException, ScrappingError, UnknownAuthorException, UnknownBookException
from audiobooker.utils import random_user_agent
from typing import List, Iterable
from audiobooker.base import AudioBook, BookAuthor, AudiobookNarrator


class AudioBookSource:
    expire_after = timedelta(hours=1)
    session = CachedSession(backend='memory', expire_after=expire_after)

    def search(self, query) -> Iterable[AudioBook]:
        # TODO fuzzy match instead
        for b in self.search_by_title(query):
            yield b
        for b in self.search_by_author(query):
            yield b
        for b in self.search_by_tag(query):
            yield b

    def search_by_narrator(self, query) -> Iterable[AudioBook]:
        for b in self.iterate_all():
            if b.narrator:
                if b.narrator.last_name.lower() in query.lower():
                    yield b

    def search_by_author(self, query) -> Iterable[AudioBook]:
        for b in self.iterate_all():
            for a in b.authors:
                if (a.last_name and a.last_name.lower() in query.lower()) or \
                        (a.first_name and a.first_name.lower() in query.lower()):
                    yield b

    def search_by_title(self, query) -> Iterable[AudioBook]:
        for b in self.iterate_all():
            if query.lower() in b.title.lower():
                yield b

    def search_by_tag(self, query) -> Iterable[AudioBook]:
        for b in self.iterate_all():
            if query.lower() in [t.lower() for t in b.tags]:
                yield b

    @abc.abstractmethod
    def iterate_all(self) -> Iterable[AudioBook]:
        pass

    def iterate_popular(self) -> Iterable[AudioBook]:
        return self.iterate_all()

    def iterate_by_author(self, author) -> Iterable[AudioBook]:
        for b in self.iterate_all():
            for a in b.authors:
                if a.last_name.lower() in author.lower():
                    yield b

    def iterate_by_tag(self, tag) -> Iterable[AudioBook]:
        for b in self.iterate_all():
            if tag in b.tags:
                yield b
