import keras.models as models
import tensorflow_text
import tensorflow_hub as hub
import json
import constants
import tg_fetch_posts
import data_preprocessing
import pandas as pd
import db_connection

model = models.load_model(constants.MODEL_NAME)

bert_encoder = hub.KerasLayer(constants.MODEL_LINK)
def get_sentence_embeding(sentences):
    # preprocessed_text = bert_preprocess(sentences)
    preprocessed_text = sentences
    return bert_encoder(preprocessed_text)


def predict(sentenses):
    values = get_sentence_embeding(sentenses)
    predicted_values = model(values)
    return float(sum(predicted_values)/len(sentenses)*2-1)


def get_indexes():
    channel_link = 'https://t.me/stremPunisher'
    data, channel_id, username = tg_fetch_posts.get_posts(channel_link)
    last_publication_date = data[-1].get('date')
    coefficient = 0
    # create smart coefficient
    for index in range(len(data)):
        text = data_preprocessing.text_to_word_list(data[index].get('message'))
        coefficient = predict(sentenses=text)
    data_to_push = {'calculated_coefficient': [coefficient], 'id_channel': [channel_id],
                     'last_publication_date': [last_publication_date]}

    df_stats = pd.DataFrame.from_dict(data_to_push)
    df_channel = pd.DataFrame.from_dict({'id_channel': [channel_id], 'channel_name': [username]})
    # db_connection.connect(df_channel, "Channel")
    # db_connection.connect(df_stats, "ProrussianCoefficient")

get_indexes()