import requests
from audiobooker import AudioBook, BookTag, BookAuthor
from audiobooker.scrappers import AudioBookSource


class GoldenAudioBooksAudioBook(AudioBook):
    base_url = "https://goldenaudiobooks.com"

    def parse_page(self):
        author_name = "goldenaudiobooks"
        title = self.soup.find("h1", {"class": "entry-title"}).text
        content = self.soup.find("div", {"class": "entry-content"})
        desc = content.find("p").text
        if "–" in title:
            pts = title.split("–")
            author_name = pts[0]
            title = " ".join(pts[1:])

        img = content.find("img")["data-src"]
        names = author_name.strip().split(" ")
        if len(names):
            first_name = names[0].strip()
            last_name = " ".join(names[1:]).strip()
            if not last_name:
                last_name = first_name
                first_name = ""
        else:
            first_name = ""
            last_name = author_name.strip()

        authors = [BookAuthor(first_name=first_name, last_name=last_name)]

        streams = [s.find("a").text for s in content.find_all("audio")]

        return {"description": desc,
                "authors": authors,
                "title": title.strip(),
                "streams": streams,
                "rating": 0,
                "tags": [],
                "img": img}

    def from_page(self):
        data = self.parse_page()
        if not self.title:
            self.title = data["title"]
        if not self._description:
            self._description = data["description"]

        self.img = data.get("img", self.img)
        for tag in data["tags"]:
            if tag.as_json not in self._tags:
                self._tags.append(tag.as_json)
        for author in data["authors"]:
            if author.as_json not in self._authors:
                self._authors.append(author.as_json)
        self._stream_list = data["streams"]
        self.raw.update(data)

    def __repr__(self):
        return "GoldenAudioBooksAudioBook(" + str(
            self) + ", " + self.book_id + ")"


