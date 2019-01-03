from pprint import pprint
from audiobooker.scrappers.loyalbooks import LoyalBooks

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

pprint(scraper.scrap_genres())
pprint(scraper.genres)