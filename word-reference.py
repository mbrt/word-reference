#!/usr/bin/env python3

import sys
import requests
from html.parser import HTMLParser


BASE_URL = "http://www.wordreference.com/enit/"
ACCENTS = ["US", "UK", "UK-RP"]


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.state = []
        self.state_data = []
        self.audios = {}
        self.accent_vals = {}

    def handle_starttag(self, tag, attrs):
        if tag == "audio":
            self._set_state("audio", find_attr(attrs, "id"))
        elif tag == "source" and self._is_state("audio"):
            self.audios[self._state_data()] = find_attr(attrs, "src")
        elif tag == "select" and find_attr(attrs, "id") == "accentSelection":
            self._set_state("accent")
        elif tag == "option" and self._is_state("accent"):
            self._set_state("accent-data", find_attr(attrs, "value"))
            print("{}".format(attrs))

    def handle_endtag(self, tag):
        if tag in ["audio", "accent", "accent-data"]:
            self.state.pop()
            self.state_data.pop()

    def handle_data(self, data):
        if self._is_state("accent-data"):
            self._handle_accent(data, self._state_data())

    def _is_state(self, expected):
        return len(self.state) and self.state[-1] == expected

    def _set_state(self, state, data=None):
        print("set state {} to {}".format(state, data))
        self.state.append(state)
        self.state_data.append(data)

    def _state_data(self):
        print("get state {} data {}".format(self.state[-1],
                                            self.state_data[-1]))
        print("overall state {} and data {}".format(self.state,
                                                    self.state_data))
        self.state_data[-1]

    def _handle_accent(self, name, val):
        # print("{}, {}".format(name, val))
        if name in ACCENTS:
            self.accent_vals[name] = val


def find_attr(attrs, name):
    for a in attrs:
        if a[0] == name:
            return a[1]
    return None


def handle(word):
    r = requests.get(BASE_URL + word)
    if r.status_code != 200:
        raise Exception("Word '{}' not found in word reference".format(word))
    parser = Parser()
    parser.feed(r.text)
    print(parser.audios)
    print(parser.accent_vals)


def main():
    handle(sys.argv[1])


if __name__ == "__main__":
    main()
