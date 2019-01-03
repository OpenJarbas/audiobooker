from audiobooker.scrappers.loyalbooks import LoyalBooks

from pprint import pprint

book = LoyalBooks.get_audiobook('Short-Science-Fiction-Collection-1')
book.play()

print(LoyalBooks.get_genre(40))

scraper = LoyalBooks()
for book in scraper.scrap_by_genre("Science fiction"):
    pprint(book.as_json)

pprint(scraper.scrap_genres())
pprint(scraper.genres)
