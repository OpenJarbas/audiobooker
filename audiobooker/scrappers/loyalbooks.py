import feedparser
from audiobooker import AudioBook, BookGenre, BookAuthor
from audiobooker.scrappers import AudioBookSource
from audiobooker.utils.google_search import GoogleSearch


class LoyalBooksAudioBook(AudioBook):
    base_url = "http://www.loyalbooks.com"

    def __init__(self, title="", authors=None, description="", genres=None,
                 book_id="", runtime=0, url="", rss_url="", img="", rating=0,
                 language='english', from_data=None):
        self.rss_url = rss_url or url + "/feed"
        self.rating = rating
        AudioBook.__init__(self, title, authors, description, genres,
                           book_id, runtime, url, img, language)
        self.from_rss()

    def parse_page(self):
        title = self.soup.find("span", {"itemprop": "name"}).text
        description = self.soup.find("font",
                                     {"class": "book-description"}).text
        if self.soup.find(id="star1") is not None:
            rating = 1
        elif self.soup.find(id="star2") is not None:
            rating = 2
        elif self.soup.find(id="star3") is not None:
            rating = 3
        elif self.soup.find(id="star4") is not None:
            rating = 4
        elif self.soup.find(id="star5") is not None:
            rating = 5
        else:
            rating = 0
        author = self.soup.find("font", {"class": "book-author"})
        author_name = author.text.replace("By: ", "")

        names = author_name.split(" ")
        if len(names):
            first_name = names[0].strip()
            last_name = " ".join(names[1:]).strip()
            if not last_name:
                last_name = first_name
                first_name = ""
        else:
            first_name = ""
            last_name = author_name.strip()

        author_url = author.find("a")
        if author_url:
            author_url = self.base_url + author_url["href"]

        authors = [BookAuthor(url=author_url, first_name=first_name,
                              last_name=last_name)]

        genres = []
        genres_table = self.soup.find(summary="Genres for this book")
        if genres_table:
            genres_urls = genres_table.find_all("a")
            for a in genres_urls:
                url = self.base_url + a["href"]
                genre = a.text.strip()
                genre_id = LoyalBooks.get_genre_id(genre)
                genres.append(BookGenre(name=genre, url=url,
                                        genre_id=genre_id))

        img = self.soup.find("img", {"itemprop": "image", "class": "cover"})
        if img:
            img = self.base_url + img["src"]
        return {"description": description, "rating": rating, "genres": genres,
                "authors": authors, "title": title, "img": img}

    @property
    def rss_data(self):
        return feedparser.parse(self.rss_url)

    @property
    def streamer(self):
        for stream in self.rss_data["entries"]:
            try:
                for url in stream["links"]:
                    if url["type"] == 'audio/mpeg':
                        yield url["href"]
            except Exception as e:
                continue

    def from_json(self, json_data):
        AudioBook.from_json(self, json_data)
        self.rss_url = json_data.get("url_rss", self.rss_url)
        self.rating = json_data.get("rating", self.rating)

    def calc_runtime(self, data=None):
        data = data or self.rss_data["entries"]
        for rss_data in data:
            runtime = rss_data["itunes_duration"].split(":")
            if len(runtime) == 1:  # seconds
                self.runtime += int(runtime[0])
            elif len(runtime) == 2:  # minutes : seconds
                self.runtime += int(runtime[1]) + (int(runtime[0]) * 60)
            elif len(runtime) == 3:  # hours : minutes : seconds
                self.runtime += int(runtime[2]) + (int(runtime[1]) * 60) + \
                                (int(runtime[0]) * 120)

    def from_rss(self):
        rss = self.rss_data["entries"]

        if self.runtime < 1:
            self.calc_runtime()

        if not self.url:
            self.url = rss[0]["link"]

        for rss_data in rss:
            first_name = ""
            last_name = rss_data["author"]
            names = last_name.split(" ")
            if len(names) > 1:
                first_name = names[0].strip()
                last_name = " ".join(names[1:]).strip()
                if not last_name:
                    last_name = first_name
                    first_name = ""
            author = BookAuthor(from_data={"first_name": first_name,
                                           "last_name": last_name})
            if author.as_json not in self._authors:
                self._authors.append(author.as_json)

    def from_page(self):
        data = self.parse_page()
        if self.rating < 1:
            self.rating = data["rating"]
        if not self.title:
            self.title = data["title"]
        if not self._description:
            self._description = data["description"]

        self.img = data.get("img", self.img)
        for genre in data["genres"]:
            if genre.as_json not in self._genres:
                self._genres.append(genre.as_json)
        for author in data["authors"]:
            if author.as_json not in self._authors:
                self._authors.append(author.as_json)

    def __repr__(self):
        return "LoyalBooksAudioBook(" + str(self) + ", " + self.book_id + ")"


