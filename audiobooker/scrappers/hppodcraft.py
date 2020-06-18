from audiobooker.scrappers import AudioBookSource


class HPPodcraft(AudioBookSource):
    base_url = "http://hppodcraft.com/"
    search_url = "http://hppodcraft.com/full-story-readings/"

    def __init__(self):
        raise RuntimeError("Webpage source changed, scrapper deprecated ")