class GoldenAudioBooks(AudioBookSource):
    base_url = "https://goldenaudiobooks.com"
    popular_url = "https://goldenaudiobooks.com/category/bestsellers"

    @classmethod
    def scrap_tags(cls):
        bucket = {}
        soup = cls._get_soup(cls._get_html(cls.base_url))
        for tag in soup.find("aside",
                               {"class": "widget widget_categories"}). \
                find_all("a"):
            bucket[tag.text] = tag["href"]
        return bucket

    @property
    def tag_pages(self):
        if self._tag_pages is None:
            try:
                self._tag_pages = self.scrap_tags()
            except Exception as e:
                self._tag_pages = {
                    'Action': 'https://goldenaudiobooks.com/category/action/',
                    'Adults': 'https://goldenaudiobooks.com/category/adults-audios/',
                    'Adventure': 'https://goldenaudiobooks.com/category/adventure/',
                    'Autobiography & Biographies': 'https://goldenaudiobooks.com/category/autobiography-biographies/',
                    'Bestsellers': 'https://goldenaudiobooks.com/category/bestsellers/',
                    'Business': 'https://goldenaudiobooks.com/category/business/',
                    'Children': 'https://goldenaudiobooks.com/category/children/',
                    'Classic': 'https://goldenaudiobooks.com/category/classic/',
                    'Crime': 'https://goldenaudiobooks.com/category/crime/',
                    'Fantasy': 'https://goldenaudiobooks.com/category/audio-fantasy/',
                    'General Fiction': 'https://goldenaudiobooks.com/category/general-fiction/',
                    'Historical Fiction': 'https://goldenaudiobooks.com/category/historical-fiction/',
                    'History': 'https://goldenaudiobooks.com/category/history/',
                    'Horror': 'https://goldenaudiobooks.com/category/horror/',
                    'Humor': 'https://goldenaudiobooks.com/category/humors/',
                    'Literary': 'https://goldenaudiobooks.com/category/literary/',
                    'Literature & Fiction': 'https://goldenaudiobooks.com/category/literature-fiction/',
                    'Mystery': 'https://goldenaudiobooks.com/category/mystery/',
                    'Nonfiction': 'https://goldenaudiobooks.com/category/nonfiction/',
                    'Novel': 'https://goldenaudiobooks.com/category/novel/',
                    'Other': 'https://goldenaudiobooks.com/category/other/',
                    'Paranormal': 'https://goldenaudiobooks.com/category/paranormal-audiobooks/',
                    'Philosophy': 'https://goldenaudiobooks.com/category/philosophy/',
                    'Romance': 'https://goldenaudiobooks.com/category/audiobooks-romance/',
                    'Sci-Fi': 'https://goldenaudiobooks.com/category/science-fiction-audiobooks/',
                    'Science': 'https://goldenaudiobooks.com/category/science/',
                    'Self-help': 'https://goldenaudiobooks.com/category/self-help/',
                    'Short Story': 'https://goldenaudiobooks.com/category/short-story/',
                    'Spiritual & Religious': 'https://goldenaudiobooks.com/category/spiritual-religious/',
                    'Sports': 'https://goldenaudiobooks.com/category/sports/',
                    'Suspense': 'https://goldenaudiobooks.com/category/suspense/',
                    'Teen & Young Adult': 'https://goldenaudiobooks.com/category/teen-and-young-adult/',
                    'Thriller': 'https://goldenaudiobooks.com/category/thriller/',
                    'Uncategorized': 'https://goldenaudiobooks.com/category/uncategorized/',
                    'Westerns': 'https://goldenaudiobooks.com/category/westerns/'}
        return self._tag_pages or {}

    @classmethod
    def _parse_page(cls, html, limit=-1):
        soup = cls._get_soup(html)
        for entry in soup.find_all("div", {"class": "columns postbox"}):
            a = entry.find("a")
            img = entry.find("img")["data-src"]
            url = a["href"]
            title = a["title"]
            tags = []
            for a in entry.find("span", {"class": "cat-links"}). \
                    find_all("a"):
                tags.append({"name": a.text, "url": a["href"]})
            yield GoldenAudioBooksAudioBook(from_data={
                "title": title,
                "url": url,
                "img": img,
                "tags": tags
            })
        if limit == -1 or limit > 0:
            limit -= 1
            next_page = soup.find("a", {"class": "next page-numbers"})
            if next_page:
                html = requests.get(next_page["href"]).text
                for ntry in cls._parse_page(html, limit=limit):
                    yield ntry

    @classmethod
    def scrap_by_tag(cls, tag, limit=-1, offset=0):
        if tag in cls._tag_pages:
            url = cls._tag_pages[tag]
            html = requests.get(url).text
            for book in cls._parse_page(html):
                # TODO inject tag in book obj
                yield book
        else:
            for book in cls.search_audiobooks(tag=tag):
                yield book

    @classmethod
    def scrap_popular(cls, limit=-1, offset=0):
        html = requests.get(cls.popular_url).text
        return cls._parse_page(html)

    @classmethod
    def search_audiobooks(cls, since=None, author=None, title=None, tag=None,
                          limit=25):
        """
        Args:
            since: a UNIX timestamp; returns all projects cataloged since that time
            author: all records by that author last name
            title: all matching titles
            tag: all projects of the matching tag
        Yields:
            AudioBook objects
        """
        query = ""
        if title:
            query += title + " "
        if tag:
            query += tag + " "
        if author:
            query += author + " "
        html = requests.get(cls.base_url,
                            params={"s": query}).text
        return cls._parse_page(html)

    @classmethod
    def get_audiobook(cls, book_id):
        url = cls.base_url + '/' + book_id
        book = GoldenAudioBooksAudioBook(url=url)
        return book

    @classmethod
    def scrap_all_audiobooks(cls, limit=-1, offset=0):
        for tag in cls._tags:
            for book in cls.scrap_by_tag(tag, limit, offset):
                yield book


if __name__ == "__main__":
    from pprint import pprint

    book = GoldenAudioBooks.get_audiobook('andy-weir-artemis-audiobook/')
    # pprint(book.parse_page())
    for a in book.authors:
        # print(a.as_json)
        pass
    tags = GoldenAudioBooks.scrap_tags()
    # print(tags)

    for book in GoldenAudioBooks.search_audiobooks(author="Lovecraft"):
        pprint(book.as_json)

    scraper = GoldenAudioBooks()
    for book in scraper.scrap_popular():
        pprint(book.as_json)

    for book in scraper.scrap_by_tag("science-fiction-audiobooks"):
        pprint(book.as_json)

    for book in scraper.scrap_all_audiobooks():
        pprint(book.as_json)
