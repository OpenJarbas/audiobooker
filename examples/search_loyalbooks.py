from pprint import pprint
from audiobooker.scrappers.loyalbooks import LoyalBooks

print(LoyalBooks().genres)
print(LoyalBooks.get_genre(40))

for book in LoyalBooks.search_audiobooks(author="Lovecraft"):
    pprint(book.as_json)

scraper = LoyalBooks()
#for book in scraper.scrap_popular():
#    pprint(book.as_json)

for book in scraper.scrap_by_genre("Science fiction"):
    pprint(book.as_json)

#pprint(scraper.scrap_genres())
#pprint(scraper.genres)
