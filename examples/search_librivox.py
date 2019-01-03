from pprint import pprint
from audiobooker.scrappers.librivox import Librivox

author = Librivox.get_author("3534")
pprint(author.last_name)

book = Librivox.get_audiobook("127")
pprint(book.title)

pprint(Librivox.get_all_audiobooks())

book = Librivox.search_audiobooks(title="Art of War")[0]
pprint(book.title)
pprint(book.description)
pprint(book.authors)
pprint(book.url)
pprint(book.streams)
pprint(book.rss_data)
book.play()
