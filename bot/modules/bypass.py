import time
import cloudscraper
import requests
from bs4 import BeautifulSoup

from bot.helper.telegram_helper.message_utils import sendMessage, deleteMessage
from bot import dispatcher
from telegram.ext import CommandHandler
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException

def rlb(update, context):
    args = update.message.text.split(" ", maxsplit=1)
    reply_to = update.message.reply_to_message
    if len(args) > 1:
        link = args[1]
    elif reply_to is not None:
        link = reply_to.text
    if "toonworld4all" in link:
        site = requests.get(link)
        new = site.link
        t_code=new.split("token=", 1)[-1]
        link = "https://rocklinks.net/"+t_code
    else:
        link
    try:
        msg = sendMessage(f"Processing: <code>{link}</code>", context.bot, update)
        link = rocklinks_bypass(link)
        deleteMessage(context.bot, msg)
    except DirectDownloadLinkException as e:
        deleteMessage(context.bot, msg)
        return sendMessage(str(e), context.bot, update)
# ---------------------------------------------------------------------------------------------------------------------

def rocklinks_bypass(link):
    client = cloudscraper.create_scraper(allow_brotli=False)
    DOMAIN = "https://links.spidermods.in"
    link = link[:-1] if link[-1] == '/' else link

    code = link.split("/")[-1]
    final_url = f"{DOMAIN}/{code}?quelle="

    resp = client.get(final_url)
    
    soup = BeautifulSoup(resp.content, "html.parser")
    try:
        inputs = soup.find(id="go-link").find_all(name="input")
    except:
        return "Incorrect Link"
    data = { input.get('name'): input.get('value') for input in inputs }

    h = { "x-requested-with": "XMLHttpRequest" }
    
    time.sleep(6)
    r = client.post(f"{DOMAIN}/links/go", data=data, headers=h)
    try:
        return r.json()['link']
    except: return "Something went wrong :("

rlb_handler = CommandHandler(BotCommands.RlbCommand, rlb, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(rlb_handler)
