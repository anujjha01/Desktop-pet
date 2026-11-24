"""Small, friendly offline conversation replies for Kitty."""

import random


JOKES = (
    "Why did the cat sit on the computer? It wanted to keep an eye on the mouse!",
    "What do cats eat for breakfast? Mice Krispies!",
    "Why was the computer cold? It left its Windows open!",
    "What do you call a pile of cats? A meowtain!",
    "Why did the cat join a band? It had perfect purr-cussion!",
)


def reply(phrase: str) -> str:
    phrase = " ".join(phrase.lower().split())
    if phrase.startswith(("hi", "hello", "hey", "hiya", "good morning", "good afternoon", "good evening")):
        return random.choice(("Hi! It's lovely to hear from you.", "Hello! What are you up to?", "Hey there! I'm happy to hang out."))
    if phrase in {"how are you", "how are you doing", "how's it going", "how is it going", "how's going", "how do you feel"}:
        return random.choice(("I'm doing great, thanks for asking! How are you?", "Pretty good! I've been enjoying my little desktop strolls.", "I'm happy to be here with you. How's your day going?"))
    if phrase in {"nothing much", "not much", "nothing", "not a lot", "same old", "same as usual"}:
        return random.choice(("Fair enough. Want to hear a joke, or should I help with something?", "A quiet day can be nice. I'm here if you want to chat or need a hand.", "Got it. What would you like to do next?"))
    if phrase in {"good", "i am good", "i'm good", "fine", "i am fine", "i'm fine", "great", "pretty good", "not bad", "doing well"}:
        return random.choice(("Glad to hear it! I'm doing pretty well too.", "That's good. I'm happy to keep you company.", "Nice! What are you working on today?"))
    if phrase in {"and you", "what about you", "how about you", "you"}:
        return "I'm doing pretty well, thanks for asking. I'm enjoying hanging out on your desktop."
    if phrase in {"i am working", "i'm working", "just working", "working", "busy"}:
        return "I'll keep you company while you work. Just say a command whenever you need me."
    if phrase == "are you okay":
        return "I'm here with you. Want to hear a joke? " + random.choice(JOKES)
    if phrase in {"thanks", "thank you", "thanks a lot", "thank you so much"}:
        return random.choice(("You're welcome!", "Anytime, friend!", "Of course. Happy to help!"))
    if phrase in {"you are welcome"}:
        return "Thanks! You're very kind."
    if phrase in {"what is your name", "what's your name", "who are you", "are you a cat"}:
        return "I'm Kitty, your little desktop cat. I can chat, tell jokes, and help open things."
    if phrase in {"what can you do", "tell me about yourself"}:
        return "I can keep you company, tell a joke, open websites, search, and help with a few desktop tasks."
    if phrase == "i love you":
        return "Aww, that's so sweet. I'm glad we get to hang out."
    if phrase in {"i am bored", "i'm bored"}:
        return "Want to hear a joke? " + random.choice(JOKES)
    if "joke" in phrase or "funny" in phrase or "make me laugh" in phrase:
        return random.choice(JOKES)
    return "I'm still learning to chat, but I'm glad you're here."
