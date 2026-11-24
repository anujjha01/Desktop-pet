"""Wake words and a fixed list of spoken commands."""

import re
from difflib import SequenceMatcher
from dataclasses import dataclass

WAKE_RE = re.compile(r"\b(kitty|sweety|sweetie|sweaty|kity|kitten|pretty|computer|gate|getty)\b")
LEADING_WAKE_RE = re.compile(
    r"^(?:(?:hey|ok|okay|hi|hello)\s+)?(?:kitty|sweety|sweetie|sweaty|kity|kitten|getty|gate|kidding|pretty|computer)\b\s*"
)
POLITE_RE = re.compile(r"^(?:please|can you|could you|would you|will you)\s+")

RULES = (
    ("chat", re.compile(r"^(?:hi|hello|hey|hiya|good morning|good afternoon|good evening)(?: there)?$")),
    ("chat", re.compile(r"^(?:how are you|how are you doing|how's it going|how is it going|how's going|are you okay|how do you feel)$")),
    ("chat", re.compile(r"^(?:thanks|thank you|thanks a lot|thank you so much|you are welcome)$")),
    ("chat", re.compile(r"^(?:what is your name|what's your name|who are you|are you a cat)$")),
    ("chat", re.compile(r"^(?:what can you do|tell me about yourself|i love you)$")),
    ("chat", re.compile(r"^(?:tell me|give me|say) (?:some )?(?:jokes?|funny things|something funny)(?: kind of things)?$")),
    ("chat", re.compile(r"^(?:tell|give|say) me a joke$|^make me laugh$|^jokes?$")),
    ("chat", re.compile(r"^(?:i am|i'm) bored$")),
    ("note_read", re.compile(r"^(?:read|show|list) (?:my )?notes?$|^what did i ask you to remember$")),
    ("note_add", re.compile(r"^(?:take a note|make a note|note|remember) (.+)$")),
    ("edge_search", re.compile(r"^(?:search|look up) (?:on )?edge (?:for )?(.+)$")),
    ("edge_search", re.compile(r"^edge search (?:for )?(.+)$")),
    ("edge_search", re.compile(r"^(?:search|look up) (.+) on edge$")),
    ("edge_search", re.compile(r"^(?:search|look up) (.+) in edge$")),
    ("edge_search", re.compile(r"^open edge and search (?:for )?(.+)$")),
    ("time", re.compile(r"^(?:what(?:'s| is) the time|what time is it|tell me the time|current time)$")),
    ("date", re.compile(r"^(?:what is|what's|tell me) (?:the )?(?:date|day|date today|day today|today's date)$|^(?:what day is it(?: today)?|what's today's date|what is today's date|today's date)$")),
    ("calculate", re.compile(r"^(?:calculate|compute|what is|what's) (.+)$")),
    ("facebook_search", re.compile(r"^(?:search|find|look up) (?:on |in )?facebook (?:for )?(.+)$")),
    ("facebook_search", re.compile(r"^(?:search|find|look up) (?:for )?(.+) on facebook$")),
    ("facebook_search", re.compile(r"^facebook (?:search )?(?:for )?(.+)$")),
    (
        "top",
        re.compile(
            r"^(?:show |open )?(?:me )?(?:the )?(?:top|latest|trending) "
            r"(?:post|posts|video|videos|feed) (?:on |in |from )?"
            r"(youtube|linkedin|instagram|twitter|facebook|x)$"
        ),
    ),
    ("top", re.compile(r"^what(?:'s| is) trending on (youtube|linkedin|instagram|twitter|facebook|x)$")),
    ("youtube_search", re.compile(r"^play (.+) on youtube$")),
    (
        "youtube_search",
        re.compile(r"^(?:search|play|find|look up) (?:on |in )?youtube (?:for )?(.+)$"),
    ),
    ("youtube_search", re.compile(r"^youtube (?:search )?(?:for )?(.+)$")),
    ("linkedin_search", re.compile(r"^search (?:on |in )?linkedin (?:for )?(.+)$")),
    ("linkedin_search", re.compile(r"^linkedin search (?:for )?(.+)$")),
    ("google", re.compile(r"^search (.+) on google$")),
    ("google", re.compile(r"^(?:search|google) (?:on )?google (?:for )?(.+)$")),
    ("google", re.compile(r"^google (?:search )?(?:for )?(.+)$")),
    ("google", re.compile(r"^(?:search|look up|find) (?:for )?(.+)$")),
    (
        "chatgpt",
        re.compile(r"^(?:ask |open |talk to )?(?:chat gpt|chatgpt|gpt)(?: about| for)? (.+)$"),
    ),
    (
        "open_site",
        re.compile(
            r"^(?:open|go to|launch) (?:a |the )?(youtube|google|linkedin|instagram|facebook|twitter|x|chatgpt|chat gpt|gpt)$"
        ),
    ),
    (
        "open_app",
        re.compile(
            r"^(?:open|launch) (notepad|calculator|calc|file explorer|explorer|chrome|microsoft edge|edge)$"
        ),
    ),
    ("open_folder", re.compile(r"^open (?:the )?(?:folder|directory) (.+)$")),
    ("open_folder", re.compile(r"^open (?:the )?(.+?)(?: folder| directory)$")),
    ("open_folder", re.compile(r"^open (?:my )?(?:the )?(desktop|downloads|documents|pictures|music|videos|this pc|computer|[cde] drive)(?: folder)?$")),
    ("open_app_any", re.compile(r"^open app (.+)$")),
    ("open_item", re.compile(r"^open (.+)$")),
)


