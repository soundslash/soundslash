
import re
from unidecode import unidecode

def transliterate(string):
    # remove accents
    string = unidecode(string)
    # remove multiple whitespaces
    string = ' '.join(string.split())
    # remove special characters
    string = re.sub('[^A-Za-z0-9\s]+', '', string)
    # replace whitespace with comma
    string = string.replace(' ', '-')
    return string