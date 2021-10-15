import requests
from audiobooker import AudioBook
from audiobooker.scrappers import AudioBookSource


class DarkerProjectsAudioBook(AudioBook):
    base_url = "http://darkerprojects.com"

    def parse_page(self):
        streams = []
        for url in self.soup.find_all("a"):
            if url["href"].endswith(".mp3"):
                if url["href"] not in streams:
                    streams.append(url["href"])
        title = self.soup.find("title").text
        img = self.img

        return {"title": title.strip(),
                "streams": streams,
                "img": img}

    def from_page(self):
        data = self.parse_page()
        self.title = data["title"]
        self.img = data.get("img", self.img)
        self._stream_list = data["streams"]
        self.raw.update(data)

    def __repr__(self):
        return "DarkerProjectsAudioBook(" + str(
            self) + ", " + self.book_id + ")"


class DarkerProjects(AudioBookSource):
    base_url = "http://darkerprojects.com"
    _tag_pages = {'Autumn': 'http://darkerprojects.com/autumn/',
                  "Batman: No Man's Land": 'http://darkerprojects.com/batman-no-mans-land/',
                  'Behind The Scenes': 'http://darkerprojects.com/behind-the-scenes/',
                  'Dark Matter': 'http://darkerprojects.com/dark-matter/',
                  'Darker Projects: Uncovered': 'http://darkerprojects.com/dp-uncovered/',
                  'Doctor Who': 'http://darkerprojects.com/doctor-who/',
                  'Five Minute Fears': 'http://darkerprojects.com/five-minute-fears/',
                  'He-Man: The Parody': 'http://darkerprojects.com/he-man-the-parody/',
                  'Madness': 'http://darkerprojects.com/madness/',
                  'Night Terrors': 'http://darkerprojects.com/night-terrors/',
                  'Other Voices': 'http://darkerprojects.com/other-voices/',
                  'Outer Limits': 'http://darkerprojects.com/outer-limits/',
                  'Quantum Leap': 'http://darkerprojects.com/quantum-leap/',
                  'Quantum Retribution': 'http://darkerprojects.com/quantum-retribution/',
                  'Star Trek: Lost Frontier': 'http://darkerprojects.com/lostfrontier/',
                  'Star Trek: Section 31': 'http://darkerprojects.com/section31/',
                  'Tales From The Museum': 'http://darkerprojects.com/tales-from-the-museum/',
                  'Tales From The Museum: The Beginning': 'http://darkerprojects.com/tales-from-the-museum-the-beginning/',
                  'The Falcon Banner': 'http://darkerprojects.com/the-falcon-banner/'}

    @classmethod
    def _parse_page(cls, html, limit=-1):
        soup = cls._get_soup(html)
        for entry in soup.find_all("article"):
            try:
                if not entry.find("div", {"class": "powerpress_player"}):
                    continue  # no audio streams, text only post
                a = entry.find("a")
                desc = ""
                for p in entry.find_all("p"):
                    desc = p.text

                tags = []
                try:
                    cat = entry.find("span", {"class": "cat-links"}).find("a")
                    tags.append({"name": cat.text, "url": cat["href"]})
                except:
                    pass
                dl = entry.find("a", {"class": "powerpress_link_d"})
                yield DarkerProjectsAudioBook(
                    title=a.text,
                    description=desc,
                    stream_list=[dl["href"]],
                    tags=tags,
                    url=a["href"]
                )
            except:
                continue

    @classmethod
    def scrap_popular(cls, limit=-1, offset=0):
        html = requests.get(cls.base_url).text
        return cls._parse_page(html)

    @classmethod
    def scrap_tags(cls):
        html = requests.get(cls.base_url).text
        soup = cls._get_soup(html)
        collections = soup.find("div", {"class": "widget-area"})
        for ul in collections.find_all("li"):
            a = ul.find("a")
            cls._tag_pages[a.text] = a["href"]
        return cls._tag_pages

    @classmethod
    def scrap_collections(cls, limit=-1, offset=0):
        for tag in cls.scrap_tags():
            yield cls.get_collection(tag)

    @classmethod
    def get_collection(cls, collection):
        for tag, url in cls.scrap_tags().items():
            if tag == collection:
                html = requests.get(url).text
                streams = []
                for book in cls._parse_page(html):
                    streams += book.streams
                streams.reverse()
                return DarkerProjectsAudioBook(title=tag,
                                              stream_list=streams,
                                              url=url)
    @classmethod
    def search_audiobooks(cls, since=None, author=None, title=None, tag=None,
                          limit=25):
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
        book = DarkerProjectsAudioBook(url=url)
        return book

    @classmethod
    def scrap_all_audiobooks(cls, limit=-1, offset=0):
        return cls.scrap_collections()


if __name__ == "__main__":
    from pprint import pprint

    # for book in DarkerProjects.search_audiobooks(title="Dark Tower"):
    #     pprint(book.as_json)

    scraper = DarkerProjects()
    print(scraper.scrap_tags())
    exit()
    for book in scraper.scrap_collections():
        pprint(book.as_json)
