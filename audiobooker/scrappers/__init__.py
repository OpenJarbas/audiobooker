import requests
from bs4 import BeautifulSoup
from threading import Thread
from fuzzywuzzy import process
from audiobooker.exceptions import UnknownAuthorIdException, \
    UnknownBookIdException, ScrappingError, UnknownGenreIdException, \
    UnknownAuthorException, UnknownBookException, UnknownGenreException
from audiobooker import AudioBook, BookAuthor
from audiobooker.utils.proxies import random_user_agent


class AudioBookSource(object):
    base_url = ""
    popular_url = ""
    genres_url = ""
    authors_url = ""
    search_url = ""
    _cache = None

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
        user_agent = random_user_agent()
        try:
            return requests.get(url, headers={'User-Agent': user_agent}).text
        except Exception as e:
            return requests.get(url, verify=False,
                                headers={'User-Agent': user_agent}).text

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

    def get_all_audiobooks(self, limit=2000, offset=0):
        """

        Args:
            limit:
            offset:

        Returns:
            list : list of LibrivoxAudioBook objects

        """

        if self._cache is not None:
            return self._cache
        self._cache = [book for book in self.scrap_all_audiobooks(limit,
                                                                  offset)]
        return self._cache

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


if __name__ == "__main__":
    # read from csv or something
    streams = ['Aldous Huxley, Brave New World, '
               'https://1fizorq.oloadcdn.net/dl/l/lhcTuuSF1qQv_hV0/Q3JE4LxtblQ/16+-+Brave+New+World+-+Aldous+Huxley+-+1932.mp3?mime=true',
               'Arthur C. Clarke, Rendezvous with Rama, '
               'https://1fizors.oloadcdn.net/dl/l/-3TKoZ6X1GdzknSE/bPk3Nk2bvCs/14+-+Rendezvous+With+Rama+-+Arthur+C+Clarke+-+1973.mp3?mime=true',
               'Philip K. Dick, Do Androids Dream of Electric Sheep, '
               'https://1fizoro.oloadcdn.net/dl/l/PvHcbH-InPYzh6Bq/Yhc2d-us-kA/12+-+Do+Androids+Dream+of+Electric+Sheep+-+Philip+K+Dick+-+1968.mp3?mime=true',
               'George Orwell, Animal Farm, https://www.youtube.com/watch?v=4Ln-Bfg6Wk0',
               'George Orwell, 1984, '
               'https://1fizorp.oloadcdn.net/dl/l/C76B03TG8T9wi-2z/vBhqbIHW5iM/Nineteen+Eighty+Four+-+George+Orwell.mp3?mime=true',
               'Arthur C. Clarke, 2001 A Space Odyssey, '
               'https://1fizorm.oloadcdn.net/dl/l/5YLhBL8cXOiOVqDh/-3w7Z_VvYCU/8+-+2001%3B+A+Space+Odyssey+-+Arthur+C+Clarke+-+1968.mp3?mime=true',
               'Arthur C. Clarke, Childhood’s End, '
               'https://1fizors.oloadcdn.net/dl/l/FsqNl_M7s_s54OeE/q2HkT0EYx8w/18+-+Childhood%27s+End+-+Arthur+C+Clarke+-+1954.mp3?mime=true',
               'Robert A. Heinlein, Starshio Troopers, '
               'https://1fizorn.oloadcdn.net/dl/l/W6xGJG_Ig2l_O7s8/XXegbOEAdz8/9+-+Starship+Troopers+-+Robert+A+Heinlein+-+1959.mp3?mime=true',
               'Robert A. Heinlein, The Moon is a Harsh Mistress, '
               'https://1fizorp.oloadcdn.net/dl/l/iHmjhmlTmw5RvaXnF4/8bwjgLgz0o0/19+-+The+Moon+is+a+Harsh+Mistress+-+Robert+A+Heinlein+-+1966.mp3?mime=true'
               ]

    from pprint import pprint

    book_lib = AudioBookSource()

    for book in streams:
        author, title, stream = book.split(",")

        audio_book = AudioBook(description="awesome book",
                               from_data={"title": title,
                                          "authors": [author],
                                          "streams": [stream]})

        book_lib.populate_cache([audio_book])

        author = BookAuthor(from_data=author)

    for book in book_lib.search_audiobooks(title="androids", limit=1):
        print(book.title, book.authors)

    for book in book_lib.search_audiobooks(author="Heinlein", limit=3):
        pprint(book.as_json)
