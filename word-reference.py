#!/usr/bin/env python3

# Example of page contents:
#
# <div>
#   <audio id='aud0' preload='none'><source src='/audio/en/us/us/en095937.mp3'
#                                           type='audio/mpeg'></audio>
#   <audio id='aud1' preload='none'><source src='/audio/en/uk/general/en095937.mp3'
#                                           type='audio/mpeg'></audio>
#   <audio id='aud2' preload='none'><source src='/audio/en/uk/rp/en095937.mp3'
#                                           type='audio/mpeg'></audio>
#   <audio id='aud3' preload='none'><source src='/audio/en/uk/Yorkshire/en095937-55.mp3'
#                                           type='audio/mpeg'></audio>
#   <audio id='aud4' preload='none'><source src='/audio/en/Irish/en095937.mp3'
#                                           type='audio/mpeg'></audio>
#   <audio id='aud5' preload='none'><source src='/audio/en/scot/en095937.mp3'
#                                           type='audio/mpeg'></audio>
#   <audio id='aud6' preload='none'><source src='/audio/en/us/south/en095937.mp3'
#                                           type='audio/mpeg'></audio>
#   <audio id='aud7' preload='none'><source src='/audio/en/Jamaica/en095937.mp3'
#                                           type='audio/mpeg'></audio>
# </div>
# <div>
#   <select id='accentSelection'>
#     <option title='USA-Neutral pronunciation' value='0' >US</option>
#     <option title='Southern UK' value='1' >UK</option>
#     <option title='Received Pronunciation (BBC English)' value='2'
#             selected='selected'>UK-RP</option>
#     <option title='Uk Yorkshire' value='3' >UK-Yorkshire</option>
#     <option title='Irish Pronunciation' value='4' >Irish</option>
#     <option title='Scottish Pronunciation' value='5' >Scottish</option>
#     <option title='US-Southern pronunciation' value='6' >US Southern</option>
#     <option title='Jamaican pronunciation' value='7' >Jamaican</option>
#   </select>
# </div>

import sys
import requests
from html.parser import HTMLParser


DEF_BASE_URL = "http://www.wordreference.com/definition/"
AUDIO_BASE_URL = "http://www.wordreference.com"
ACCENTS = ["US", "UK-RP", "UK"]


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parsed = Parsed()
        self.state = SearchState(self.parsed)

    def handle_starttag(self, tag, attrs):
        self.state = self.state.on_tag(tag, attrs)

    def handle_endtag(self, tag):
        self.state = self.state.on_tag_end(tag)

    def handle_data(self, data):
        self.state = self.state.on_data(data)


class Parsed(object):
    def __init__(self):
        self.audios = {}
        self.accent_vals = {}

    def url_for_accent(self, accent):
        if accent not in self.accent_vals:
            return None
        path = self.audios.get("aud" + self.accent_vals[accent])
        if path is None:
            return None
        return AUDIO_BASE_URL + path


class State(object):
    def on_tag(self, tag, attrs):
        return self

    def on_tag_end(self, tag):
        return self

    def on_data(self, data):
        return self


class SearchState(State):
    def __init__(self, parsed):
        self.parsed = parsed

    def on_tag(self, tag, attrs):
        if tag == "audio":
            return AudioState(self.parsed, find_attr(attrs, "id"))
        elif tag == "select" and find_attr(attrs, "id") == "accentSelection":
            return AccentState(self.parsed)
        return self


class AudioState(State):
    def __init__(self, parsed, id):
        self.parsed = parsed
        self.id = id

    def on_tag(self, tag, attrs):
        if tag == "source":
            self.parsed.audios[self.id] = find_attr(attrs, "src")
        return self

    def on_tag_end(self, tag):
        if tag == "audio":
            return SearchState(self.parsed)
        return self


class AccentState(State):
    def __init__(self, parsed):
        self.parsed = parsed
        self.in_option = True

    def on_tag(self, tag, attrs):
        if tag == "option":
            self.in_option = True
            self.value = find_attr(attrs, "value")
        return self

    def on_tag_end(self, tag):
        self.in_option = False
        if tag == "select":
            return SearchState(self.parsed)
        return self

    def on_data(self, data):
        if self.in_option:
            self.parsed.accent_vals[data] = self.value
        return self


def find_attr(attrs, name):
    for a in attrs:
        if a[0] == name:
            return a[1]
    return None


def handle(word):
    r = requests.get(DEF_BASE_URL + word)
    if r.status_code != 200:
        raise Exception("Word '{}' not found in word reference".format(word))
    parser = Parser()
    parser.feed(r.text)
    for accent in ACCENTS:
        if accent in parser.parsed.accent_vals:
            url = parser.parsed.url_for_accent(accent)
            print("Found audio for accent {}: {}".format(accent, url))


def main():
    handle(sys.argv[1])


if __name__ == "__main__":
    main()