class LoyalBooks(AudioBookSource):
    base_url = "http://www.loyalbooks.com"
    popular_url = "http://www.loyalbooks.com"
    genres_url = "http://www.loyalbooks.com/genre-menu"
    search_url = "http://www.loyalbooks.com/search?q=%s"

    @classmethod
    def scrap_genres(cls):
        soup = cls._get_soup(cls._get_html(cls.genres_url))
        urls = soup.find("div", {"class": "left"}).find_all("a")
        bucket = {}
        for url in urls:
            genre = url.text
            url = url["href"]
            if url.startswith("/genre"):
                url = "http://www.loyalbooks.com" + url
                bucket[genre] = url
        cls._genres = list(bucket.keys())
        return bucket

    @property
    def genre_pages(self):
        if LoyalBooks._genre_pages is None:
            try:
                LoyalBooks._genre_pages = LoyalBooks.scrap_genres()
            except Exception as e:
                LoyalBooks._genre_pages = {
                    'Adventure': 'http://www.loyalbooks.com/genre/Adventure',
                    'Advice': 'http://www.loyalbooks.com/genre/Advice',
                    'Ancient Texts': 'http://www.loyalbooks.com/genre/Ancient_Texts',
                    'Animals': 'http://www.loyalbooks.com/genre/Animals',
                    'Art': 'http://www.loyalbooks.com/genre/Art',
                    'Biography': 'http://www.loyalbooks.com/genre/Biography',
                    'Children': 'http://www.loyalbooks.com/genre/Children',
                    'Classics (antiquity)': 'http://www.loyalbooks.com/genre/Classics_antiquity',
                    'Comedy': 'http://www.loyalbooks.com/genre/Comedy',
                    'Cookery': 'http://www.loyalbooks.com/genre/Cookery',
                    'Dramatic Works': 'http://www.loyalbooks.com/genre/Dramatic_Works',
                    'Economics': 'http://www.loyalbooks.com/genre/Economics_Political_Economy',
                    'Epistolary fiction': 'http://www.loyalbooks.com/genre/Epistolary_fiction',
                    'Essay/Short nonfiction': 'http://www.loyalbooks.com/genre/Essay_Short_nonfiction',
                    'Fairy tales': 'http://www.loyalbooks.com/genre/Fairy_tales',
                    'Fantasy': 'http://www.loyalbooks.com/genre/Fantasy',
                    'Fiction': 'http://www.loyalbooks.com/genre/Fiction',
                    'Historical Fiction': 'http://www.loyalbooks.com/genre/Historical_Fiction',
                    'History': 'http://www.loyalbooks.com/genre/History',
                    'Holiday': 'http://www.loyalbooks.com/genre/Holiday',
                    'Horror/Ghost stories': 'http://www.loyalbooks.com/genre/Horror_Ghost_stories',
                    'Humor': 'http://www.loyalbooks.com/genre/Humor',
                    'Instruction': 'http://www.loyalbooks.com/genre/Instruction',
                    'Languages': 'http://www.loyalbooks.com/genre/Languages',
                    'Literature': 'http://www.loyalbooks.com/genre/Literature',
                    'Memoirs': 'http://www.loyalbooks.com/genre/Memoirs',
                    'Music': 'http://www.loyalbooks.com/genre/Music',
                    'Mystery': 'http://www.loyalbooks.com/genre/Mystery',
                    'Myths/Legends': 'http://www.loyalbooks.com/genre/Myths_Legends',
                    'Nature': 'http://www.loyalbooks.com/genre/Nature',
                    'Non-fiction': 'http://www.loyalbooks.com/genre/Non-fiction',
                    'Philosophy': 'http://www.loyalbooks.com/genre/Philosophy',
                    'Play': 'http://www.loyalbooks.com/genre/Play',
                    'Poetry': 'http://www.loyalbooks.com/genre/Poetry',
                    'Politics': 'http://www.loyalbooks.com/genre/Politics',
                    'Psychology': 'http://www.loyalbooks.com/genre/Psychology',
                    'Religion': 'http://www.loyalbooks.com/genre/Religion',
                    'Romance': 'http://www.loyalbooks.com/genre/Romance',
                    'Satire': 'http://www.loyalbooks.com/genre/Satire',
                    'Science': 'http://www.loyalbooks.com/genre/Science',
                    'Science fiction': 'http://www.loyalbooks.com/genre/Science_fiction',
                    'Sea stories': 'http://www.loyalbooks.com/genre/Sea_stories',
                    'Self Published': 'http://www.loyalbooks.com/genre/Self-Published',
                    'Short stories': 'http://www.loyalbooks.com/genre/Short_stories',
                    'Spy stories': 'http://www.loyalbooks.com/genre/Spy_stories',
                    'Teen/Young adult': 'http://www.loyalbooks.com/genre/Teen_Young_adult',
                    'Tragedy': 'http://www.loyalbooks.com/genre/Tragedy',
                    'Travel': 'http://www.loyalbooks.com/genre/Travel',
                    'War stories': 'http://www.loyalbooks.com/genre/War_stories',
                    'Westerns': 'http://www.loyalbooks.com/genre/Westerns'}
        return self._genre_pages or {}

    @property
    def genres(self):
        if LoyalBooks._genres is None:
            try:
                LoyalBooks._genres = list(self.genre_pages.keys())
            except Exception as e:
                LoyalBooks._genres = ['Advice', 'Instruction',
                                      'Ancient Texts',
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
                                      'Philosophy', 'Mystery']
        return sorted(self._genres) or []

    @classmethod
    def _parse_book_div(cls, book):
        try:
            url = cls.base_url + book.find("a")[
                "href"].strip()
            img = book.find("img")
            if img:
                img = cls.base_url + img["src"].strip()
            name = book.find("b")
            if name:
                name = name.text.strip()
                author = book.text.replace(name, "").strip()
            else:
                name, author = book.find("div", {"class": "s-left"}) \
                    .text.split(" By: ")
            if book.find(id="star1") is not None:
                rating = 1
            elif book.find(id="star2") is not None:
                rating = 2
            elif book.find(id="star3") is not None:
                rating = 3
            elif book.find(id="star4") is not None:
                rating = 4
            elif book.find(id="star5") is not None:
                rating = 5
            else:
                rating = 0
            names = author.split(" ")
            if len(names):
                first_name = names[0].strip()
                last_name = " ".join(names[1:]).strip()
                if not last_name:
                    last_name = first_name
                    first_name = ""
            else:
                first_name = ""
                last_name = author.strip()
            return LoyalBooksAudioBook(title=name.strip(), url=url,
                                       img=img or "", rating=rating,
                                       authors=[BookAuthor(
                                           first_name=first_name,
                                           last_name=last_name).as_json])
        except Exception as e:
            pass  # probably an add
        return None

    @classmethod
    def scrap_by_genre(cls, genre, limit=-1, offset=0):
        """
        Generator, yields AudioBook objects
        """
        if genre not in cls._genre_pages:
            cls._genre_pages = cls.scrap_genres()
        if genre not in cls._genre_pages:
            return

        url = cls._genre_pages[genre] + "?page=" + str(offset)
        limit = int(limit)
        soup = cls._get_soup(cls._get_html(url))
        el = soup.find("table", {"class": "layout2-blue"})
        if el is None:
            el = soup.find("table", {"class": "layout3"})

        books = el.find_all("td", {"class": "layout2-blue"})
        if not len(books):
            books = el.find_all("td", {"class": "layout3"})

        for book in books:
            book = cls._parse_book_div(book)
            if book is None:
                continue
            book._genres = [BookGenre(name=genre, url=cls._genre_pages[genre],
                                      genre_id=cls.get_genre_id(genre)).as_json],
            yield book

        # check if last page reached
        pages = soup.find("div", {"class": "result-pages"}).text
        if ">" not in pages:
            return

        # check if limit crawled
        if limit > 0 and int(offset) > limit:
            return

        # crawl next page
        for book in cls.scrap_by_genre(genre, offset + 1, limit):
            yield book

    @classmethod
    def scrap_popular(cls, limit=-1, offset=0):
        """
        Generator, yields AudioBook objects
        """
        soup = cls._get_soup(cls._get_html(cls.popular_url))
        books = soup.find(summary="Audio books").find_all("td")
        for b in books:
            b = cls._parse_book_div(b)
            if b is not None:
                yield b

    @classmethod
    def search_audiobooks(cls, since=None, author=None, title=None, genre=None,
                          limit=25):
        """
        Args:
            since: a UNIX timestamp; returns all projects cataloged since that time
            author: all records by that author last name
            title: all matching titles
            genre: all projects of the matching genre

        Yields:
            AudioBook objects
        """
        query = ""
        if title:
            query += title + " "
        if genre:
            query += genre + " "
        if author:
            query += author + " "
        ## TODO find out how to get callback and nocache values
        """
        import requests
        url = LoyalBooks.search_url % query
        cx = "003017802411926626169:x3dul6qfjls"
        session = requests.Session()
        session.get(url)
        cx_token = session.get(
            "https://cse.google.com/cse.js?cx=003017802411926626169"
            ":x3dul6qfjls").text.split('"cse_token": "')[1].split('",')[0]
        params = {"rsz": "filtered_cse",
                  "num": "10",
                  "hl": "en",
                  "source": "gcsc",
                  "gss": ".com",
                  "cx": cx,
                  "q": query,
                  "safe": "off",
                  "cse_tok": cx_token,
                  "sort": ""#,
                  #"callback": "google.search.cse.api15358",
                  #"nocache": "1546515546857"
                  }
        print(session.get("https://cse.google.com/cse/element/v1",
                          data=params))
        """

        query += " site:" + LoyalBooks.base_url

        for url in GoogleSearch.search(query):
            if "www.loyalbooks.com/book/" not in url:
                continue
            if url.endswith("/feed"):
                continue
            yield LoyalBooksAudioBook(url=url)

        return []

    @classmethod
    def get_audiobook(cls, book_id):
        url = cls.base_url + '/book/' + book_id
        return LoyalBooksAudioBook(url=url)

    def scrap_all_audiobooks(self, limit=-1, offset=0):
        """
        Generator, yields AudioBook objects
        """
        for genre in self.genres:
            for book in self.scrap_by_genre(genre, limit, offset):
                yield book


if __name__ == "__main__":
    from pprint import pprint

    book = LoyalBooks.get_audiobook('Slave-Is-A-Slave-by-H-Beam-Piper')
    pprint(book.parse_page())

    for a in book.authors:
        print(a.as_json)

    print(LoyalBooks.get_genre(40))

    for book in LoyalBooks.search_audiobooks(author="Lovecraft"):
        pprint(book.as_json)

    scraper = LoyalBooks()
    for book in scraper.scrap_popular():
        pprint(book.as_json)

    for book in scraper.scrap_by_genre("Science fiction"):
        pprint(book.as_json)

    for book in scraper.scrap_all_audiobooks():
        pprint(book.as_json)
    pprint(scraper.scrap_genres())
    pprint(scraper.genres)
