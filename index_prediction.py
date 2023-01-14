import keras.models as models
import tensorflow_text
import tensorflow_hub as hub
import json
import constants
import tg_fetch_posts
import data_preprocessing

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


for channel_link in constants.PROUKRAINIAN_CHANNELS:
    data, channel_id = tg_fetch_posts.get_posts(channel_link)
    for index in range(len(data)):
        last_publication_date = data[index].get('date')
        text = data_preprocessing.text_to_word_list(data[index].get('message'))
        print(predict(sentenses=text), channel_id)

        # create df from id, username indendical to fetch_stats one
        #create df from id, index, text with the columns as postgres columns names
        #db_connection.connect(df_stats, "ChannelStatistics") but for channels and for index with the second arg of connect() as table name
