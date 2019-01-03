import random

USER_AGENTS = [
    ('Mozilla/5.0 (X11; Linux x86_64) '
     'AppleWebKit/537.36 (KHTML, like Gecko) '
     'Chrome/57.0.2987.110 '
     'Safari/537.36'),  # chrome
    ('Mozilla/5.0 (X11; Linux x86_64) '
     'AppleWebKit/537.36 (KHTML, like Gecko) '
     'Chrome/61.0.3163.79 '
     'Safari/537.36'),  # chrome
    ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) '
     'Gecko/20100101 '
     'Firefox/55.0'),  # firefox
    ('Mozilla/5.0 (X11; Linux x86_64) '
     'AppleWebKit/537.36 (KHTML, like Gecko) '
     'Chrome/61.0.3163.91 '
     'Safari/537.36'),  # chrome
    ('Mozilla/5.0 (X11; Linux x86_64) '
     'AppleWebKit/537.36 (KHTML, like Gecko) '
     'Chrome/62.0.3202.89 '
     'Safari/537.36'),  # chrome
    ('Mozilla/5.0 (X11; Linux x86_64) '
     'AppleWebKit/537.36 (KHTML, like Gecko) '
     'Chrome/63.0.3239.108 '
     'Safari/537.36'),  # chrome
    ("Mozilla/5.0 (Windows NT 6.1; WOW64) "
     "AppleWebKit/537.36 (KHTML, like Gecko) "
     "Chrome/ 58.0.3029.81 Safari/537.36"),
]


def random_user_agent():
    return random.choice(USER_AGENTS)


try:
    import asyncio
    from proxybroker import Broker


    def get_proxies(n=10, types=['HTTP', 'HTTPS']):
        proxy_list = []
        proxies = asyncio.Queue()
        broker = Broker(proxies)

        async def show(proxies):
            while True:
                proxy = await proxies.get()
                if proxy is None:
                    break
                print('Found proxy: %s' % proxy)
                proxy_list.append(proxy.host + ":" + str(proxy.port))

        tasks = asyncio.gather(
            broker.find(types=types, limit=n),
            show(proxies))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(tasks)
        return proxy_list

except ImportError:
    import requests
    from bs4 import BeautifulSoup


    def get_proxies(n=10, types=['HTTP', 'HTTPS']):
        url = 'https://free-proxy-list.net/'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        proxies = set()
        for i in soup.find_all("tr")[1:]:

            if not i.text or not i.text[0].isdigit():
                break
            ip, port = [proxy.text for proxy in i.find_all("td")[:2]]
            proxy = ":".join([ip, port])
            proxies.add(proxy)
        return proxies


    import sys

    if sys.version.startswith("2"):

        try:
            import grey_harvest  # py2 only


            def get_proxies(n=10, types=['HTTP', 'HTTPS']):
                ''' spawn a harvester '''
                harvester = grey_harvest.GreyHarvester()

                ''' harvest some proxies from teh interwebz '''
                count = 0
                proxies = []
                for proxy in harvester.run():
                    proxies.append(proxy)
                    count += 1
                    if count >= n:
                        break
                return proxies

        except ImportError:
            pass
