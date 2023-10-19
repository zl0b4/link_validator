import time

import bs4.builder
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry



all_urls = {}
ready = set()


def get_request(url):
    '''
    Возвращает результат запроса к URL веб-страницы.
    Если не удается открыть web-страницу из-за исключения requests.exceptions.ConnectionError,
    то возвращает None

            Parameters:
                    url (str): url web-страницы

            Returns:
                    reqs (session): web-страница
        '''
    try:
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('https://', adapter)
        session.mount('http://', adapter)
        reqs = session.get(url)
        return reqs
    except requests.exceptions.ConnectionError:
        print(f"Exception with URL: {url}")

def get_links(url):
    '''
    Возвращает множества всех ссылок с web-страницы.

            Parameters:
                    url (str): url web-страницы

            Returns:
                    urls (set): Множество, состоящее из всех ссылок, находящихся на web-странице
    '''
    reqs = get_request(url)
    if reqs is None:
        return set()
    try:
        soup = BeautifulSoup(reqs.text, 'html.parser')
        urls = [link.get('href') for link in soup.find_all('a')]
        urls = list(filter(lambda u: u and len(u) >= 2 and '/' in u, urls))
        for i, link in enumerate(urls):
            if '://' not in link:
                urls[i] = ('https://www.magtu.ru/' + link).replace('www.magtu.ru//', 'www.magtu.ru/')
        urls = set(filter(lambda u: 'magtu.ru' in u, urls))
        return urls
    except bs4.builder.ParserRejectedMarkup:
        return set()


def get_links_from_magtu_link(url):
    '''
    Возвращает множества всех ссылок с web-страницы МГТУ. Выполняется проверка,
    является ли данная web-страница

            Parameters:
                    url (str): url web-страницы МГТУ

            Returns:
                    urls (set): Множество, состоящее из всех ссылок, находящихся на web-странице
        '''

    # проверка, что это web-страница сайта МГТУ
    if 'magtu.ru' not in url:
        return
    values = set()
    for value in all_urls.values():
        values |= value
    return get_links(url).difference(set(all_urls.keys()) | values)


def get(url):
    '''
    Рекурсивная функция.
    Дополняет словарь all_urls всеми полученными URL со всех вложенных web-страниц данной

            Parameters:
                    url (str): url web-страницы

            Returns:
                    None
        '''
    global all_urls
    if url not in ready:
        print(f"URL: {url}")
        result.write(f"URL: {url}\n")
        urls = get_links_from_magtu_link(url)
        not_validated = validate_links(urls)
        if not_validated:
            print(f"Not validated on {url}:")
            print(*not_validated, sep='\n')
            for s in not_validated:
                result.write(f"{s}\n")
            result.write("\n")
            print()
        else:
            print(f"URL: {url}. All links are validated!")
        ready.add(url)

        if url not in all_urls:
            all_urls[url] = urls
        else:
            all_urls[url] |= urls

        if urls:
            for link in urls:
                if 'https://www.magtu.ru' not in link:
                    continue
                get(link)


def validate_links(urls):
    not_validated = []
    for link in urls:
        #  print(link)
        r = get_request(link)
        if r is None:
            result.write(f"{link} can't connect!\n")
            print(f"{link} can't connect!")
            continue

        if r.status_code == 404:
            print(f"{link} is not validated")
            not_validated.append(link)

        # time.sleep(1)
    return not_validated

start_time = time.time()

result = open('result.txt', 'a')

link = 'https://www.magtu.ru/'

get(link)

result.write("--- %s seconds ---" % (time.time() - start_time))

result.close()
print(all_urls)
#validate_links(["http://magtu.ru/weblinks?task=weblink.go&id=48"])
print("--- %s seconds ---" % (time.time() - start_time))
print()
