from audiobooker import AudioBook, BookAuthor
from audiobooker.scrappers import AudioBookSource

from pprint import pprint


# not real streams
# read from csv or something
streams = ['Aldous Huxley, Brave New World, '
           'https://1fizorq.oloadcdn.net/dl/l/lhcTuuSF1qQv_hV0/Q3JE4LxtblQ/16+-+Brave+New+World+-+Aldous+Huxley+-+1932.mp3?mime=true',
           'Arthur C. Clarke, Rendezvous with Rama, '
           'https://1fizors.oloadcdn.net/dl/l/-3TKoZ6X1GdzknSE/bPk3Nk2bvCs/14+-+Rendezvous+With+Rama+-+Arthur+C+Clarke+-+1973.mp3?mime=true',
           'Philip K. Dick, Do Androids Dream of Electric Sheep, '
           'https://1fizoro.oloadcdn.net/dl/l/PvHcbH-InPYzh6Bq/Yhc2d-us-kA/12+-+Do+Androids+Dream+of+Electric+Sheep+-+Philip+K+Dick+-+1968.mp3?mime=true',
           'George Orwell, Animal Farm, https://www.youtube.com/watch?v=4Ln-Bfg6Wk0',
           'George Orwell, 1984, '
           'https://1fizorp.oloadcdn.net/dl/l/C76B03TG8T9wi-2z/vBhqbIHW5iM/Nineteen+Eighty+Four+-+George+Orwell.mp3?mime=true',
           'Arthur C. Clarke, 2001 A Space Odyssey, '
           'https://1fizorm.oloadcdn.net/dl/l/5YLhBL8cXOiOVqDh/-3w7Z_VvYCU/8+-+2001%3B+A+Space+Odyssey+-+Arthur+C+Clarke+-+1968.mp3?mime=true',
           'Arthur C. Clarke, Childhood’s End, '
           'https://1fizors.oloadcdn.net/dl/l/FsqNl_M7s_s54OeE/q2HkT0EYx8w/18+-+Childhood%27s+End+-+Arthur+C+Clarke+-+1954.mp3?mime=true',
           'Robert A. Heinlein, Starshio Troopers, '
           'https://1fizorn.oloadcdn.net/dl/l/W6xGJG_Ig2l_O7s8/XXegbOEAdz8/9+-+Starship+Troopers+-+Robert+A+Heinlein+-+1959.mp3?mime=true',
           'Robert A. Heinlein, The Moon is a Harsh Mistress, '
           'https://1fizorp.oloadcdn.net/dl/l/iHmjhmlTmw5RvaXnF4/8bwjgLgz0o0/19+-+The+Moon+is+a+Harsh+Mistress+-+Robert+A+Heinlein+-+1966.mp3?mime=true'
           ]

book_lib = AudioBookSource()

for book in streams:
    author, title, stream = book.split(",")

    audio_book = AudioBook(description="awesome book",
                           from_data={"title": title,
                                      "authors": [author],
                                      "streams": [stream]})

    book_lib.populate_cache([audio_book])

    author = BookAuthor(from_data=author)

for book in book_lib.search_audiobooks(title="androids", limit=1):
    print(book.title, book.authors)

for book in book_lib.search_audiobooks(author="Heinlein", limit=3):
    pprint(book.as_json)
