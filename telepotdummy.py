import re
import time

import telepot
from departures import normalize_stopcode, HslRequests
from keys import telegram_api_key, hsl_username, hsl_passcode


def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == u"location":
        location = msg["location"]
        latitude = location["latitude"]
        longitude = location["longitude"]
        reply, stops = hsl.stops_for_location(latitude, longitude)
        bot.sendMessage(chat_id, reply)
    if content_type == u"text":
        print msg
        text = msg["text"]
        m = re.match(r".*\b(\D+)(\d+)", text)
        if m:
            card = get_stop_text(m.groups()[0], m.groups()[1])
            bot.sendMessage(chat_id, card)
        else:
            m = re.match(r".*\b(\d+)", text)
            if m:
                card = get_stop_text("", m.groups()[0])
                bot.sendMessage(chat_id, card)

    print ('Chat Message:', content_type, chat_type, chat_id)


def get_stop_text(city, stop_code):
    normalized = normalize_stopcode(stop_code)
    _, card, actual = hsl.relative_time(city + normalized, 6)
    return "%s %s" % (actual, card)


def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print ('Callback Query:', query_id, from_id, query_data)


def on_inline_query(msg):
    query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
    print ('Inline Query:', query_id, from_id, query_string)

    # Compose your own answers
    articles = [{'type': 'article',
                 'id': 'abc', 'title': 'ABC', 'message_text': 'Good morning'}]

    bot.answerInlineQuery(query_id, articles)


def on_chosen_inline_result(msg):
    result_id, from_id, query_string = telepot.glance(msg,
                                                      flavor='chosen_inline_result')
    print ('Chosen Inline Result:', result_id, from_id, query_string)


bot = telepot.Bot(telegram_api_key)
bot.message_loop({'chat': on_chat_message,
                  'callback_query': on_callback_query,
                  'inline_query': on_inline_query,
                  'chosen_inline_result': on_chosen_inline_result})
hsl = HslRequests(hsl_username, hsl_passcode)
print ('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)
