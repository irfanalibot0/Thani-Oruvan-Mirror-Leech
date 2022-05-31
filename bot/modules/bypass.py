import time
import cloudscraper
import requests
from bs4 import BeautifulSoup

from bot.helper.telegram_helper.message_utils import sendMessage, deleteMessage
from bot import dispatcher
from telegram.ext import CommandHandler
from bot.modules.clone import is_gdrive_link,is_gdtot_link
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands

def rlb(update, context):
    args = update.message.text.split(" ", maxsplit=1)
    reply_to = update.message.reply_to_message
    if len(args) > 1:
        link = args[1]
    elif reply_to is not None:
        link = reply_to.text
    url = link

    if "toonworld4all" in url:
        site = requests.get(url)
        new = site.url
        t_code=new.split("token=", 1)[-1]
        url = "https://rocklinks.net/"+t_code
    else:
        url = url

    if "rocklinks.net" in url:
        msg = sendMessage(f"Processing: <code>{url}</code>", context.bot, update)
        ghi = rocklinks_bypass(url)
        deleteMessage(context.bot, msg)
        sendMessage(f"{ghi}", context.bot, update)
    else:
        deleteMessage(context.bot, msg)
        sendMessage('Send Rocklinks url along with command or by replying to the link by command', context.bot, update)
# ---------------------------------------------------------------------------------------------------------------------

def rocklinks_bypass(url):
    client = cloudscraper.create_scraper(allow_brotli=False)
    DOMAIN = "https://links.spidermods.in"
    url = url[:-1] if url[-1] == '/' else url

    code = url.split("/")[-1]
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
        return r.json()['url']
    except: return "Something went wrong :("

rlb_handler = CommandHandler(BotCommands.RlbCommand, rlb, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(rlb_handler)
