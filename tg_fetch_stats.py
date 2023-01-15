import configparser
import json
import asyncio
from datetime import date, datetime
import config
import constants
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.types import (PeerChannel)
import base64
from datetime import datetime
import db_connection
import pandas as pd


class DateTimeEncoder(json.JSONEncoder):
    """
    Parse JSON datetime
    """
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, bytes):
            return list(o)

        return json.JSONEncoder.default(self, o)


# Setting configuration values
api_id = config.API_ID
api_hash = config.API_HASH
phone = config.PHONE
username = config.USERNAME
# Create the client and connect
client = TelegramClient(username, api_id, api_hash)


async def fetch_stats(channel_link):
    """
    Request TG API and get stats by channel_id
    :param channel_link: str
    :return: json with stats
    """
    await client.start()
    print("Client Created")
    # Ensure you're authorized
    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))

    # user_input_channel = input('enter entity(telegram URL or entity id):')
    user_input_channel = channel_link
    if user_input_channel.isdigit():
        entity = PeerChannel(int(user_input_channel))
    else:
        entity = user_input_channel

    my_channel = await client.get_entity(entity)

    offset_id = 0
    limit = 100
    all_messages = []
    # Limit of posts to fetch
    total_count_limit = 10

    while True:
        history = await client(GetHistoryRequest(
            peer=my_channel,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))
        if not history.messages:
            break
        messages = history.messages
        for message in messages:
            all_messages.append(message.to_dict())
        offset_id = messages[len(messages) - 1].id
        total_messages = len(all_messages)
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break
    return all_messages, my_channel.id, my_channel.username


def process_data(json_stats, channel_id, username):
    """
    Calculate total numbers of needed parameters
    :param json_stats: raw json from TG API stats
    :param channel_id: id of the channel by link
    :param username: username of the channel
    """
    views_total_count = 0
    forwards_total_count = 0
    reactions_total_count = {}
    last_publication_date = json_stats[-1].get('date').strftime("%Y-%m-%d")
    for index in range(len(json_stats)):
        if json_stats[index].get('views'):
            views_total_count += int(json_stats[index].get('views'))
        if json_stats[index].get('forwards'):
            forwards_total_count += int(json_stats[index].get('forwards'))
        if json_stats[index].get('reactions'):
            for reaction in json_stats[index]['reactions']['results']:
                key_emoticon = str(reaction['reaction']['emoticon'].encode('unicode-escape').decode('ASCII'))
                emoticon_count = int(reaction['count'])
                if key_emoticon in reactions_total_count.keys():
                    reactions_total_count[key_emoticon] += emoticon_count
                else:
                    reactions_total_count[key_emoticon] = emoticon_count
    stats_to_push = {'id_channel': [channel_id], 'views_total_count': [views_total_count], 'forwards_total_count': [forwards_total_count], 'reactions_total_count': [json.dumps(reactions_total_count)], 'last_publication_date': [last_publication_date]}
    df_stats = pd.DataFrame.from_dict(stats_to_push)
    db_connection.connect(df_stats, "ChannelStatistics")


def insert_stats(channel_link):
    with client:
        # To insert channels data swap constants.PROUKRAINIAN_CHANNELS/constants.PRORUSSIAN_CHANNELS
        # for channel_link in constants.PROUKRAINIAN_CHANNELS:
        stats, channel_id, username = client.loop.run_until_complete(fetch_stats(channel_link))
        process_data(stats, channel_id, username)
