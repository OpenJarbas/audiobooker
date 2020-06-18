from bs4 import BeautifulSoup
from audiobooker.utils import random_user_agent
from audiobooker.exceptions import RateLimitedError
from audiobooker import session


class GoogleSearch:
    SEARCH_URL = "https://google.com/search"
    RATE_LIMITED = "Our systems have detected unusual traffic from your computer"

    @staticmethod
    def _request(url, params=None, user_agent=None):
        params = params or {}
        try:
            user_agent = user_agent or random_user_agent()
            response = session.get(url, params=params,
                                   headers={
                                       'User-Agent': user_agent,
                                       "Accept-Language": "en-US,en;q=0.5"
                                   })
        except Exception as e:
            print(e)
            raise
        return response.text

    @staticmethod
    def search(query):
        try:
            html = GoogleSearch._request(GoogleSearch.SEARCH_URL,
                                         {"q": query})
            soup = BeautifulSoup(html, "html.parser")
            if GoogleSearch.RATE_LIMITED in soup.text:
                raise RateLimitedError("Google banned IP address")
        except RateLimitedError as e:
            raise

        urls = []
        for url in soup.find_all("a"):
            try:
                url = url["href"]
                if "google" in url:
                    continue
                if url.startswith("http"):
                    urls.append(url)
            except:
                continue

        return urls


if __name__ == "__main__":
    query = "lovecraft audio drama"
    google = GoogleSearch()
    print("Searching: \"" + query + "\"...")
    for url in google.search(query):
        print(url)
