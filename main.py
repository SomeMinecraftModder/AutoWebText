from random import shuffle
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib.parse
from urllib.parse import urlparse
from tqdm import trange, tqdm


def parse_url(url: str):
    data = requests.get(url)
    data.encoding = data.apparent_encoding  # fix the encoding
    soup = BeautifulSoup(data.text, 'html.parser')
    return soup


def get_all_link(soup: BeautifulSoup, url: str):
    all_link = []
    for link in soup.find_all('a'):
        current_link = link.get("href")
        parsed_url = urlparse(url)
        current_link = urllib.parse.urljoin('{uri.scheme}://{uri.netloc}/'.format(uri=parsed_url), current_link)
        all_link.append(current_link)
    return all_link


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_soup(soup):
    texts = soup.findAll(string=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)


def explore(starting_url: str, n: int, n_urls: int = 5, url_pool: list = None, write_to_file: bool = False):
    if url_pool is None:
        url_pool = [starting_url]
    text = ""
    for _ in tqdm(range(n)):
        for url in tqdm(url_pool, leave=False):
            try:
                soup = parse_url(url)
            except Exception as e:
                print(e)
                continue
            if write_to_file:
                with open("data.txt", mode="a", encoding="utf-8") as f:
                    f.write(text_from_soup(soup) + "<|end|>")
            else:
                text += text_from_soup(soup) + "<|end|>"
            possible_urls = get_all_link(soup, url)
            shuffle(possible_urls)
            possible_urls = possible_urls[0:n_urls]
            url_pool = possible_urls
    return text


a = explore("https://en.wikipedia.org/wiki/Nice", 5000, n_urls=15, write_to_file=True)
print(a)
