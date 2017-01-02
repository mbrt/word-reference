#!/usr/bin/env python3

import requests
import sys
from lxml.html import fromstring


BASE_URL = 'http://www.urbandictionary.com/define.php?term='


def get(url):
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception('cannot get url {}, status code {}'.format(url, r.status_code))
    return r.text


def parse(contents):
    doc = fromstring(contents)
    meanings = doc.findall('.//div[@class="meaning"]')
    word = doc.find('.//div[@class="def-header"]/a[@class="word"]')
    return (word, meanings)


def dump_def(tag):
    for t in tag.itertext():
        print(t)


def main(word):
    url = BASE_URL + word
    wrd, meanings = parse(get(url))
    if wrd is None or meanings is None or len(meanings) == 0:
        print('Word "{}" not found'.format(word))
        return 1
    print('Definition for {}'.format(wrd.text_content()))
    dump_def(meanings[0])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
