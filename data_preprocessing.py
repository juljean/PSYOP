import logging
from re import sub
import emot
import constants
import os
import json

directory = 'ChannelsIds'
# Creating basic objects
logging.basicConfig(format="%(levelname)s - %(asctime)s: %(message)s", datefmt='%H:%M:%S', level=logging.INFO)
# Label = 0 -> Prorussian; label = 1-> Proukrainian
labeled_data = {}

stats = {}

def text_to_word_list(text):
    """
    Preprocessing steps:
    - Lowercase text
    - Drop numbers
    - Verbalize emojis
    - Verbalize '+'
    - Drop words with length<2
    :param text:
    :return:
    """
    text = str(text)
    text = text.lower()
    # Clean the text
    text = sub(r"[^Яа-яЁё^_+]", " ", text)
    text = sub(r"\+", " плюс ", text)
    text = sub(r"\s{2,}", " ", text)
    text = text.split()
    text_without_stopwords = []
    for word in text:
        # word = stemmer.stemWord(word)
        if word not in constants.STOP_WORDS_RU:
            text_without_stopwords.append(word)
    return ' '.join(text_without_stopwords)


for filename in constants.PRORUSSIAN_CHANNELS:
    f = os.path.join(directory, filename)
    # checking if it is a file
    if os.path.isfile(f):
        if filename in constants.PRORUSSIAN_CHANNELS_IDS:
            label = 0
        else:
            label = 1
        f = open(f, encoding="utf-8")
        data = json.load(f)
        for index in range(len(data)):
            text = text_to_word_list(data[index].get('message'))
            if text:
                labeled_data[text] = label
                stats[text] = [data[index].get('views'), data[index].get('forwards'), data[index]['reactions']]

# with open("labeled_data_small.json", "w", encoding="utf-8") as outfile:
#     json.dump(labeled_data, outfile, ensure_ascii=False)
#
#
# with open("stats_small.json", "w", encoding="utf-8") as outfile:
#     json.dump(stats, outfile, ensure_ascii=False)