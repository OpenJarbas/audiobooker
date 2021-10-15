from pprint import pprint
from audiobooker.scrappers.librivox import Librivox

author = Librivox.get_author("3534")
pprint(author.last_name)

book = Librivox.get_audiobook("127")
pprint(book.title)

scraper = Librivox()
#pprint(scraper.get_all_audiobooks())

book = scraper.search_audiobooks(title="war of the worlds")[0]
pprint(book.title)
pprint(book.description)
pprint(book.authors)
pprint(book.url)
pprint(book.streams)
pprint(book.runtime)
pprint(book.rss_data)
#book.play()
a = ", ".join([au.first_name + au.last_name for au in book.authors])
pprint(a)
