from somewhere import API_KEY, TG_API_ID, TG_API_HASH

from telethon import TelegramClient, events

bot = TelegramClient('bot', TG_API_ID, TG_API_HASH)
bot.start(bot_token=API_KEY)


@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    """Send a message when the command /start is issued."""
    await event.respond('Hi!')
    raise events.StopPropagation


@bot.on(events.NewMessage)
async def echo(event):
    """Echo the user message."""
    await event.respond(event.text)


def main():
    """Start the bot."""
    bot.run_until_disconnected()


if __name__ == '__main__':
    main()
