import keras.models as models
import tensorflow_text
import tensorflow_hub as hub
import json
import constants
import tg_fetch_posts
import data_preprocessing
import pandas as pd
import db_connection
import tg_fetch_stats

model = models.load_model(constants.MODEL_NAME)

bert_encoder = hub.KerasLayer(constants.MODEL_LINK)
def get_sentence_embeding(sentences):
    # preprocessed_text = bert_preprocess(sentences)
    preprocessed_text = sentences
    return bert_encoder(preprocessed_text)


def predict(sentenses):
    values = get_sentence_embeding(sentenses)
    predicted_values = model(values)
    coef = float(sum(predicted_values)/len(sentenses)*2-1)
    return max(min(coef,1),-1)



def get_indexes(channel_link, total_count_limit=300):
    data, channel_id, username = tg_fetch_posts.get_posts(channel_link,total_count_limit)
    last_publication_date = data[-1].get('date')
    sentences = []
    # create smart coefficient
    for index in range(len(data)):
        text = data_preprocessing.text_to_word_for_model(data[index].get('message'))
        if text:
            sentences.extend(text)
    print(len(sentences))
    print(total_count_limit)
    if len(sentences) > 600 or total_count_limit > 1500:
        coefficient = predict(sentenses=sentences)
        print(coefficient)
        data_to_push = {'calculated_coefficient': [coefficient], 'id_channel': [channel_id],
                         'last_publication_date': [last_publication_date]}

        df_stats = pd.DataFrame.from_dict(data_to_push)
        df_channel = pd.DataFrame.from_dict({'id_channel': [channel_id], 'channel_name': [username]})
        db_connection.connect(df_channel, "Channel", operation_name="insert")
        db_connection.connect(df_stats, "ProrussianCoefficient", operation_name="insert")
        tg_fetch_stats.insert_stats(channel_link)
    else:
        get_indexes(channel_link, total_count_limit=total_count_limit + 500)

for link in constants.VAGUE_CHANNELS:
    get_indexes(link)
    print(link)
