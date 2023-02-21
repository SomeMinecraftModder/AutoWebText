from random import shuffle
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib.parse
from urllib.parse import urlparse
from tqdm import tqdm
import re
import logging


def parse_url(url: str):
    data = requests.get(url)
    if "text/html" not in data.headers["content-type"]:
        raise ValueError
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


def clean_text(text: str):
    for letter in [".", "?", "!"]:
        text = text.replace(f"{letter}", f"{letter}\n")
    text = re.sub(' +', ' ', text)
    return text


def text_from_soup(soup):
    texts = soup.findAll(string=True)
    visible_texts = filter(tag_visible, texts)
    text = " ".join(t.strip() for t in visible_texts)
    return clean_text(text)


def explore(starting_url: str, n: int, n_urls: int = 5, url_pool: list = None, write_to_file: bool = False,
            verbose: bool = False):
    if url_pool is None:
        url_pool = [starting_url]
    text = ""
    for _ in tqdm(range(n)):
        possible_urls = []
        for url in tqdm(url_pool, leave=False):
            try:
                soup = parse_url(url)
            except Exception as e:
                logging.warning(f"Fake url found: {e}")
                continue
            if write_to_file:
                with open("data.txt", mode="a", encoding="utf-8") as f:
                    f.write(text_from_soup(soup) + "<|end|>")
            else:
                text += text_from_soup(soup) + "<|end|>"
            possible_url = get_all_link(soup, url)
            possible_urls += possible_url
        if not possible_urls:
            logging.warning("Ran out of url, restarting with base url")
            possible_urls = [starting_url]
        shuffle(possible_urls)
        url_pool = possible_urls[0:n_urls]
        if verbose:
            print(url_pool)
    return text


a = explore("https://fr.wikipedia.org/wiki/Sp%C3%A9cial:Page_au_hasard  ", 5000, n_urls=15,
            write_to_file=True, verbose=True)
print(a)
