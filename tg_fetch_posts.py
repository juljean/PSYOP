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


async def fetch_posts(channels_link,total_count_limit=100):
    await constants.client.start()
    print("Client Created")
    # Ensure you're authorized
    if not await constants.client.is_user_authorized():
        await constants.client.send_code_request(constants.phone)
        try:
            await constants.client.sign_in(constants.phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await constants.client.sign_in(password=input('Password: '))

    # user_input_channel = input('enter entity(telegram URL or entity id):')
    user_input_channel = channels_link
    if user_input_channel.isdigit():
        entity = PeerChannel(int(user_input_channel))
    else:
        entity = user_input_channel

    my_channel = await constants.client.get_entity(entity)

    offset_id = 0
    limit = 100
    all_messages = []
    total_messages = 0
    # Limit of posts to fetch
    # total_count_limit = 100

    while True:
        print("Current Offset ID is:", offset_id, "; Total Messages:", total_messages)
        history = await constants.client(GetHistoryRequest(
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


def get_posts(channel_link, total_count_limit=100):
    with constants.client:
        posts, channel_id, username = constants.client.loop.run_until_complete(fetch_posts(channel_link,total_count_limit))
        return posts, channel_id, username