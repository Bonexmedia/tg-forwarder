# forwarder.py - Advanced Cleaner + Replacer
from telethon import TelegramClient, events
import os
import re

# Your settings (from Render environment variables)
API_ID       = int(os.getenv('38218054'))
API_HASH     = os.getenv('15f4186fa3b18bdc191ba9f4f5cfd7a1')
PHONE        = os.getenv('+2349016571580')
SOURCE       = os.getenv('@cryptoinsidebets')
TARGET       = os.getenv('@cryptoinsderpump')

# ←←←←←←←←←←←←←←←←←  EDIT THESE 3 LINES BELOW  ←←←←←←←←←←←←←←←←←
REPLACE_USERNAME = "@Cryptoinsiderbets"           # ← What every @username becomes
REMOVE_TELEGRAM_LINKS = True              # ← Set to False if you ever want to allow t.me links

# Keywords to replace (case-insensitive)
# Format: "old word" : "new word or ***"
KEYWORDS_TO_REPLACE = {
    "shit": "****",
    "fuck": "****",
    "scam": "opportunity",
    "free money": "hard work",
    # add as many as you want ↓
    # "oldname": "NewBrand",
}
# ============================================================

client = TelegramClient('sess', API_ID, API_HASH)

# Regex patterns
TG_LINKS = re.compile(r'(https?://)?(t\.me|telegram\.me|telegram\.dog)/[^\s]+', re.IGNORECASE)
USERNAME_MENTION = re.compile(r'@\w+')

def clean_text(text: str) -> str:
    if not text:
        return text

    # 1. Replace keywords
    for bad, good in KEYWORDS_TO_REPLACE.items():
        text = re.sub(re.escape(bad), good, text, flags=re.IGNORECASE)

    # 2. Remove ALL Telegram links
    if REMOVE_TELEGRAM_LINKS:
        text = TG_LINKS.sub('', text)

    # 3. Replace every @username with your chosen one
    text = USERNAME_MENTION.sub(REPLACE_USERNAME, text)

    return text.strip()

@client.on(events.NewMessage(chats=SOURCE))
async def handler(event):
    try:
        msg = event.message

        # If the message was already forwarded from somewhere else → keep original forward tag
        if msg.fwd_from:
            await client.forward_messages(TARGET, msg)
            print(f"Forwarded (kept original tag) → {msg.id}")
            return

        # Normal message → clean andily copy with our rules
        cleaned_text = clean_text(msg.message) if msg.message else None

        # Download media if present
        file = await msg.download_media() if msg.media else None

        await client.send_message(
            entity=TARGET,
            message=cleaned_text,
            file=file,
            formatting_entities=msg.entities,   # keeps bold, italic, links (except t.me)
            silent=True
        )
        print(f"Cleaned & posted → {msg.id}")

    except Exception as e:
        print(f"Error: {e}")

print("Advanced Forwarder starting...")
client.start(phone=PHONE)
print(f"Watching {SOURCE} → {TARGET}")
print(f"• All @username → {REPLACE_USERNAME}")
print(f"• Telegram links removed: {REMOVE_TELEGRAM_LINKS}")
client.run_until_disconnected()
