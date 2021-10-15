import requests
from audiobooker import AudioBook, BookAuthor
from audiobooker.scrappers import AudioBookSource


class StephenKingAudioBook(AudioBook):
    base_url = "https://stephenkingaudiobooks.com/"

    def parse_page(self):
        author_name = "Stephen King"
        title = self.soup.find("h1", {"class": "title-page"}).text
        content = self.soup.find("div", {"class": "post-single clearfix"})
        desc = content.find("p").text
        if "–" in title:
            pts = title.split("–")
            author_name = pts[0]
            title = " ".join(pts[1:]).strip().lstrip(",")

        img = content.find("img")["src"]
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
        return "StephenKingAudioBook(" + str(
            self) + ", " + self.book_id + ")"


class StephenKingAudioBooks(AudioBookSource):
    base_url = "https://stephenkingaudiobooks.com"
    _tags = ["Harry Potter", 'Stephen King']
    _tag_pages = {
        "Harry Potter": "https://stephenkingaudiobooks.com/category/harry-potter/",
        'Stephen King': 'https://stephenkingaudiobooks.com/category/stephen-king/'}

    @classmethod
    def _parse_page(cls, html, limit=-1):
        soup = cls._get_soup(html)
        for entry in soup.find_all("article"):
            try:
                a = entry.find("a")
                img = entry.find("img")["src"]
                url = a["href"]
                title = a["title"]
                book = StephenKingAudioBook(title=title, url=url, img=img)
                book.from_page()  # parse url
                yield book
            except:
                continue
        if limit == -1 or limit > 0:
            limit -= 1
            next_page = soup.find("div", {"class": "nav-previous"})
            if next_page:
                html = requests.get(next_page.find("a")["href"]).text
                for ntry in cls._parse_page(html, limit=limit):
                    yield ntry

    @classmethod
    def scrap_by_tag(cls, tag, limit=-1, offset=0):
        for book in cls.search_audiobooks(tag=tag):
            yield book

    @classmethod
    def scrap_popular(cls, limit=-1, offset=0):
        html = requests.get(cls.base_url).text
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
        html = requests.get(cls.base_url, params={"s": query}).text
        return cls._parse_page(html)

    @classmethod
    def get_audiobook(cls, book_id):
        url = cls.base_url + '/' + book_id
        book = StephenKingAudioBook(url=url)
        return book

    @classmethod
    def scrap_all_audiobooks(cls, limit=-1, offset=0):
        return cls.scrap_popular()


if __name__ == "__main__":
    from pprint import pprint

    # for book in StephenKingAudioBooks.search_audiobooks(title="Dark Tower"):
    #     pprint(book.as_json)

    scraper = StephenKingAudioBooks()
    for book in scraper.scrap_popular():
        pprint(book.as_json)
