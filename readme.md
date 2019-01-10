# AudioBooker
[![Donate with Bitcoin](https://en.cryptobadges.io/badge/micro/1QJNhKM8tVv62XSUrST2vnaMXh5ADSyYP8)](https://en.cryptobadges.io/donate/1QJNhKM8tVv62XSUrST2vnaMXh5ADSyYP8)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://paypal.me/jarbasai)
<span class="badge-patreon"><a href="https://www.patreon.com/jarbasAI" title="Donate to this project using Patreon"><img src="https://img.shields.io/badge/patreon-donate-yellow.svg" alt="Patreon donate button" /></a></span>
[![Say Thanks!](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/JarbasAl)

AudioBook scrapper and player

Currently supports [Librivox](https://librivox.org/), [LoyalBooks](http://www.loyalbooks.com), [KiddieRecords](http://www.kiddierecords.com/) and [HPPodcraft](http://hppodcraft.com/full-story-readings/)
 
Will be expanded with more sources over time, suggestions and Pull Requests welcome!

## Install

    pip install audiobooker
    
## Usage

search libribox

    from audiobooker.scrappers.librivox import Librivox
    
    author = Librivox.get_author("3534")
    print(author.last_name)
    
    book = Librivox.get_audiobook("127")
    pprint(book.title)
    
    books = Librivox.get_all_audiobooks(limit=50)    
    
    book = Librivox.search_audiobooks(title="Art of War")[0]

interact with a book object
  
    print(book.title)
    print(book.description)
    print(book.authors)
    print(book.url)
    print(book.streams)
    print(book.rss_data)
    book.play()

search loyalbooks

    from audiobooker.scrappers.loyalbooks import LoyalBooks

    book = LoyalBooks.get_audiobook('Short-Science-Fiction-Collection-1')
    book.play()
    
    scraper = LoyalBooks()
    for book in scraper.scrap_by_genre("Science fiction"):
        print(book.as_json)
        
    for book in LoyalBooks.search_audiobooks(author="Lovecraft"):
        print(book.as_json)

search kid stories

    from audiobooker.scrappers.kiddie_records import KiddieRecords
    
    for b in KiddieRecords.search_audiobooks(genre="song"):
        print(b.as_json)
        b.play()
    
    for b in KiddieRecords.search_audiobooks(title="Snow White and the Seven Dwarfs"):
        print(b.as_json)

    for b in KiddieRecords.scrap_all_audiobooks():
        pprint(b.as_json)

