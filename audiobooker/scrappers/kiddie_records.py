from audiobooker.scrappers import AudioBookSource


class KiddieRecords(AudioBookSource):
    """
        Warning: this website formatting is kinda ridiculous, if some stuff
        bellow seems weird it's because it is

    """
    base_url = "http://www.kiddierecords.com/"
    urls = ["http://www.kiddierecords.com/2005/index.htm",
            "http://www.kiddierecords.com/2006/index.htm",
            "http://www.kiddierecords.com/2007/index.htm",
            "http://www.kiddierecords.com/2009/index.htm",
            "http://www.kiddierecords.com/mgac/index_1.htm",
            "http://www.kiddierecords.com/mgac/index_2.htm",
            "http://www.kiddierecords.com/albums/index_1.htm",
            "http://www.kiddierecords.com/albums/index_2.htm",
            "http://www.kiddierecords.com/albums/index_3.htm",
            "http://www.kiddierecords.com/xmas/index.htm"]

    def __init__(self):
        raise RuntimeError("Scrapper deprecated ")

