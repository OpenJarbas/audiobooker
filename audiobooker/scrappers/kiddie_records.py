from audiobooker.exceptions import UnknownAuthorIdException, \
    UnknownBookIdException, UnknownAuthorException, UnknownBookException, \
    ParseErrorException

from audiobooker import AudioBook
from audiobooker.scrappers import AudioBookSource

from fuzzywuzzy import process


class KiddieAudioBook(AudioBook):

    def __init__(self, title="", authors=None, description="", genres=None,
                 book_id="", runtime=0, stream=None, url="", img="",
                 release_date=0, language='english', from_data=None):
        self.stream = stream
        self.release_date = release_date
        AudioBook.__init__(self, title, authors, description, genres,
                           book_id, runtime, url, img, language, from_data)

    @property
    def streamer(self):
        """

        """
        if not self.stream:
            raise ParseErrorException
        if isinstance(self.stream, list):
            for s in self.stream:
                yield s
            return
        yield self.stream

    @property
    def as_json(self):
        bucket = self.raw
        bucket["url"] = self.url
        bucket["img"] = self.img
        bucket["title"] = self.title
        bucket["authors"] = self._authors
        bucket["description"] = self._description
        bucket["format"] = self._description
        bucket["genres"] = self._genres
        bucket["id"] = self.book_id
        bucket["runtime"] = self.runtime
        bucket["language"] = self.lang
        bucket["release_date"] = self.release_date
        bucket["streams"] = [s for s in self.streamer]
        return bucket

    def calc_runtime(self, data=None):
        data = data or self.raw
        try:
            runtime = data["duration"].split(":")
            if len(runtime) == 1:  # seconds
                self.runtime += int(runtime[0])
            elif len(runtime) == 2:  # minutes : seconds
                self.runtime += int(runtime[1]) + (int(runtime[0]) * 60)
            elif len(runtime) == 3:  # hours : minutes : seconds
                self.runtime += int(runtime[2]) + (int(runtime[1]) * 60) + \
                                (int(runtime[0]) * 120)
        except:
            pass

    def from_json(self, json_data):
        """

        Args:
            json_data:
        """
        AudioBook.from_json(self, json_data)
        if not self.title:
            self.title = " ".join(json_data.get("titles", []))
        self._description = json_data.get("description", json_data.get(
            "format", self._description))
        self.book_id = json_data.get("release_id", self.book_id)
        self.stream = json_data.get("stream", self.stream)
        self.release_date = json_data.get("release_date", self.release_date)
        self.calc_runtime(json_data)

    def __repr__(self):
        """

        Returns:

        """
        return "KiddieRecordsAudioBook(" + self.__str__() + ", " + \
               self.book_id + ")"


