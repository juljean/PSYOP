import index_prediction
import time
import db_connection


def query_handler():
    fetched_data = db_connection.connect(operation_name="select")
    if fetched_data:
        # Sort the resultative dictionary by priority
        fetched_data = sorted(fetched_data.items(), key=lambda x:x[1], reverse=True)
        # data format [('https://t.me/dvachannel', 0)]
        for item in fetched_data:
            index_prediction.get_indexes(item[0])
            db_connection.connect(channel_link=item[0], operation_name="delete" )
    else:
        time.sleep(60)
    query_handler()


query_handler()