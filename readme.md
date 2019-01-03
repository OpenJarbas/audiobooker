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
    
    books = Librivox.get_all_audiobooks()    
    
    book = Librivox.search_audiobooks(title="Art of War")[0]
    
    print(book.title)
    print(book.description)
    print(book.authors)
    print(book.librivox_url)
    print(book.streams)
    print(book.rss_data)
    book.play()
