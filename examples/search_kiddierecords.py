from pprint import pprint
from audiobooker.scrappers.kiddie_records import KiddieRecords


for b in KiddieRecords.search_audiobooks(
        title="Snow White and the Seven Dwarfs", limit=5):
    pprint(b.as_json)

for b in KiddieRecords.search_audiobooks(
        author="Irving Caesar", limit=3):
    pprint(b.as_json)

for b in KiddieRecords.search_audiobooks(genre="song"):
    pprint(b.as_json)
    if "prettiest song" in b.title.lower():
        b.play()


for b in KiddieRecords.scrap_all_audiobooks():
    pprint(b.as_json)
