import logging
from datetime import datetime

from notion_client import Client
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
import re

TELEGRAM_TOKEN = '7654089116:AAFM-bVqNmy-cL5mJKDow5ORjyLjyQPuDD0'
NOTION_TOKEN = 'ntn_V96402409754We2UgeyXKFPjl2sPvX7UvUos2j3oA4w291'
LINKS_DB_ID = '13e23e9a674f80488b74e2ceb9cba33e'
TEXT_DB_ID = '13e23e9a674f8034adace47afc1fc61c'


notion = Client(auth=NOTION_TOKEN)


def detect_platform(url):
    if 'facebook.com' in url:
        return 'Facebook'
    elif 'tiktok.com' in url:
        return 'TikTok'
    elif 'linkedin.com' in url:
        return 'LinkedIn'
    return 'Unknown'


def save_to_notion(url, platform, event_type):
    if event_type == "link":
        notion.pages.create(
            parent={"database_id": LINKS_DB_ID},
            properties={
                "Platform": {"title": [{"text": {"content": platform}}]},
                "URL": {"url": url},
                "Date Added": {"date": {"start": str(datetime.now().date())}}
            }
        )
    elif event_type == "text":
        notion.pages.create(
            parent={"database_id": TEXT_DB_ID},
            properties={
                "Text": {"title": [{"text": {"content": url}}]},
                "Date Added": {"date": {"start": str(datetime.now().date())}}
            }
        )



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message_text = update.message.text
    print(">>>>>> message received: ", message_text)
    urls = re.findall(r'(https?://\S+)', message_text)
    if not urls or len(urls) == 0:
        save_to_notion(message_text, None, "text")
        await update.message.reply_text("saved text to Notion")
    else:
        for url in urls:
            platform = detect_platform(url)
            save_to_notion(url, platform, "link")
            await update.message.reply_text(f"Saved link to Notion: {url}")


if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler)

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    # application.add_handler(echo_handler)
    application.add_handler(message_handler)
    application.run_polling()