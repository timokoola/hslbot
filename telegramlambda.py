"""Lambda handle function for Telegram bot"""
from __future__ import print_function

import re

import departures
import telepot
from departures import normalize_stopcode
from keys import hsl_username, hsl_passcode, telegram_api_key


def lambda_handler(event, context):
    """Lambda handle function for Telegram bot, calls are
    routed through API gateway"""
    print(event)
    hsl = departures.HslRequests(hsl_username,
                                 hsl_passcode)
    bot = telepot.Bot(telegram_api_key)
    on_chat_message(event["message"], hsl, bot)


def send_help_text(bot):
    """Help text"""
    return "Hello, this bot offers Helsinki area public transportation info.\n" \
           "Send a location to bot to get stops near you.\n" \
           "Send a stop code to see departures\n" \
           "For example try 'V0531' for airport trains to Helsinki\n" \
           "or '0099' for Suomenlinna ferries\n"


def on_chat_message(msg, hsl, bot):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print('Chat Message:', content_type, chat_type, chat_id)
    if content_type == u"location":
        location = msg["location"]
        latitude = location["latitude"]
        longitude = location["longitude"]
        reply, stops = hsl.stops_for_location(latitude, longitude)
        bot.sendMessage(chat_id, reply)
    if content_type == u"text":
        text = msg["text"]
        if text.find("help") != -1:
            bot.sendMessage(chat_id, send_help_text(bot))
            return
        m = re.match(r".*\b(\D+)(\d+)", text)
        if m:
            card = get_stop_text(m.groups()[0], m.groups()[1], hsl)
            bot.sendMessage(chat_id, card)
        else:
            m = re.match(r".*\b(\d+)", text)
            if m:
                card = get_stop_text("", m.groups()[0], hsl)
                bot.sendMessage(chat_id, card)

    print('Chat Message:', content_type, chat_type, chat_id)


def get_stop_text(city, stop_code, hsl):
    normalized = normalize_stopcode(stop_code)
    _, card, actual = hsl.relative_time(city + normalized, 6)
    return "%s %s" % (actual, card)
