from dataclasses import dataclass

from audiobooker.base import AudioBook, BookAuthor
from audiobooker.scrappers import AudioBookSource
from audiobooker.utils import get_soup


@dataclass
class AudioAnarchyAudioBook:
    url: str
    image: str = ""

    def parse_page(self) -> AudioBook:
        base_url = "http://www.audioanarchy.org/"
        soup = get_soup(self.url)
        streams = []
        for url in soup.find_all("a"):
            try:
                if not url["href"].endswith(".mp3"):
                    continue
                streams.append(base_url + url["href"])
            except:
                continue
        title = soup.find("title").text.split(" - ")[-1].split(" :: ")[-1]
        return AudioBook(
            title=title,
            streams=streams,
            image=self.image,
            tags=["Anarchy"],
            authors=[BookAuthor(last_name="Audio Anarchy")],
            language="en"
        )


class AudioAnarchy(AudioBookSource):
    base_url = "http://www.audioanarchy.org"

    def iterate_all(self):
        soup = get_soup(self.base_url)
        for entry in soup.find_all("div", {"id": "album"}):
            try:
                a = entry.find("a")
                img = entry.find("img")
                yield AudioAnarchyAudioBook(
                    url="https://www.audioanarchy.org/" + a["href"],
                    image="https://www.audioanarchy.org/" + img["src"]
                ).parse_page()
            except:
                continue


if __name__ == "__main__":
    from pprint import pprint

    scraper = AudioAnarchy()
    for book in scraper.iterate_all():
        pprint(book)
