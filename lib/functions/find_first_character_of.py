import re

def findFirstCharacterOf(instring, *substrings):
    pat = re.compile("|".join([re.escape(s) for s in substrings]))
    match = pat.search(instring)
    if match is None:
        return -1
    else:
        return match.start()