class KiddieRecords(AudioBookSource):
    """
        Warning: this website formatting is kinda ridiculous, if some stuff
        bellow seems weird it's because it is

    """
    base_url = "http://www.kiddierecords.com/"
    urls = ["http://www.kiddierecords.com/2005/index.htm",
            "http://www.kiddierecords.com/2006/index.htm",
            "http://www.kiddierecords.com/2007/index.htm",
            "http://www.kiddierecords.com/2009/index.htm",
            "http://www.kiddierecords.com/mgac/index_1.htm",
            "http://www.kiddierecords.com/mgac/index_2.htm",
            "http://www.kiddierecords.com/albums/index_1.htm",
            "http://www.kiddierecords.com/albums/index_2.htm",
            "http://www.kiddierecords.com/albums/index_3.htm",
            "http://www.kiddierecords.com/xmas/index.htm"]

    @staticmethod
    def scrap_all_audiobooks(limit=-1, offset=0):
        """

        Generator, yields AudioBook objects


        Args:
            limit:
            offset:
        """

        for url in KiddieRecords.urls:
            buckets = []

            soup = KiddieRecords._get_soup(KiddieRecords._get_html(url))

            rows = soup.find_all("td")[2:]

            for idx, row in enumerate(rows):
                if not row:
                    continue
                text = row.find("p")
                if not text:
                    continue
                title = text.find_all("b")
                if not title:
                    continue

                # beware, there be dragons, data is not saved in a
                # structured way, website design is ridiculous, you can
                # probably waste time coming up with better rules
                bucket = {"url": url}
                published = author = release_format = duration = ""

                if len(title) > 2:
                    title = title[:2]

                # handle random \n that make no sense
                title = "\n".join([t.text for t in title])

                # handle \n that seem to be 2 titles in one release, maybe
                bucket["titles"] = [t.strip() for t in title.split("\n")]
                text = text.text.replace(title, "").strip()

                # regular file format? nah, at some point they gave up and
                # started adding youtube videos instead of real streams
                if 'Launch Stream' in text or 'Youtube' in text:
                    # some entries decided to include the streams inside the
                    # bold tag that usually is reserved for titles...
                    text = text.replace('Launch Stream', "") \
                        .replace('| Download Zip File', "")

                # randomly get empty strings because of stray \n ....
                components = [a.strip() for a in text.split("\n") if a.strip()]

                if len(components) == 0:
                    # these ones have their own div!
                    title = None
                    for p in row.find_all("font", {"size": 1}):
                        p = " ".join([a.strip() for a in p.text.split("\n")])
                        if not title:
                            title = p
                            bucket["titles"] = [t.strip() for t in
                                                title.split("\n")]
                        else:
                            author = p
                    # TODO scrap other fields not in soup
                    # failing mainly in http://www.kiddierecords.com/mgac/index_2.htm

                elif len(components) == 4:
                    author, published, release_format, duration = components
                # at some point putting all info also became optional
                elif len(components) == 3:
                    author, published, duration = components
                else:

                    # yep, even less info in a couple of them, can't depend
                    # on order...
                    for idx, c in enumerate(components):
                        c = c.strip()
                        if c.startswith("(1)") or c.startswith("(2)"):
                            release_format = c
                            components[idx] = ""
                        elif "Total Time:" in c:
                            duration = c
                            components[idx] = ""

                    # let's ensure we didn't miss other misbehaving entries
                    components = [c for c in components if c]
                    if len(components):
                        raise ParseErrorException

                bucket["authors"] = author.strip().split(" and ")
                if "©" in published:
                    bucket["release_id"], bucket["release_date"] = \
                        published.strip().split("©")
                else:
                    bucket["release_id"] = published.strip()
                bucket["format"] = release_format.strip()
                bucket["duration"] = duration \
                    .replace("Total Time: ", "").strip()

                # save for building AudioBook object later
                if bucket not in buckets:
                    buckets.append(bucket)

            # lazy find all streams by file extension,
            # assuming 1-to-1 match with buckets
            # NOTE bad assumption, corner cases creeped up
            el = soup.find_all("a")[8:]

            streams = [a["href"] for a in el if
                       ".zip" not in a["href"]
                       and not a["href"].endswith(".htm")]

            # lazy find all pics
            #  1-to-1 match with buckets
            el = soup.find_all("img")[1:]
            _index = url.split("/")[-1]
            pics = [url.replace(_index, pic["src"]) for pic in el]

            if not len(streams) == len(pics) == len(buckets):
                # NOTE Hack mentioned above, unlike with pics we can
                # not assure 1-to-1 match between buckets and streams
                # TODO FIX ME with proper parsing
                streams, pics, buckets = KiddieRecords._hack_fix_parsing(
                    streams, pics, buckets, url)

            # re check if fixes fixed everything
            if len(streams) == len(pics) == len(buckets):
                # everything checks out
                for idx, bucket in enumerate(buckets):
                    bucket["stream"] = streams[idx]
                    bucket["img"] = pics[idx]

                    yield KiddieAudioBook(from_data=bucket)
            else:
                raise ParseErrorException

    @staticmethod
    def _hack_fix_parsing(streams, pics, buckets, url):
        """ TODO FIX ME , bad asumption of 1-to-1 correspondence,
        that was true for most part/pages but not always"""

        if len(buckets) > len(pics):
            # parsed too many buckets
            raise ParseErrorException

        if len(streams) < len(buckets):
            # one entry is grayed out and has no stream
            if url == "http://www.kiddierecords.com/2007/index.htm":
                streams.insert(21, " ")
            else:
                raise ParseErrorException
        elif len(streams) > len(buckets):

            # Uncle Dave's Kiddie Christmas Collections entry messes
            # things up, it has 3 streams, we need to merge them into a
            # single index
            volumes = [a for a in streams if "/streams/volume_" in a]
            if len(volumes):
                streams.remove(volumes[1])
                streams.remove(volumes[2])
                streams[streams.index(volumes[0])] = volumes

                # in this same page another entry breaks things by randomly
                # deciding to name the stream differently, Spike Jones |
                # Jimmy Boyd, we need to merge these 2 streams
                bad_streans = ["http://youtu.be/oTLPMdsGgeQ",
                               "http://youtu.be/q8E1WafpFvo"]
                streams.remove(bad_streans[0])
                streams[streams.index(bad_streans[1])] = bad_streans
                # print(streams.index(bad_streans))  # should be 5

            if url == "http://www.kiddierecords.com/mgac/index_1.htm":
                # youtube + streams in some entries
                groups = [
                    [
                        "http://www.kiddierecords.com/mgac/streams/Dennis_the_Menace.m3u",
                        "http://youtu.be/Vlj7vqSDbqo"],
                    [
                        "http://www.kiddierecords.com/mgac/streams/The_Brave_Engineer.m3u",
                        "http://www.youtube.com/watch?v=SIrjnWKM9Tw"],
                    [
                        "http://www.kiddierecords.com/mgac/streams/Ferdinand_the_Bull.m3u",
                        "http://www.youtube.com/watch?v=0nSBxrFsLTY"],
                    [
                        "http://www.kiddierecords.com/mgac/streams/Carbon_the_Copy_Cat.m3u",
                        "http://youtu.be/_hg2ocEMET4"]
                ]
                for group in groups:
                    streams.remove(group[1])
                    streams[streams.index(group[0])] = group

            elif url == "http://www.kiddierecords.com/mgac/index_2.htm":

                # TODO component parsing for this page needs improvement
                # since its failing on a few fields it is considering a
                # duplicate entry for different Snow White and the Seven
                # Dwarfs releases
                missing_bucket = {
                    'authors': ['Lyn Murray Orchestra and Chorus'],
                    'duration': '23:25',
                    'format': '(4) 10" 78RPM record album with booklet',
                    'release_id': 'Decca A-368',
                    'titles': ['Snow White and the Seven Dwarfs'],
                    'url': 'http://www.kiddierecords.com/mgac/index_2.htm'}
                buckets.insert(69, missing_bucket)

        return streams, pics, buckets

    @staticmethod
    def get_audiobook(book_id):
        """

        Args:
            book_id:

        Returns:
            AudioBook

        """
        for b in KiddieRecords.get_all_audiobooks(cache=True):
            if b.book_id == book_id:
                return b
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
        for b in KiddieRecords.get_all_audiobooks(cache=True):
            if b.title == book:
                return b
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
            since: a year; returns all projects released since that time
            author: all records by that author last name
            title: all matching titles
            genre: all projects of the matching genre

        Yields:
            AudioBook objects
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

        # TODO genre, somehow need to catalog songs vs stories etc.
        # comparing same as title for now
        if genre:
            for res in process.extract(genre, alll, limit=limit):
                match, score = res
                yield match
                alll.remove(match)


if __name__ == "__main__":
    from pprint import pprint

    scraper = KiddieRecords()
    for b in scraper.search_audiobooks(
            title="Snow White and the Seven Dwarfs"):
        print(b.as_json)

    for b in KiddieRecords.scrap_all_audiobooks():
        pprint(b.as_json)
