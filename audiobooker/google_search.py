import urllib.request, urllib.error, urllib.parse
import math
from bs4 import BeautifulSoup


class GoogleSearch(object):
    USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/ 58.0.3029.81 Safari/537.36"
    SEARCH_URL = "https://google.com/search"
    TOTAL_SELECTOR = "#resultStats"
    RESULTS_PER_PAGE = 10
    DEFAULT_HEADERS = [
        ('User-Agent', USER_AGENT),
        ("Accept-Language", "en-US,en;q=0.5"),
    ]

    def total_results(self, query):
        opener = urllib.request.build_opener()
        opener.addheaders = GoogleSearch.DEFAULT_HEADERS
        response = opener.open(
            GoogleSearch.SEARCH_URL + "?q=" + urllib.parse.quote(query) + (
                ""))
        soup = BeautifulSoup(response.read(), "html.parser")
        response.close()
        totalText = \
            soup.select(GoogleSearch.TOTAL_SELECTOR)[0].text.split(
                "(")[0]
        total = int("".join([c for c in totalText if c.isdigit()]))
        return total

    def search(self, query, num_results=-1):
        total = self.total_results(query)
        if num_results < 1:
            pages = int(
                math.ceil(total // float(GoogleSearch.RESULTS_PER_PAGE)))
        else:
            pages = int(
                math.ceil(num_results // float(GoogleSearch.RESULTS_PER_PAGE)))

        result_num = 0
        for i in range(pages):
            start = i * GoogleSearch.RESULTS_PER_PAGE
            opener = urllib.request.build_opener()
            opener.addheaders = GoogleSearch.DEFAULT_HEADERS
            response = opener.open(
                GoogleSearch.SEARCH_URL + "?q=" + urllib.parse.quote(query) + (
                    "" if start == 0 else ("&start=" + str(start))))
            soup = BeautifulSoup(response.read(), "html.parser")
            response.close()
            results = self.parse_results(soup)
            result_num += len(results)

            if result_num > num_results and num_results > -1:
                d = result_num - num_results
                results = results[:len(results) - d]

            yield SearchResponse(results, total)

            if result_num > num_results and num_results > -1:
                return

    def parse_results(self, soup):
        bucket = []
        for a in soup.find_all("a"):
            try:
                url = a["href"]
                if not url.startswith("http"):
                    continue
                if "google" in url:
                    continue
                title = a.text.replace(url, "")
                bucket.append(SearchResult(title, url))
            except:
                pass

        return bucket


class SearchResponse(object):
    def __init__(self, results, total):
        self.results = results
        self.total = total


class SearchResult(object):
    def __init__(self, title, url):
        self.title = title
        self.url = url

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


if __name__ == "__main__":
    import sys

    search = GoogleSearch()
    i = 1
    query = " ".join(sys.argv[1:])
    if len(query) == 0:
        query = "Lovecraft audio drama"
    count = -1
    print("Fetching first " + str(count) + " results for \"" + query + "\"...")
    print("TOTAL: " + str(search.total_results(query)) + " RESULTS")
    for response in search.search(query, count):
        for result in response.results:
            print("RESULT #" + str(i) + ": " + result.url)
            print(result.title)
            i += 1
