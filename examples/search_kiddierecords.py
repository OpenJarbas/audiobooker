from pprint import pprint
from audiobooker.scrappers.kiddie_records import KiddieRecords

scraper = KiddieRecords()

for b in scraper.search_audiobooks(
        title="Snow White and the Seven Dwarfs", limit=5):
    pprint(b.as_json)

for b in scraper.search_audiobooks(
        author="Irving Caesar", limit=3):
    pprint(b.as_json)

for b in scraper.search_audiobooks(genre="song"):
    pprint(b.as_json)
    if "prettiest song" in b.title.lower():
        b.play()

for b in scraper.scrap_all_audiobooks():
    pprint(b.as_json)
