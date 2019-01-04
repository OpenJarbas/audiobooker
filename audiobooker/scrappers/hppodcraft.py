from audiobooker.exceptions import UnknownAuthorIdException, \
    UnknownBookIdException, UnknownAuthorException, UnknownBookException
from audiobooker import AudioBook, BookAuthor
from audiobooker.scrappers import AudioBookSource


class HPPodcraft(AudioBookSource):
    base_url = "http://hppodcraft.com/"
    search_url = "http://hppodcraft.com/full-story-readings/"

    @staticmethod
    def scrap_all_audiobooks(limit=-1, offset=0):
        """

        Generator, yields AudioBook objects

        Args:
            limit:
            offset:
        """
        soup = HPPodcraft._get_soup(
            HPPodcraft._get_html(HPPodcraft.search_url))
        i = 0
        for url in soup.find_all("a"):
            href = url["href"]
            if href.endswith(".mp3"):
                title = url["title"].replace("HP Lovecraft Literary Podcast "
                                             "- ", "")
                if not href.startswith(HPPodcraft.base_url):
                    href = HPPodcraft.base_url + href
                yield AudioBook(title=title, book_id=str(i),
                                stream_list=[href], url=HPPodcraft.search_url,
                                authors=[{"first_name": "Howard P.",
                                          "last_name": "Lovecraft",
                                          "id": "0",
                                          "url": "http://hppodcraft.com/"}])
                i += 1

    def get_audiobook(self, book_id):
        """

        Args:
            book_id:

        Returns:
            AudioBook

        """
        for b in self.get_all_audiobooks():
            if str(b.book_id) == str(book_id):
                return b
        raise UnknownBookIdException

    @staticmethod
    def get_author(author_id=0):
        """

        Args:
            author_id:

        Returns:
            BookAuthor
        """
        if str(author_id) == "0":
            return BookAuthor(from_data={"first_name": "Howard P.",
                                         "last_name": "Lovecraft",
                                         "id": "0",
                                         "url": "http://hppodcraft.com/"})
        raise UnknownAuthorIdException

    def get_audiobook_id(self, book):
        """

        Args:
            book:

        Returns:

            book_id (str)
        """
        for b in self.get_all_audiobooks():
            if b.title == book:
                return b.book_id
        raise UnknownBookException

    @staticmethod
    def get_author_id(author):
        """

        Args:
            author_id:

        Returns:
            author id (str)
        """
        if "lovecraft" in author.lower():
            return "0"
        raise UnknownAuthorException


if __name__ == "__main__":

    from pprint import pprint

    book_lib = HPPodcraft()

    for book in book_lib.scrap_all_audiobooks():
        pprint(book.as_json)
        book.play()
