import telepot
from keys import telegram_api_key, telegram_bot_url

bot = telepot.Bot(telegram_api_key)
bot.setWebhook(telegram_bot_url)