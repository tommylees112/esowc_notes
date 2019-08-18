# text_similarity.py
import string
import difflib

def remove_punctuation(text: str):
    trans = str.maketrans('', '', string.punctuation)
    return text.lower().translate(trans)

def compute_similarity(str1: str, str2: str):
    similarity_measure = difflib.SequenceMatcher(
        isjunk=NoneNone, a=str1, b=str2, autojunk=False
    ).ratio()

    return similarity_measure
