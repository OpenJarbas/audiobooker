# AudioBooker

AudioBook scrapper and player

Currently supports Librivox, will be expanded with more sources over time

Leave a suggestion!

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


## TODO

future scrappers

* http://hppodcraft.com
* http://www.kiddierecords.com/
* http://freeclassicaudiobooks.com/
* https://www.gutenberg.org/browse/categories/1
* http://www.openculture.com/freeaudiobooks
* https://www.storynory.com/
* http://etc.usf.edu/lit2go/
* https://www.learnoutloud.com/
* https://archive.org/details/MindWebs_201410/001CarcinomaAngels-NormanSpinrad.wav
* https://scribl.com
* http://www.audioanarchy.org/
* http://thoughtaudio.com/
