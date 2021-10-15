from pprint import pprint
from audiobooker.scrappers.loyalbooks import LoyalBooks

print(LoyalBooks().tags)
print(LoyalBooks.get_tag(40))

for book in LoyalBooks.search_audiobooks(author="Lovecraft"):
    pprint(book.as_json)

scraper = LoyalBooks()
#for book in scraper.scrap_popular():
#    pprint(book.as_json)

for book in scraper.scrap_by_tag("Science fiction"):
    pprint(book.as_json)

#pprint(scraper.scrap_tags())
#pprint(scraper.tags)
