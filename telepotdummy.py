import sys
import time
import telepot
from keys import telegram_api_key
from departures import city_code, normalize_stopcode, HslRequests


def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == u"location":
        location = msg["location"]
        bot.sendMessage(chat_id, location)
    print ('Chat Message:', content_type, chat_type, chat_id)


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

print ('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)
