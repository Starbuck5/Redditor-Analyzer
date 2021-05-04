import string

# UI module constants
INPUT_DIGITS = set([str(i) for i in range(10)])
INPUT_LETTERS = set(string.ascii_letters)
INPUT_PUNCTUATION = set(string.punctuation)
INPUT_DEFAULT = INPUT_DIGITS | INPUT_LETTERS | INPUT_PUNCTUATION | set(" ")
INPUT_SPECIALS = set(["\b", "\t", "\r", "\n"])
