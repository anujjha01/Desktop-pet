"""Open the default browser to search and social pages."""

import subprocess
import webbrowser
from urllib.parse import quote_plus

CREATE_NO_WINDOW = 0x08000000

SITES = {
    "youtube": "https://www.youtube.com/",
    "google": "https://www.google.com/",
    "linkedin": "https://www.linkedin.com/feed/",
    "instagram": "https://www.instagram.com/",
    "facebook": "https://www.facebook.com/",
    "twitter": "https://x.com/",
    "x": "https://x.com/explore",
    "chatgpt": "https://chatgpt.com/",
}

TOP = {
    "youtube": "https://www.youtube.com/feed/trending",
    "linkedin": "https://www.linkedin.com/feed/",
    "instagram": "https://www.instagram.com/",
    "facebook": "https://www.facebook.com/",
    "twitter": "https://x.com/explore",
    "x": "https://x.com/explore",
}

NAMES = {
    "youtube": "YouTube",
    "google": "Google",
    "linkedin": "LinkedIn",
    "instagram": "Instagram",
    "facebook": "Facebook",
    "twitter": "X",
    "x": "X",
    "chatgpt": "ChatGPT",
}


def open_url(url):
    webbrowser.open(url, new=2)


def google(query):
    open_url("https://www.google.com/search?q=" + quote_plus(query))


def youtube(query):
    open_url("https://www.youtube.com/results?search_query=" + quote_plus(query))


def edge_search(query):
    from actions import apps

    url = "https://www.bing.com/search?q=" + quote_plus(query)
    apps.open_app("edge", url)


def linkedin(query):
    open_url("https://www.linkedin.com/search/results/all/?keywords=" + quote_plus(query))


def facebook_search(query):
    open_url("https://www.facebook.com/search/people/?q=" + quote_plus(query))


def site(name):
    open_url(SITES[name])


def top(name):
    open_url(TOP[name])


def copy_text(text):
    subprocess.run(
        ["clip"],
        input=text,
        text=True,
        check=False,
        creationflags=CREATE_NO_WINDOW,
    )


def display_name(name):
    return NAMES.get(name, name)
