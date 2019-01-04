import requests
import math
from bs4 import BeautifulSoup
from itertools import cycle
from audiobooker.utils.proxies import get_proxies, random_user_agent, \
    USER_AGENTS
from audiobooker.exceptions import RateLimitedError


class GoogleSearch(object):
    SEARCH_URL = "https://google.com/search"
    TOTAL_SELECTOR = "#resultStats"
    RESULTS_PER_PAGE = 10
    RATE_LIMITED = "Our systems have detected unusual traffic from your computer"
    PROXIES = []
    PROXY_POOL = cycle(PROXIES)
    USER_AGENT_POOL = cycle(USER_AGENTS)
    CURRENT_PROXY = None
    CURRENT_USER_AGENT = None
    PROXY_FALLBACK = False

    def __init__(self, proxied=False, proxy_list=None, fallback=False):

        if proxied:
            self.PROXY_FALLBACK = True
            self.next_proxy()
        elif fallback:
            self.PROXY_FALLBACK = True

        if proxy_list:
            GoogleSearch.PROXIES = proxy_list or []

    @staticmethod
    def next_proxy():
        # Get a proxy from the pool
        if not len(GoogleSearch.PROXIES):
            GoogleSearch.reset_proxies()
        GoogleSearch.CURRENT_PROXY = next(GoogleSearch.PROXY_POOL)
        GoogleSearch.CURRENT_USER_AGENT = next(GoogleSearch.USER_AGENT_POOL)

    @staticmethod
    def reset_proxies():
        print("refreshing proxy list")
        GoogleSearch.PROXIES = get_proxies(25)
        GoogleSearch.PROXY_POOL = cycle(GoogleSearch.PROXIES)

    @staticmethod
    def remove_proxy(proxy):
        if proxy in GoogleSearch.PROXIES:
            print("removing bad proxy", proxy)
            GoogleSearch.PROXIES.remove(proxy)
            GoogleSearch.PROXY_POOL = cycle(GoogleSearch.PROXIES)
            if GoogleSearch.CURRENT_PROXY == proxy:
                GoogleSearch.next_proxy()

    @staticmethod
    def make_request(url, data=None, user_agent=None, proxy=None):
        try:
            user_agent = user_agent or GoogleSearch.CURRENT_USER_AGENT
            if user_agent is None:
                user_agent = random_user_agent()
            proxy = proxy or GoogleSearch.CURRENT_PROXY
            if proxy:
                print("using proxy", proxy)
            if data is not None and proxy is not None:
                response = requests.get(url, data,
                                        headers={
                                            'User-Agent': user_agent,
                                            "Accept-Language": "en-US,en;q=0.5"
                                        },
                                        proxies={"http": proxy,
                                                 "https": proxy})
            elif data is not None:
                response = requests.get(url, data,
                                        headers={
                                            'User-Agent': user_agent,
                                            "Accept-Language": "en-US,en;q=0.5"
                                        })
            elif proxy is not None:
                response = requests.get(url,
                                        headers={
                                            'User-Agent': user_agent,
                                            "Accept-Language": "en-US,en;q=0.5"
                                        },
                                        proxies={"http": proxy,
                                                 "https": proxy})
            else:
                response = requests.get(url,
                                        headers={
                                            'User-Agent': user_agent,
                                            "Accept-Language": "en-US,en;q=0.5"
                                        })
        except Exception as e:
            print(e)
            GoogleSearch.remove_proxy(proxy)
            raise
        return response.text

    @staticmethod
    def get_soup(url, data=None):
        try:
            html = GoogleSearch.make_request(url, data)
            soup = BeautifulSoup(html, "html.parser")
            if GoogleSearch.RATE_LIMITED in soup.text:
                raise RateLimitedError("Google banned IP address")
            return soup
        except RateLimitedError as e:
            if GoogleSearch.PROXY_FALLBACK:
                GoogleSearch.remove_proxy(GoogleSearch.CURRENT_PROXY)
                if len(GoogleSearch.PROXIES):
                    return GoogleSearch.get_soup(url, data)
                raise RateLimitedError("Google banned IP of all proxies")
            raise

    @staticmethod
    def total_results(query):
        soup = GoogleSearch.get_soup(GoogleSearch.SEARCH_URL, {"q": query})
        try:
            totalText = \
                soup.select(GoogleSearch.TOTAL_SELECTOR)[0].text.split("(")[0]
        except IndexError:
            GoogleSearch.next_proxy()
            if len(GoogleSearch.PROXIES):
                return GoogleSearch.total_results(query)
            raise
        total = int("".join([c for c in totalText if c.isdigit()]))
        return total, soup

    @staticmethod
    def search(query, num_results=-1):
        total, soup = GoogleSearch.total_results(query)
        if num_results < 1:
            pages = int(
                math.ceil(total // float(GoogleSearch.RESULTS_PER_PAGE)))
        else:
            pages = int(
                math.ceil(num_results // float(GoogleSearch.RESULTS_PER_PAGE)))
        if pages < 1:
            pages = 1
        result_num = 0
        for i in range(pages):
            start = i * GoogleSearch.RESULTS_PER_PAGE

            params = {"q": query}
            if start > 0:
                params["start"] = start
                soup = GoogleSearch.get_soup(GoogleSearch.SEARCH_URL, params)
            results = GoogleSearch.parse_results(soup)
            result_num += len(results)

            if result_num > num_results and num_results > -1:
                d = result_num - num_results
                results = results[:len(results) - d]

            for idx, r in enumerate(results):
                r.num = idx + start
                r.total = total
                yield r

            if result_num > num_results and num_results > -1:
                return

    @staticmethod
    def parse_results(soup):
        bucket = []
        for a in soup.find_all("a"):
            try:
                url = a["href"]
                if url.startswith("/url?q="):
                    url = url.replace("/url?q=", "")
                elif url.startswith("/search?ie=UTF-8&q=related:"):
                    url = url.replace("/search?ie=UTF-8&q=related:", "")
                if not url.startswith("http"):
                    continue
                if "google" in url:
                    continue
                title = a.text.replace(url, "")
                bucket.append(SearchResult(title, url))
            except:
                pass

        return bucket


class SearchResult(object):
    def __init__(self, title, url, num=1, total=1):
        self.title = title
        self.url = url
        self.num = num
        self.total = 1

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


if __name__ == "__main__":
    query = "lovecraft audio drama"
    count = 5
    google = GoogleSearch()
    print("Fetching first " + str(count) + " results for \"" + query + "\"...")
    for result in google.search(query, count):
        print("result #", result.num, " of ", result.total)
        print(result.url)
        print(result.title)
