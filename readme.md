# AudioBooker

AudioBook scrapper

Currently supports [Librivox](https://librivox.org/) and [LoyalBooks](http://www.loyalbooks.com) 

Will be expanded with more sources over time, suggestions and Pull Requests welcome!

## Install

```bash
pip install audiobooker
```

## Usage

search librivox

```python
from audiobooker.scrappers.librivox import Librivox

author = Librivox.get_author("3534")
print(author.last_name)

book = Librivox.get_audiobook("127")
print(book.title)

books = Librivox.get_all_audiobooks(limit=50)    

book = Librivox.search_audiobooks(title="Art of War")[0]

# interact with a book object
print(book.title)
print(book.description)
print(book.authors)
print(book.url)
print(book.streams)
print(book.rss_data)
book.play()
```

search loyalbooks
```python
from audiobooker.scrappers.loyalbooks import LoyalBooks

book = LoyalBooks.get_audiobook('Short-Science-Fiction-Collection-1')
book.play()

scraper = LoyalBooks()
for book in scraper.scrap_by_genre("Science fiction"):
    print(book.as_json)
    
for book in LoyalBooks.search_audiobooks(author="Lovecraft"):
    print(book.as_json)
```
