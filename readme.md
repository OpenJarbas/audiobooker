# AudioBooker

AudioBook scrapper and player

Currently supports Librivox, will be expanded with more sources over time

Leave a suggestion!

## Install

    pip install audiobooker
    
## Usage

    from audiobooker.librivox import Librivox
    
    author = Librivox.get_author("3534")
    print(author.last_name)
    
    book = Librivox.get_audiobook("127")
    pprint(book.title)
    
    books = Librivox.get_all_audiobooks(limit=50)    
    
    book = Librivox.search_audiobooks(title="Art of War")[0]
    
    print(book.title)
    print(book.description)
    print(book.authors)
    print(book.librivox_url)
    print(book.streams)
    print(book.rss_data)
    book.play()


## TODO

future scrappers

* http://hppodcraft.com
* http://www.kiddierecords.com/
* http://freeclassicaudiobooks.com/
* https://www.gutenberg.org/browse/categories/1
* http://www.openculture.com/freeaudiobooks
* http://www.loyalbooks.com
* https://www.storynory.com/
* http://etc.usf.edu/lit2go/
* https://www.learnoutloud.com/
* https://archive.org/details/MindWebs_201410/001CarcinomaAngels-NormanSpinrad.wav
* https://scribl.com
* http://www.audioanarchy.org/
* http://thoughtaudio.com/