@dataclass(frozen=True)
class Command:
    name: str
    arg: str = ""


def normalize(text):
    cleaned = text.lower().replace("\u2019", "'")
    cleaned = re.sub(r"[^a-z0-9' ]+", " ", cleaned)
    cleaned = re.sub(r"\bsweet(?: tea| the)\b", "sweetie", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def has_wake(text):
    phrase = normalize(text)
    if WAKE_RE.search(phrase):
        return True
    # The small offline model often hears the short wake word as "getty" or
    # "kidding". Accept close single-word phonetic variants at utterance start.
    words = phrase.split()
    if words and words[0] in {"getty", "gate", "kidding", "kittycat", "kity", "pretty", "computer"}:
        return True
    return bool(words and SequenceMatcher(None, words[0], "kitty").ratio() >= 0.80)


def strip_leading_wake(text):
    phrase = normalize(text)
    stripped = LEADING_WAKE_RE.sub("", phrase, count=1).strip()
    if stripped != phrase:
        return stripped
    words = phrase.split(maxsplit=1)
    if words and has_wake(words[0]):
        return words[1] if len(words) > 1 else ""
    return phrase


def prepare(text, armed):
    """Return the command phrase, or None when this utterance should be ignored.

    An empty string means the wake word arrived without a command yet.
    """
    phrase = normalize(text)
    if not phrase:
        return None
    if not armed:
        if not has_wake(phrase):
            return None
        return strip_leading_wake(phrase)
    return strip_leading_wake(phrase)


def parse(text):
    phrase = normalize(text)
    if re.fullmatch(r"(?:hi|hello|hey) (?:kitty|sweety|sweetie|computer)", phrase):
        return Command("chat", phrase)
    # Also accept an exact command spoken without the wake word, and remove
    # common wake-word substitutions when they are present in the transcript.
    phrase = strip_leading_wake(phrase)
    phrase = POLITE_RE.sub("", phrase).strip()
    if not phrase:
        return None
    # Common Vosk substitutions observed in kitty.log for command phrases.
    phrase = re.sub(r"\bopn\b", "open", phrase)
    phrase = re.sub(r"^(?:head|he|hey)\s+(?=open\b)", "", phrase)
    phrase = re.sub(r"\b(?:a|the|he|be|we|head)\s+(?=open\b)", "", phrase)
    phrase = re.sub(r"\b(?:you do|you tube|you duke|you too|you to)\b", "youtube", phrase)
    phrase = re.sub(r"\bvs good\b", "youtube", phrase)
    phrase = re.sub(r"\bnew deal\b", "edge", phrase)
    phrase = re.sub(r"\byour deal\b", "edge", phrase)
    phrase = re.sub(r"\bthe crowd\b", "chrome", phrase)
    phrase = re.sub(r"\b(?:microsoft edge|microsoft edged)\b", "edge", phrase)
    for name, pattern in RULES:
        match = pattern.match(phrase)
        if not match:
            continue
        arg = match.group(1).strip() if match.groups() else ""
        if name == "chat":
            arg = phrase
        if name == "open_folder":
            arg = re.sub(r"\s+on (?:my )?desktop$", "", arg).strip()
        if name == "open_site":
            arg = {"chat gpt": "chatgpt", "gpt": "chatgpt"}.get(arg, arg)
        if name == "open_app":
            arg = {
                "calc": "calculator",
                "explorer": "file explorer",
                "microsoft edge": "edge",
            }.get(arg, arg)
        if name == "top":
            arg = "twitter" if arg == "x" else arg
        return Command(name, arg)
    return None
